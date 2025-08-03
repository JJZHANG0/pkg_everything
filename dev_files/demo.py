#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ros_robot_controller_msgs.msg import SetPWMServoState, PWMServoState, ButtonState
from sensor_msgs.msg import Image
import requests
import time
import threading
import numpy as np
import cv2
from cv_bridge import CvBridge

SERVER_URL = 'http://192.168.110.148:8000/api'
ROBOT_ID = 1
USERNAME = 'root'
PASSWORD = 'test123456'
SERVO_ID = 3
OPEN_POS = 2200
CLOSE_POS = 1000
DOOR_STATE_UNKNOWN = 0
DOOR_STATE_OPEN = 1
DOOR_STATE_CLOSED = 2

class BotNode(Node):
    def __init__(self):
        super().__init__('multi_cmd_bot')
        self.token = None
        self.servo_pub = self.create_publisher(SetPWMServoState, '/ros_robot_controller/pwm_servo/set_state', 10)
        self.door_state = DOOR_STATE_CLOSED
        self.last_nav_cmd_id = None
        self._nav_sim_thread = None
        self._nav_sim_stop = threading.Event()
        self.bridge = CvBridge()
        self._qr_image = None
        self._qr_event = threading.Event()

        # Subscribe to physical button status
        self.create_subscription(ButtonState, '/ros_robot_controller/button', self.button_callback, 10)
        self.get_logger().info("Subscribed to /ros_robot_controller/button")

        self.get_logger().info("Node starting: actively closing the door.")
        self.set_door_state(False)
        self.get_logger().info("Door is initialized as CLOSED at startup.")

        self.get_logger().info("✅ multi_cmd_bot started")
        self.create_timer(3.0, self.poll_server_commands)

    def set_door_state(self, open_):
        self.get_logger().info(f"set_door_state called: {'Open' if open_ else 'Close'}")
        msg = SetPWMServoState()
        state = PWMServoState()
        state.id = [SERVO_ID]
        state.position = [OPEN_POS if open_ else CLOSE_POS]
        state.offset = [0]
        msg.state.append(state)
        self.servo_pub.publish(msg)
        self.get_logger().info(f"{'Open' if open_ else 'Close'} door servo command published.")

    def poll_server_commands(self):
        self.get_logger().info("Polling server for new command...")
        if not self.ensure_token():
            self.get_logger().warn("No valid token, skipping poll.")
            return
        cmd = self.get_pending_command()
        if not cmd:
            self.get_logger().info("No pending command from server.")
            return

        ctype = cmd['command']
        cid = cmd['command_id']
        cparam = cmd.get('param')
        self.get_logger().info(f"Received command from server: {ctype}, id: {cid}, param: {cparam}")
        if ctype == 'open_door':
            self.handle_open_close_door(cid, True)
        elif ctype == 'close_door':
            self.handle_open_close_door(cid, False)
        elif ctype == 'upload_qr':
            self.handle_upload_qr(cid)
        elif ctype == 'navigate':
            self.handle_navigation(cid, cparam)
        elif ctype == 'emergency_button':
            self.handle_emergency_button(cid)
        else:
            self.get_logger().info(f"Unknown command received: {ctype}")

    def handle_open_close_door(self, cid, want_open):
        action = "open" if want_open else "close"
        self.get_logger().info(f"Handling {action} door command. (current state: {self.door_state})")
        if want_open:
            if self.door_state == DOOR_STATE_OPEN:
                self.get_logger().info("Door already open, skipping operation.")
                self.report_door_status(cid, "open")
                return
            self.set_door_state(True)
            self.door_state = DOOR_STATE_OPEN
            self.report_door_status(cid, "open")
        else:
            if self.door_state == DOOR_STATE_CLOSED:
                self.get_logger().info("Door already closed, skipping operation.")
                self.report_door_status(cid, "closed")
                return
            self.set_door_state(False)
            self.door_state = DOOR_STATE_CLOSED
            self.report_door_status(cid, "closed")

    def report_door_status(self, command_id, state):
        self.get_logger().info(f"Reporting door status to server: {state}, command_id: {command_id}")
        try:
            resp = requests.post(
                f"{SERVER_URL}/robots/{ROBOT_ID}/execute_command/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"command_id": command_id, "result": f"door_{state}"},
                timeout=5
            )
            self.get_logger().info(f"Door status report server response: {resp.status_code} {resp.text}")
        except Exception as e:
            self.get_logger().error(f"Failed to report door status: {e}")

    def handle_upload_qr(self, cid):
        self.get_logger().info("Received upload QR image command. Subscribing to camera...")
        self._qr_event.clear()
        self._qr_image = None
        sub = self.create_subscription(Image, '/ascamera/camera_publisher/rgb0/image', self._on_qr_image, 10)
        got = self._qr_event.wait(3.0)
        self.destroy_subscription(sub)
        if not got or self._qr_image is None:
            self.get_logger().error("Failed to capture image in time.")
            self.report_command(cid, "qr_upload_fail")
            return
        self.get_logger().info("Image captured, encoding and uploading to server...")
        try:
            img_cv = self.bridge.imgmsg_to_cv2(self._qr_image, desired_encoding="bgr8")
            ret, buf = cv2.imencode('.jpg', img_cv)
            if not ret:
                raise Exception("cv2.imencode failed")
            resp = requests.post(
                f"{SERVER_URL}/robots/{ROBOT_ID}/upload_qr/",
                headers={"Authorization": f"Bearer {self.token}"},
                files={"qr_image": ("qr.jpg", buf.tobytes())},
                timeout=5
            )
            msg = "success" if resp.status_code == 200 else "fail"
            self.report_command(cid, f"qr_upload_{msg}")
            self.get_logger().info(f"QR image upload result: {msg}. Server response: {resp.status_code} {resp.text}")
        except Exception as e:
            self.get_logger().error(f"Failed to upload QR image: {e}")
            self.report_command(cid, "qr_upload_fail")

    def _on_qr_image(self, msg):
        if not self._qr_event.is_set():
            self._qr_image = msg
            self._qr_event.set()

    def handle_navigation(self, cid, param):
        if not param:
            self.get_logger().warn("Navigation command missing parameters, ignored.")
            return
        if self._nav_sim_thread and self._nav_sim_thread.is_alive():
            self.get_logger().warn("A navigation task is already running, ignoring new one.")
            return
        target = param.get('target') if isinstance(param, dict) else param
        self.last_nav_cmd_id = cid
        self._nav_sim_stop.clear()
        self._nav_sim_thread = threading.Thread(target=self._simulate_navigation, args=(cid, target))
        self._nav_sim_thread.start()

    def _simulate_navigation(self, command_id, target):
        current = [0.0, 0.0]
        target_coord = np.array(
            [target.get('x', 0), target.get('y', 0)], dtype=np.float32
        ) if isinstance(target, dict) else np.array(target if isinstance(target, (list, tuple)) else [0, 0], dtype=np.float32)
        start = np.array(current, dtype=np.float32)
        steps = 4
        path = [list(start + (i / steps) * (target_coord - start)) for i in range(steps)]
        path.append(list(target_coord))
        for i, coord in enumerate(path):
            nav_state = "delivering" if i < steps else "arrived"
            try:
                resp = requests.post(
                    f"{SERVER_URL}/robots/{ROBOT_ID}/navigation_status/",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json={"command_id": command_id, "coord": {'x': coord[0], 'y': coord[1]}, "status": nav_state},
                    timeout=5
                )
                self.get_logger().info(f"Navigation status reported: {resp.status_code} {resp.text}")
            except Exception as e:
                self.get_logger().error(f"Failed to report navigation status: {e}")
            if nav_state == "arrived":
                break
            for _ in range(30):
                if self._nav_sim_stop.is_set():
                    return
                time.sleep(0.1)

    def handle_emergency_button(self, cid):
        self.get_logger().warn("Handling emergency button command!")
        try:
            resp = requests.post(
                f"{SERVER_URL}/robots/{ROBOT_ID}/emergency_button/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            if resp.status_code == 200:
                self.get_logger().info("Emergency button triggered successfully.")
                self.report_command(cid, "emergency_success")
            else:
                self.get_logger().error(f"Emergency request failed: {resp.status_code} {resp.text}")
                self.report_command(cid, "emergency_fail")
        except Exception as e:
            self.get_logger().error(f"Exception during emergency button request: {e}")
            self.report_command(cid, "emergency_fail")

    def button_callback(self, msg):
        if msg.id == 1:
            self.process_button_press('Button 1', msg.state)
        elif msg.id == 2:
            self.process_button_press('Button 2', msg.state)

    def process_button_press(self, button_name, state):
        if state == 1:
            self.get_logger().info(f"{button_name} short press detected")
            self.handle_emergency_button(cid=0)
        elif state == 2:
            self.get_logger().info(f"{button_name} long press detected")

    def report_command(self, command_id, result):
        try:
            resp = requests.post(
                f"{SERVER_URL}/robots/{ROBOT_ID}/execute_command/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"command_id": command_id, "result": result},
                timeout=5
            )
            self.get_logger().info(f"Command report server response: {resp.status_code} {resp.text}")
        except Exception as e:
            self.get_logger().error(f"Failed to report command: {e}")

    def ensure_token(self):
        if self.token is not None:
            return True
        try:
            resp = requests.post(f"{SERVER_URL}/token/", json={"username": USERNAME, "password": PASSWORD}, timeout=5)
            if resp.status_code == 200:
                self.token = resp.json().get('access')
                return True
            else:
                self.get_logger().error(f"Token request failed: {resp.text}")
        except Exception as e:
            self.get_logger().error(f"Login failed: {e}")
        return False

    def get_pending_command(self):
        try:
            resp = requests.get(
                f"{SERVER_URL}/robots/{ROBOT_ID}/get_commands/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            if resp.status_code == 200:
                cmds = resp.json().get('pending_commands', [])
                return cmds[0] if cmds else None
        except Exception as e:
            self.get_logger().error(f"Failed to get command: {e}")
        return None

def main(args=None):
    rclpy.init(args=args)
    node = BotNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
