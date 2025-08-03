#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ros_robot_controller_msgs.msg import SetPWMServoState, PWMServoState
from sensor_msgs.msg import Image
import requests
import time
import threading
import numpy as np
import cv2
from cv_bridge import CvBridge
import asyncio
import websockets
import json
from urllib.parse import urlencode

SERVER_URL = 'http://192.168.110.148:8000/api'
ROBOT_ID = 1
USERNAME = 'root'
PASSWORD = 'test123456'
SERVO_ID = 3
OPEN_POS = 2200
CLOSE_POS = 800
DOOR_STATE_UNKNOWN = 0
DOOR_STATE_OPEN = 1
DOOR_STATE_CLOSED = 2

class BotNode(Node):
    def __init__(self):
        super().__init__('multi_cmd_bot')

        self.token = None
        self.loop = asyncio.get_event_loop()
        self.bridge = CvBridge()
        self._qr_event = threading.Event()
        self._qr_image = None
        self._nav_sim_thread = None
        self._nav_sim_stop = threading.Event()
        self.last_nav_cmd_id = None
        self.websocket = None
        self.connected = False

        self.servo_pub = self.create_publisher(SetPWMServoState, '/ros_robot_controller/pwm_servo/set', 10)

        # Initialize: force servo to close the door, and set state to CLOSED
        self.set_door_state(False) 
        self.door_state = DOOR_STATE_CLOSED
        self.get_logger().info("Initialization done. Door is set to CLOSED (door_state = CLOSED)")

        # Start WebSocket listener as asyncio task
        self.loop.create_task(self.websocket_listener())

    # ==== WebSocket listening and dispatch ====
    async def websocket_listener(self):
        while True:
            try:
                # 获取token
                token = self.ensure_token_and_get()
                if not token:
                    self.get_logger().error("Failed to get Token, retry after 5 seconds...")
                    await asyncio.sleep(5)
                    continue
                
                # 构建WebSocket URL（将token作为查询参数，兼容旧版本websockets）
                params = urlencode({
                    'token': token,
                    'robot_id': ROBOT_ID
                })
                ws_url = f"ws://192.168.110.148:8000/ws/robot/{ROBOT_ID}/?{params}"
                
                self.get_logger().info(f"Connecting to WebSocket: {ws_url}")
                
                # 连接WebSocket（不使用extra_headers，兼容旧版本）
                self.websocket = await websockets.connect(ws_url)
                self.connected = True
                
                self.get_logger().info("WebSocket connected, waiting for commands...")
                
                # 发送初始状态
                await self.send_status_update({
                    'status': 'IDLE',
                    'battery': 85,
                    'door_status': 'CLOSED',
                    'location': {'x': 0, 'y': 0}
                })
                
                # 开始接收消息
                async for message in self.websocket:
                    self.get_logger().info(f"Received WS command: {message}")
                    try:
                        cmd = json.loads(message)
                        await self.handle_ws_command(cmd)
                    except Exception as e:
                        self.get_logger().error(f"Failed to parse WS command: {e}")
                        
            except websockets.exceptions.ConnectionClosed:
                self.get_logger().info("WebSocket connection closed")
                self.connected = False
            except Exception as e:
                self.get_logger().error(f"WebSocket connection failed: {e}, retry after 5 seconds")
                self.connected = False
                await asyncio.sleep(5)

    def ensure_token_and_get(self):
        if self.token:
            return self.token
        try:
            resp = requests.post(f"{SERVER_URL}/token/", json={
                "username": USERNAME, "password": PASSWORD
            }, timeout=5)
            if resp.status_code == 200:
                self.token = resp.json().get('access')
                self.get_logger().info("Token obtained successfully")
                return self.token
            else:
                self.get_logger().error(f"Token request failed: {resp.text}")
        except Exception as e:
            self.get_logger().error(f"Login exception: {e}")
        return ""

    async def handle_ws_command(self, cmd):
        ctype = cmd.get('command')
        cid = cmd.get('command_id')
        cparam = cmd.get('param')
        self.get_logger().info(f"WS Command: {ctype}, id={cid}, param={cparam}")
        
        if ctype == 'open_door':
            await self.handle_open_close_door(cid, True)
        elif ctype == 'close_door':
            await self.handle_open_close_door(cid, False)
        elif ctype == 'upload_qr':
            await self.handle_upload_qr(cid)
        elif ctype == 'navigate':
            await self.handle_navigation(cid, cparam)
        elif ctype == 'emergency_open_door':
            await self.handle_emergency_open_door(cid)
        else:
            self.get_logger().info(f"Unknown command: {ctype}")

    async def send_status_update(self, status_data):
        """发送状态更新到WebSocket"""
        if not self.connected or not self.websocket:
            return
        
        message = {
            'type': 'status_update',
            **status_data
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            self.get_logger().info("Status update sent via WebSocket")
        except Exception as e:
            self.get_logger().error(f"Failed to send status update: {e}")

    async def send_command_result(self, command_id, result):
        """发送指令执行结果到WebSocket"""
        if not self.connected or not self.websocket:
            # 如果WebSocket未连接，回退到HTTP
            self.report_command(command_id, result)
            return
        
        message = {
            'type': 'command_result',
            'command_id': command_id,
            'result': result
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            self.get_logger().info(f"Command result sent via WebSocket: {result}")
        except Exception as e:
            self.get_logger().error(f"Failed to send command result: {e}")
            # 回退到HTTP
            self.report_command(command_id, result)

    # ========== Door control ==========
    async def handle_open_close_door(self, cid, want_open):
        action = "open" if want_open else "close"
        self.get_logger().info(f"Handling {action} door command. (current state: {self.door_state})")
        
        if want_open:
            if self.door_state == DOOR_STATE_OPEN:
                self.get_logger().info("Door already open, skipping operation.")
                await self.send_command_result(cid, "door_open")
                return
            self.get_logger().info("Publishing open door command.")
            self.set_door_state(True)
            self.door_state = DOOR_STATE_OPEN   # Directly update state
            await self.send_command_result(cid, "door_open")
        else:
            if self.door_state == DOOR_STATE_CLOSED:
                self.get_logger().info("Door already closed, skipping operation.")
                await self.send_command_result(cid, "door_closed")
                return
            self.get_logger().info("Publishing close door command.")
            self.set_door_state(False)
            self.door_state = DOOR_STATE_CLOSED # Directly update state
            await self.send_command_result(cid, "door_closed")

    async def handle_emergency_open_door(self, cid):
        """处理紧急开门指令"""
        self.get_logger().info("Emergency door open command received!")
        
        # 强制开门
        self.set_door_state(True)
        self.door_state = DOOR_STATE_OPEN
        
        # 发送结果
        await self.send_command_result(cid, "door_open")
        
        # 更新状态
        await self.send_status_update({
            'status': 'EMERGENCY',
            'door_status': 'OPEN',
            'battery': 85,
            'location': {'x': 0, 'y': 0}
        })

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

    # ========== Upload QR image ==========
    async def handle_upload_qr(self, cid):
        self.get_logger().info("Received upload QR image command. Subscribing to camera...")
        self._qr_event.clear()
        self._qr_image = None

        sub = self.create_subscription(
            Image,
            '/ascamera/camera_publisher/rgb0/image',
            self._on_qr_image,
            10)
        got = self._qr_event.wait(3.0)
        self.destroy_subscription(sub)
        if not got or self._qr_image is None:
            self.get_logger().error("Failed to capture image in time.")
            await self.send_command_result(cid, "qr_upload_fail")
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
            ok = resp.status_code == 200
            msg = "success" if ok else "fail"
            await self.send_command_result(cid, f"qr_upload_{msg}")
            self.get_logger().info(f"QR image upload result: {msg}. Server response: {resp.status_code} {resp.text}")
        except Exception as e:
            self.get_logger().error(f"Failed to upload QR image: {e}")
            await self.send_command_result(cid, "qr_upload_fail")

    def _on_qr_image(self, msg):
        self.get_logger().info("QR image callback triggered.")
        if not self._qr_event.is_set():
            self._qr_image = msg
            self._qr_event.set()

    # ========== Navigation simulation ==========
    async def handle_navigation(self, cid, param):
        self.get_logger().info(f"Received navigation command: {param}")
        if not param:
            self.get_logger().warn("Navigation command missing parameters, ignored.")
            return
        if self._nav_sim_thread and self._nav_sim_thread.is_alive():
            self.get_logger().warn("A navigation task is already running, ignoring new one.")
            return
        target = param.get('target') if isinstance(param, dict) else param
        self.get_logger().info(f"Start navigation simulation, target coordinates: {target}")
        self.last_nav_cmd_id = cid
        self._nav_sim_stop.clear()
        self._nav_sim_thread = threading.Thread(target=self._simulate_navigation, args=(cid, target))
        self._nav_sim_thread.start()

    def _simulate_navigation(self, command_id, target):
        current = [0.0, 0.0]
        if isinstance(target, dict):
            target_coord = np.array([target.get('x', 0), target.get('y', 0)], dtype=np.float32)
        elif isinstance(target, (list, tuple)) and len(target) == 2:
            target_coord = np.array(target, dtype=np.float32)
        else:
            target_coord = np.array([0, 0], dtype=np.float32)
        start = np.array(current, dtype=np.float32)
        steps = 4
        path = [list(start + (i / steps) * (target_coord - start)) for i in range(steps)]
        path.append(list(target_coord))
        for i, coord in enumerate(path):
            nav_state = "delivering" if i < steps else "arrived"
            self.get_logger().info(f"Reporting navigation: coord={coord}, state={nav_state}")
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
                self.get_logger().info("Navigation simulation arrived at target.")
                break
            for _ in range(30):
                if self._nav_sim_stop.is_set():
                    self.get_logger().info("Navigation simulation stopped early.")
                    return
                time.sleep(0.1)

    # ========== General command report ==========
    def report_command(self, command_id, result):
        self.get_logger().info(f"Reporting command execution result to server: {result}")
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

def main(args=None):
    rclpy.init(args=args)
    node = BotNode()
    try:
        node.loop.run_forever()
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 