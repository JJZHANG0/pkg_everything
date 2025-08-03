#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import json
from datetime import datetime, timedelta
from config import Config
from utils.logger import RobotLogger
from hardware.gpio_controller import GPIOController
from hardware.camera_scanner import CameraScanner
from network.api_client import APIClient

class EnhancedRobotClient:
    """增强版机器人客户端"""
    
    def __init__(self):
        self.logger = RobotLogger()
        self.api = APIClient(self.logger)
        self.gpio = GPIOController(self.logger)
        self.camera = CameraScanner(self.logger)
        
        # 状态变量
        self.is_running = True
        self.current_orders = []
        self.robot_status = "IDLE"
        self.current_location = "Warehouse"
        self.battery_level = 100
        self.door_status = "CLOSED"
        
        # 配送相关
        self.delivery_route = []
        self.current_delivery_index = 0
        self.qr_wait_start_time = None
        self.qr_wait_timeout = 600  # 10分钟超时
        
        # 启动后台线程
        self.start_background_threads()
    
    def start_background_threads(self):
        """启动后台线程"""
        # 状态反馈线程（每5秒）
        status_thread = threading.Thread(target=self.status_feedback_loop, daemon=True)
        status_thread.start()
        
        # 订单轮询线程（每3秒）
        poll_thread = threading.Thread(target=self.order_polling_loop, daemon=True)
        poll_thread.start()
        
        # 配送监控线程（每1秒）
        delivery_thread = threading.Thread(target=self.delivery_monitoring_loop, daemon=True)
        delivery_thread.start()
        
        self.logger.info("🚀 增强版机器人客户端启动完成")
    
    def status_feedback_loop(self):
        """状态反馈循环"""
        while self.is_running:
            try:
                # 模拟位置更新（实际应用中应该从GPS或SLAM获取）
                self.update_location()
                
                # 模拟电池消耗
                self.update_battery()
                
                # 发送状态到服务器
                result = self.api.update_robot_status(
                    location=self.current_location,
                    battery=self.battery_level,
                    door_status=self.door_status,
                    status=self.robot_status
                )
                
                if result:
                    self.logger.info(f"📍 位置: {self.current_location}, 🔋 电池: {self.battery_level}%")
                
                time.sleep(5)  # 每5秒反馈一次
                
            except Exception as e:
                self.logger.error(f"状态反馈异常: {e}")
                time.sleep(10)
    
    def order_polling_loop(self):
        """订单轮询循环"""
        while self.is_running:
            try:
                data = self.api.get_current_orders()
                if data:
                    old_order_count = len(self.current_orders)
                    self.current_orders = data.get('current_orders', [])
                    
                    # 检测新订单
                    if len(self.current_orders) > old_order_count:
                        self.logger.info("🔔 收到新订单!")
                        self.gpio.beep(0.3)
                        self.gpio.set_led_status(True)
                        
                        # 更新机器人状态为装货中
                        self.robot_status = "LOADING"
                        self.api.update_robot_status(status=self.robot_status)
                
                time.sleep(3)  # 每3秒轮询一次
                
            except Exception as e:
                self.logger.error(f"订单轮询异常: {e}")
                time.sleep(10)
    
    def delivery_monitoring_loop(self):
        """配送监控循环"""
        while self.is_running:
            try:
                if self.robot_status == "DELIVERING" and self.current_orders:
                    self.monitor_delivery()
                elif self.robot_status == "RETURNING":
                    self.monitor_return()
                
                time.sleep(1)  # 每1秒检查一次
                
            except Exception as e:
                self.logger.error(f"配送监控异常: {e}")
                time.sleep(5)
    
    def monitor_delivery(self):
        """监控配送过程"""
        if not self.current_orders:
            return
        
        current_order = self.current_orders[self.current_delivery_index]
        order_id = current_order['order_id']
        
        # 检查是否到达配送点
        if self.check_arrived_at_destination(current_order):
            self.logger.info(f"🎯 到达配送点: {current_order['delivery_location']}")
            
            # 开始等待二维码扫描
            self.start_qr_waiting(order_id)
            
            # 检查二维码等待超时
            if self.qr_wait_start_time:
                elapsed_time = (datetime.now() - self.qr_wait_start_time).total_seconds()
                if elapsed_time > self.qr_wait_timeout:
                    self.logger.warning(f"⏰ 二维码等待超时 ({elapsed_time:.0f}秒)，开始自动返航")
                    self.start_auto_return()
    
    def monitor_return(self):
        """监控返航过程"""
        # 检查是否返回仓库
        if self.check_arrived_at_warehouse():
            self.logger.info("🏠 已返回仓库")
            self.robot_status = "IDLE"
            self.current_delivery_index = 0
            self.delivery_route = []
            self.api.update_robot_status(status=self.robot_status)
    
    def start_qr_waiting(self, order_id):
        """开始等待二维码扫描"""
        if not self.qr_wait_start_time:
            self.qr_wait_start_time = datetime.now()
            self.api.start_qr_wait(order_id)
            self.logger.info(f"📱 开始等待二维码扫描，订单: {order_id}")
            
            # 启动二维码扫描
            self.start_qr_scanning(order_id)
    
    def start_qr_scanning(self, order_id):
        """开始二维码扫描"""
        def qr_scan_loop():
            while self.is_running and self.qr_wait_start_time:
                try:
                    # 尝试扫描二维码
                    qr_data = self.camera.scan_qr_code()
                    if qr_data:
                        self.process_qr_scan(order_id, qr_data)
                        break
                    
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"二维码扫描异常: {e}")
                    time.sleep(2)
        
        qr_thread = threading.Thread(target=qr_scan_loop, daemon=True)
        qr_thread.start()
    
    def process_qr_scan(self, order_id, qr_data):
        """处理二维码扫描"""
        try:
            # 验证二维码数据
            if self.validate_qr_data(qr_data, order_id):
                self.logger.info(f"✅ 二维码验证成功，订单: {order_id}")
                
                # 开门
                self.open_door()
                
                # 通知服务器
                result = self.api.qr_scanned(order_id, qr_data)
                if result:
                    self.logger.info(f"📦 包裹已取出，订单: {order_id}")
                    
                    # 15秒后自动关门
                    threading.Timer(15, self.close_door).start()
                    
                    # 移动到下一个订单
                    self.move_to_next_order()
                else:
                    self.logger.error(f"❌ 二维码处理失败，订单: {order_id}")
            else:
                self.logger.warning(f"⚠️ 二维码验证失败，订单: {order_id}")
                
        except Exception as e:
            self.logger.error(f"二维码处理异常: {e}")
    
    def validate_qr_data(self, qr_data, order_id):
        """验证二维码数据"""
        try:
            # 这里应该实现具体的二维码验证逻辑
            # 暂时简单验证是否包含订单ID
            if isinstance(qr_data, dict) and qr_data.get('order_id') == order_id:
                return True
            elif isinstance(qr_data, str):
                # 尝试解析JSON
                parsed_data = json.loads(qr_data)
                return parsed_data.get('order_id') == order_id
            return False
        except:
            return False
    
    def open_door(self):
        """开门"""
        self.logger.info("🚪 开门中...")
        self.gpio.simulate_door_open()
        self.door_status = "OPEN"
        self.api.update_robot_status(door_status=self.door_status)
    
    def close_door(self):
        """关门"""
        self.logger.info("🚪 关门中...")
        self.gpio.simulate_door_close()
        self.door_status = "CLOSED"
        self.api.update_robot_status(door_status=self.door_status)
    
    def move_to_next_order(self):
        """移动到下一个订单"""
        self.current_delivery_index += 1
        self.qr_wait_start_time = None
        
        if self.current_delivery_index >= len(self.current_orders):
            # 所有订单配送完成，开始返航
            self.logger.info("🎉 所有订单配送完成，开始返航")
            self.start_auto_return()
        else:
            # 移动到下一个配送点
            next_order = self.current_orders[self.current_delivery_index]
            self.logger.info(f"🚚 移动到下一个配送点: {next_order['delivery_location']}")
    
    def start_auto_return(self):
        """开始自动返航"""
        self.robot_status = "RETURNING"
        self.qr_wait_start_time = None
        self.api.auto_return()
        self.logger.info("🔄 开始自动返航")
    
    def update_location(self):
        """更新位置（模拟）"""
        # 实际应用中应该从GPS或SLAM获取真实位置
        locations = [
            "ORIGIN", "Lauridsen Barrack"
        ]
        
        if self.robot_status == "DELIVERING" and self.current_orders:
            current_order = self.current_orders[self.current_delivery_index]
            self.current_location = current_order['delivery_location']
        elif self.robot_status == "RETURNING":
            self.current_location = "Warehouse"
        else:
            self.current_location = "Warehouse"
    
    def update_battery(self):
        """更新电池电量（模拟）"""
        # 模拟电池消耗
        if self.robot_status in ["DELIVERING", "RETURNING"]:
            self.battery_level = max(0, self.battery_level - 0.1)
        else:
            # 空闲时充电
            self.battery_level = min(100, self.battery_level + 0.05)
    
    def check_arrived_at_destination(self, order):
        """检查是否到达配送点（模拟）"""
        # 实际应用中应该基于真实位置判断
        return self.current_location == order['delivery_location']
    
    def check_arrived_at_warehouse(self):
        """检查是否到达仓库（模拟）"""
        return self.current_location == "Warehouse"
    
    def start_delivery(self):
        """开始配送"""
        if self.robot_status == "LOADING" and self.current_orders:
            self.robot_status = "DELIVERING"
            self.current_delivery_index = 0
            self.api.update_robot_status(status=self.robot_status)
            self.logger.info("🚀 开始配送")
            return True
        return False
    
    def stop_robot(self):
        """停止机器人"""
        self.is_running = False
        self.robot_status = "IDLE"
        self.api.update_robot_status(status=self.robot_status)
        self.logger.info("⏹️ 机器人已停止")
    
    def get_status_summary(self):
        """获取状态摘要"""
        return {
            "robot_status": self.robot_status,
            "current_location": self.current_location,
            "battery_level": self.battery_level,
            "door_status": self.door_status,
            "current_orders": len(self.current_orders),
            "current_delivery_index": self.current_delivery_index,
            "qr_waiting": self.qr_wait_start_time is not None
        }


def main():
    """主函数"""
    try:
        robot = EnhancedRobotClient()
        
        # 保持主线程运行
        while robot.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在停止机器人...")
        if 'robot' in locals():
            robot.stop_robot()
    except Exception as e:
        print(f"❌ 程序异常: {e}")


if __name__ == "__main__":
    main() 