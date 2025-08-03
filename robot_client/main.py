#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
import signal
from config import Config
from utils.logger import RobotLogger
from hardware.gpio_controller import GPIOController
from hardware.camera_scanner import CameraScanner
from network.api_client import APIClient

class RobotClient:
    """快递车客户端主程序"""
    
    def __init__(self):
        # 初始化日志
        self.logger = RobotLogger()
        self.logger.info("🤖 启动 CulverBot 快递车客户端 (Mac模拟版)")
        
        # 初始化组件
        self.gpio = GPIOController(self.logger)
        self.camera = CameraScanner(self.logger)
        self.api = APIClient(self.logger)
        
        # 状态管理
        self.current_status = 'IDLE'
        self.current_orders = []
        self.is_running = False
        self.poll_thread = None
        
        # 注册回调函数
        self.register_callbacks()
        
        # 信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def register_callbacks(self):
        """注册回调函数"""
        self.gpio.register_callback('loading_button', self.on_loading_button)
        self.gpio.register_callback('delivery_button', self.on_delivery_button)
        self.gpio.register_callback('emergency_stop', self.on_emergency_stop)

        self.camera.register_callback('qr_scanned', self.on_qr_scanned)
        self.camera.register_callback('scan_timeout', self.on_scan_timeout)  # 新增：扫描超时回调
    
    def start(self):
        """启动客户端"""
        try:
            self.is_running = True
            self.logger.info("🚀 启动快递车客户端...")
            
            # 测试服务器连接
            if not self.api.test_connection():
                self.logger.warning("⚠️ 无法连接到服务器，将以演示模式运行")
                self.logger.info("📱 演示模式说明:")
                self.logger.info("   - 可以测试所有模拟功能")
                self.logger.info("   - 可以测试二维码扫描")
                self.logger.info("   - 服务器连接功能将被跳过")
            else:
                # 开始轮询服务器
                self.start_polling()
            
            # 不再自动开始二维码扫描，改为按钮触发模式
            self.logger.info("📱 二维码扫描已设置为按钮触发模式")
            
            # 设置初始状态
            self.set_status('IDLE')
            
            self.logger.info("✅ 快递车客户端启动成功")
            self.logger.info("📱 模拟操作说明:")
            self.logger.info("   - 输入 'loading' 模拟装货按钮")
            self.logger.info("   - 输入 'delivery' 模拟开始配送按钮")
            self.logger.info("   - 输入 'emergency' 模拟紧急停止")

            self.logger.info("   - 输入 'door_open' 模拟开门")
            self.logger.info("   - 输入 'door_close' 模拟关门")
            self.logger.info("   - 输入 'test_qr' 模拟二维码扫描")
            self.logger.info("   - 输入 'quit' 退出程序")
            
            # 启动交互线程
            self.start_interactive_mode()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 启动失败: {e}")
            return False
    
    def start_polling(self):
        """开始轮询服务器"""
        self.poll_thread = threading.Thread(target=self.poll_server)
        self.poll_thread.daemon = True
        self.poll_thread.start()
        self.logger.info(f"📡 开始轮询服务器，间隔: {Config.POLL_INTERVAL}秒")
    
    def poll_server(self):
        """轮询服务器"""
        while self.is_running:
            try:
                # 获取当前订单
                data = self.api.get_current_orders()
                if data:
                    self.handle_server_data(data)
                
                # 获取并执行待处理的指令
                commands = self.api.get_commands()
                if commands:
                    self.handle_commands(commands)
                
                time.sleep(Config.POLL_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"轮询失败: {e}")
                time.sleep(Config.RETRY_DELAY)
    
    def handle_server_data(self, data):
        """处理服务器数据"""
        try:
            # 检查状态变化
            if data.get('status') != self.current_status:
                old_status = self.current_status
                self.current_status = data.get('status', 'IDLE')
                self.logger.info(f"🔄 状态变化: {old_status} → {self.current_status}")
                self.set_status(self.current_status)
            
            # 更新订单信息
            orders = data.get('current_orders', [])
            if orders != self.current_orders:
                self.current_orders = orders
                self.logger.info(f"📦 订单更新，数量: {len(orders)}")
                
                # 显示订单信息
                for order in orders:
                    self.logger.info(f"  订单{order.get('order_id')}: {order.get('student', {}).get('name', 'Unknown')} - {order.get('status', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"处理服务器数据失败: {e}")
    
    def handle_commands(self, commands):
        """处理待执行的指令"""
        try:
            for command in commands:
                command_id = command.get('command_id')
                command_type = command.get('command')
                command_display = command.get('command_display', command_type)
                
                self.logger.info(f"🤖 收到指令: {command_display}")
                
                # 执行指令
                result = self.execute_command(command_type, command_id)
                
                # 报告执行结果
                if result:
                    self.logger.info(f"✅ 指令执行成功: {command_display}")
                else:
                    self.logger.error(f"❌ 指令执行失败: {command_display}")
                    
        except Exception as e:
            self.logger.error(f"处理指令失败: {e}")
    
    def execute_command(self, command_type, command_id):
        """执行具体指令"""
        try:
            result = "执行成功"
            
            if command_type == 'open_door':
                self.logger.info("🚪 执行开门指令...")
                self.gpio.simulate_door_open()
                time.sleep(2)  # 模拟开门时间
                result = "门已打开"
                
            elif command_type == 'close_door':
                self.logger.info("🚪 执行关门指令...")
                self.gpio.simulate_door_close()
                time.sleep(2)  # 模拟关门时间
                result = "门已关闭"
                
            elif command_type == 'start_delivery':
                self.logger.info("🚀 执行开始配送指令...")
                # 这里可以添加实际的配送逻辑
                result = "开始配送成功"
                
            elif command_type == 'stop_robot':
                self.logger.info("⏹️ 执行停止机器人指令...")
                self.is_running = False
                result = "机器人已停止"
                
            elif command_type == 'emergency_open_door':
                self.logger.info("🚨 执行紧急开门指令...")
                self.gpio.simulate_door_open()
                time.sleep(1)  # 紧急开门更快
                result = "紧急开门完成"
                
            else:
                self.logger.warning(f"❓ 未知指令类型: {command_type}")
                result = "未知指令"
            
            # 报告执行结果给服务器
            success = self.api.execute_command(command_id, result)
            return success
            
        except Exception as e:
            self.logger.error(f"执行指令异常: {e}")
            # 报告执行失败
            self.api.execute_command(command_id, f"执行失败: {str(e)}")
            return False
    
    def set_status(self, status):
        """设置机器人状态"""
        self.current_status = status
        
        # 设置LED状态
        if status == 'IDLE':
            self.gpio.set_led_status(True)
            self.gpio.set_loading_led(False)
            self.gpio.set_delivering_led(False)
        elif status == 'LOADING':
            self.gpio.set_led_status(True)
            self.gpio.set_loading_led(True)
            self.gpio.set_delivering_led(False)
        elif status == 'DELIVERING':
            self.gpio.set_led_status(True)
            self.gpio.set_loading_led(False)
            self.gpio.set_delivering_led(True)
        
        self.logger.info(f"🤖 机器人状态: {Config.STATUS.get(status, status)}")
    
    def on_loading_button(self):
        """装货按钮回调"""
        self.logger.info("📦 装货按钮被按下")
        
        if self.current_status == 'LOADING':
            # 模拟装货过程
            self.logger.info("📦 开始装货流程...")
            self.gpio.beep(0.3)
            
            # 这里可以添加实际的装货逻辑
            # 比如更新订单状态等
            
        else:
            self.logger.warning("⚠️ 当前状态不允许装货操作")
            self.gpio.beep_pattern([0.1, 0.1, 0.1])
    
    def on_delivery_button(self):
        """开始配送按钮回调"""
        self.logger.info("🚚 开始配送按钮被按下")
        
        if self.current_status == 'LOADING' and self.current_orders:
            # 开始配送
            self.logger.info("🚚 开始配送流程...")
            self.gpio.beep(0.5)
            
            # 通知服务器开始配送
            result = self.api.start_delivery()
            if result:
                self.logger.info("✅ 配送模式启动成功")
                self.gpio.simulate_door_close()
                
                # 开始自主配送
                self.start_autonomous_delivery()
            else:
                self.logger.error("❌ 启动配送失败")
        else:
            self.logger.warning("⚠️ 当前状态不允许开始配送")
            self.gpio.beep_pattern([0.1, 0.1, 0.1])
    
    def on_emergency_stop(self):
        """紧急停止回调"""
        self.logger.warning("🚨 紧急停止被触发！")
        self.gpio.beep_pattern([0.5, 0.2, 0.5, 0.2, 0.5])
        
        # 停止所有操作
        self.stop()
    

    
    def on_qr_scanned(self, qr_data):
        """二维码扫描回调"""
        self.logger.info(f"📱 扫描到二维码: {qr_data}")
        
        # 验证二维码
        if isinstance(qr_data, dict) and 'order_id' in qr_data:
            order_id = qr_data['order_id']
            self.logger.info(f"✅ 验证二维码成功，订单ID: {order_id}")
            
            # 蜂鸣器提示扫描成功
            self.gpio.beep_pattern([0.1, 0.1, 0.1])
            
            # 模拟订单取出
            self.simulate_order_pickup(order_id)
        else:
            self.logger.warning("❌ 二维码格式无效")
            # 蜂鸣器提示扫描失败
            self.gpio.beep_pattern([0.5, 0.2, 0.5])
    
    def on_scan_timeout(self, reason="扫描超时"):
        """扫描超时回调"""
        self.logger.warning(f"⚠️ 二维码扫描超时！原因: {reason}")
        
        # 蜂鸣器提示超时
        self.gpio.beep_pattern([0.5, 0.2, 0.5, 0.2, 0.5])
        self.logger.info("📱 请再次按下QR扫描按钮进行扫描。")
    
    def simulate_order_pickup(self, order_id):
        """模拟订单取出"""
        self.logger.info(f"📦 模拟订单{order_id}取出流程...")
        
        # 模拟开门
        self.gpio.simulate_door_open()
        time.sleep(2)
        
        # 模拟等待用户取货
        self.logger.info("⏳ 等待用户取货...")
        time.sleep(3)
        
        # 模拟关门
        self.gpio.simulate_door_close()
        
        # 更新订单状态
        result = self.api.update_order_status(order_id, 'DELIVERED')
        if result:
            self.logger.info(f"✅ 订单{order_id}配送完成")
            self.gpio.beep(0.3)
        else:
            self.logger.error(f"❌ 更新订单{order_id}状态失败")
    
    def start_autonomous_delivery(self):
        """开始自主配送"""
        self.logger.info("🤖 启动自主配送模式")
        
        # 模拟配送路线
        delivery_thread = threading.Thread(target=self.simulate_delivery_route)
        delivery_thread.daemon = True
        delivery_thread.start()
    
    def simulate_delivery_route(self):
        """模拟配送路线"""
        if not self.current_orders:
            return
        
        self.logger.info("🗺️ 开始模拟配送路线...")
        
        for i, order in enumerate(self.current_orders):
            order_id = order.get('order_id')
            student_name = order.get('student', {}).get('name', 'Unknown')
            delivery_location = order.get('delivery_location', {}).get('building', 'Unknown')
            
            self.logger.info(f"📍 前往第{i+1}个配送点: {delivery_location}")
            self.logger.info(f"📦 配送订单{order_id}给{student_name}")
            
            # 模拟行驶时间
            time.sleep(5)
            
            # 到达配送点
            self.logger.info(f"🎯 到达配送点: {delivery_location}")
            self.gpio.beep(0.2)
            
            # 等待二维码扫描
            self.logger.info("📱 等待用户扫描二维码...")
            time.sleep(10)
    
    def start_interactive_mode(self):
        """启动交互模式"""
        while self.is_running:
            try:
                command = input("\n请输入命令: ").strip().lower()
                
                if command == 'quit':
                    self.logger.info("👋 用户请求退出")
                    break
                elif command == 'loading':
                    self.gpio.simulate_button_press('loading')
                elif command == 'delivery':
                    self.gpio.simulate_button_press('delivery')
                elif command == 'emergency':
                    self.gpio.simulate_button_press('emergency')

                elif command == 'door_open':
                    self.gpio.simulate_door_open()
                elif command == 'door_close':
                    self.gpio.simulate_door_close()
                elif command == 'status':
                    self.logger.info(f"当前状态: {self.current_status}")
                    self.logger.info(f"订单数量: {len(self.current_orders)}")
                elif command == 'orders':
                    for order in self.current_orders:
                        self.logger.info(f"订单{order.get('order_id')}: {order.get('student', {}).get('name', 'Unknown')}")
                elif command == 'help':
                    self.show_help()
                elif command == 'test_qr':
                    self.logger.info("🔍 模拟二维码扫描...")
                    self.gpio.simulate_qr_scan()
                else:
                    self.logger.warning("未知命令，输入 'help' 查看帮助")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"交互模式错误: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🤖 CulverBot 快递车客户端 - 帮助信息

可用命令:
  loading     - 模拟装货按钮按下
  delivery    - 模拟开始配送按钮按下
  emergency   - 模拟紧急停止按钮按下

  door_open   - 模拟开门操作
  door_close  - 模拟关门操作
  status      - 显示当前状态
  orders      - 显示当前订单
  help        - 显示此帮助信息
  quit        - 退出程序

当前状态: {status}
订单数量: {order_count}
        """.format(status=self.current_status, order_count=len(self.current_orders))
        
        print(help_text)
    
    def stop(self):
        """停止客户端"""
        self.logger.info("🛑 停止快递车客户端...")
        self.is_running = False
        
        # 停止组件
        if self.camera:
            self.camera.cleanup()
        if self.gpio:
            self.gpio.cleanup()
        
        self.logger.info("✅ 快递车客户端已停止")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，正在停止...")
        self.stop()
        sys.exit(0)

def main():
    """主函数"""
    robot = RobotClient()
    
    try:
        if robot.start():
            # 主程序会在这里等待交互模式
            pass
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        robot.logger.info("收到中断信号")
    except Exception as e:
        robot.logger.error(f"程序异常: {e}")
    finally:
        robot.stop()

if __name__ == "__main__":
    main() 