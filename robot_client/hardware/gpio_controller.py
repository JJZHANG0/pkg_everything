#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from config import Config

class GPIOController:
    """GPIO硬件控制器 - Mac模拟版本"""
    
    def __init__(self, logger):
        self.logger = logger
        self.pins = Config.GPIO_PINS
        self.callbacks = {}
        self.is_running = False
        self.simulated_states = {
            'door_closed': True,
            'loading_button_pressed': False,
            'delivery_button_pressed': False,
            'emergency_stop_pressed': False
        }
        
        self.logger.info("GPIO控制器初始化完成 (Mac模拟模式)")
    
    def setup_gpio(self):
        """初始化GPIO设置 - 模拟版本"""
        self.logger.info("模拟GPIO设置完成")
        return True
    
    def button_callback(self, channel):
        """按钮回调函数 - 模拟版本"""
        pass
    
    def register_callback(self, event, callback):
        """注册回调函数"""
        self.callbacks[event] = callback
        self.logger.info(f"注册回调函数: {event}")
    
    def get_door_status(self):
        """获取门状态 - 模拟版本"""
        return self.simulated_states['door_closed']
    
    def set_door_status(self, closed):
        """设置门状态 - 模拟版本"""
        self.simulated_states['door_closed'] = closed
        status = "关闭" if closed else "打开"
        self.logger.info(f"🚪 模拟门状态: {status}")
    
    def set_led_status(self, status):
        """设置状态LED - 模拟版本"""
        led_status = "亮起" if status else "熄灭"
        self.logger.info(f"💡 模拟状态LED: {led_status}")
    
    def set_loading_led(self, status):
        """设置装货LED - 模拟版本"""
        led_status = "亮起" if status else "熄灭"
        self.logger.info(f"📦 模拟装货LED: {led_status}")
    
    def set_delivering_led(self, status):
        """设置配送LED - 模拟版本"""
        led_status = "亮起" if status else "熄灭"
        self.logger.info(f"🚚 模拟配送LED: {led_status}")
    

    
    def beep(self, duration=0.5):
        """蜂鸣器响一声 - 模拟版本"""
        self.logger.info(f"🔊 模拟蜂鸣器响 {duration}秒")
        time.sleep(duration)
    
    def beep_pattern(self, pattern):
        """蜂鸣器模式 - 模拟版本"""
        self.logger.info(f"🔊 模拟蜂鸣器模式: {pattern}")
        for duration in pattern:
            time.sleep(duration)
            time.sleep(0.1)
    
    def simulate_button_press(self, button_type):
        """模拟按钮按下"""
        if button_type == 'loading':
            self.logger.info("🔘 模拟装货按钮被按下")
            if 'loading_button' in self.callbacks:
                self.callbacks['loading_button']()
        elif button_type == 'delivery':
            self.logger.info("🔘 模拟开始配送按钮被按下")
            if 'delivery_button' in self.callbacks:
                self.callbacks['delivery_button']()
        elif button_type == 'emergency':
            self.logger.warning("🔘 模拟紧急停止按钮被按下！")
            if 'emergency_stop' in self.callbacks:
                self.callbacks['emergency_stop']()

    
    def simulate_door_open(self):
        """模拟开门"""
        self.set_door_status(False)
        self.logger.info("🚪 模拟开门操作")
    
    def simulate_door_close(self):
        """模拟关门"""
        self.set_door_status(True)
        self.logger.info("🚪 模拟关门操作")
    
    def simulate_qr_scan(self):
        """模拟二维码扫描"""
        self.logger.info("📱 模拟二维码扫描...")
        
        # 模拟扫描到的二维码数据
        test_qr_data = {
            "order_id": 1,
            "student_id": 2,
            "student_name": "张三",
            "delivery_building": "宿舍楼A",
            "delivery_room": "101",
            "package_type": "书籍",
            "signature": "abc123def456ghi789"
        }
        
        self.logger.info(f"📋 扫描到二维码数据: {test_qr_data}")
        
        # 触发二维码扫描回调
        if 'qr_scanned' in self.callbacks:
            self.callbacks['qr_scanned'](test_qr_data)
    
    def cleanup(self):
        """清理资源 - 模拟版本"""
        self.logger.info("GPIO模拟器清理完成") 