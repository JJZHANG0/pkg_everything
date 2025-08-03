#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
import threading
import time
import os
from datetime import datetime
from config import Config
from utils.logger import RobotLogger
from hardware.gpio_controller import GPIOController
from hardware.camera_scanner import CameraScanner
from network.api_client import APIClient

# 设置Pygame环境变量以避免Mac上的问题
# os.environ['SDL_VIDEODRIVER'] = 'x11'  # 移除这行，Mac不支持x11
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

class ModernRobotGUI:
    """现代化机器人GUI界面"""
    
    def __init__(self):
        # 安全初始化Pygame
        try:
            pygame.init()
            # 设置视频驱动
            pygame.display.init()
        except Exception as e:
            print(f"❌ Pygame初始化失败: {e}")
            sys.exit(1)
        
        # 屏幕设置
        self.width = 1400
        self.height = 900
        try:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("🤖 Robot Delivery System")
        except Exception as e:
            print(f"❌ 屏幕设置失败: {e}")
            pygame.quit()
            sys.exit(1)
        
        # 颜色定义 - 现代化配色
        self.colors = {
            'background': (18, 18, 18),      # 深色背景
            'card': (28, 28, 28),            # 卡片背景
            'primary': (0, 122, 255),        # 主色调 - 蓝色
            'success': (52, 199, 89),        # 成功色 - 绿色
            'warning': (255, 149, 0),        # 警告色 - 橙色
            'danger': (255, 59, 48),         # 危险色 - 红色
            'text_primary': (255, 255, 255), # 主文本色
            'text_secondary': (142, 142, 147), # 次要文本色
            'border': (44, 44, 46),          # 边框色
            'accent': (88, 86, 214),         # 强调色 - 紫色
        }
        
        # 字体设置 - 使用默认字体避免问题
        try:
            self.fonts = {
                'title': pygame.font.Font(None, 48),
                'heading': pygame.font.Font(None, 32),
                'body': pygame.font.Font(None, 24),
                'small': pygame.font.Font(None, 18),
                'tiny': pygame.font.Font(None, 14)
            }
        except Exception as e:
            print(f"⚠️ 字体加载失败，使用默认字体: {e}")
            # 使用系统默认字体
            self.fonts = {
                'title': pygame.font.SysFont(None, 48),
                'heading': pygame.font.SysFont(None, 32),
                'body': pygame.font.SysFont(None, 24),
                'small': pygame.font.SysFont(None, 18),
                'tiny': pygame.font.SysFont(None, 14)
            }
        
        # 初始化组件
        try:
            self.logger = RobotLogger()
            self.gpio = GPIOController(self.logger)
            self.camera = CameraScanner(self.logger)
            self.api = APIClient(self.logger)
        except Exception as e:
            print(f"❌ 组件初始化失败: {e}")
            pygame.quit()
            sys.exit(1)
        
        # 状态变量
        self.is_running = True
        self.robot_status = "IDLE"
        self.current_orders = []
        self.log_messages = []
        self.last_poll_time = "Never"
        self.connection_status = "Disconnected"
        self.qr_detection_active = False
        self.camera_feed = None
        self.show_camera = False
        
        # 按钮定义
        self.buttons = {
            'close_door': {
                'rect': pygame.Rect(50, 750, 200, 60),
                'text': '🚪 Close Door & Start',
                'color': self.colors['primary'],
                'hover_color': (0, 102, 235),
                'action': self.close_door_and_start
            },
            'toggle_qr': {
                'rect': pygame.Rect(270, 750, 200, 60),
                'text': '🔍 Start QR Detection',
                'color': self.colors['success'],
                'hover_color': (42, 179, 79),
                'action': self.toggle_qr_detection
            },
            'toggle_camera': {
                'rect': pygame.Rect(490, 750, 200, 60),
                'text': '📷 Toggle Camera',
                'color': self.colors['accent'],
                'hover_color': (78, 76, 194),
                'action': self.toggle_camera_view
            }
        }
        
        # 启动后台线程
        self.start_background_threads()
    
    def start_background_threads(self):
        """启动后台线程"""
        try:
            # 服务器轮询线程
            poll_thread = threading.Thread(target=self.poll_server_loop, daemon=True)
            poll_thread.start()
            
            # 摄像头线程
            camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            camera_thread.start()
        except Exception as e:
            self.add_log_message(f"❌ 后台线程启动失败: {e}")
    
    def poll_server_loop(self):
        """服务器轮询循环"""
        while self.is_running:
            try:
                self.poll_server()
                time.sleep(Config.POLL_INTERVAL)
            except Exception as e:
                self.add_log_message(f"❌ Polling error: {e}")
                time.sleep(5)
    
    def poll_server(self):
        """轮询服务器获取最新数据"""
        try:
            data = self.api.get_current_orders()
            if data:
                self.handle_server_data(data)
                self.last_poll_time = datetime.now().strftime("%H:%M:%S")
                self.connection_status = "Connected"
            else:
                self.connection_status = "Failed"
        except Exception as e:
            self.connection_status = "Error"
            self.add_log_message(f"❌ Server connection failed: {e}")
    
    def handle_server_data(self, data):
        """处理服务器数据"""
        old_order_count = len(self.current_orders)
        self.robot_status = data.get('status', 'IDLE')
        self.current_orders = data.get('current_orders', [])
        
        # 检测新订单
        if len(self.current_orders) > old_order_count:
            self.add_log_message("🔔 New order received!")
            self.gpio.beep(0.3)
    
    def camera_loop(self):
        """摄像头循环"""
        while self.is_running:
            if self.qr_detection_active and self.camera.camera_available:
                try:
                    frame = self.camera.capture_frame()
                    if frame is not None:
                        # 更新摄像头画面
                        self.camera_feed = frame
                        
                        # 检测二维码
                        qr_data = self.camera.scan_qr_code(frame)
                        if qr_data:
                            self.process_qr_data(qr_data)
                            
                except Exception as e:
                    self.add_log_message(f"❌ Camera error: {e}")
            
            time.sleep(0.1)
    
    def process_qr_data(self, qr_data):
        """处理二维码数据"""
        try:
            import json
            data = json.loads(qr_data)
            if 'order_id' in data:
                self.add_log_message(f"✅ Valid QR: Order {data['order_id']}")
                self.gpio.beep(0.2)
                
                # 自动开门
                self.auto_open_door(data['order_id'])
                
        except:
            self.add_log_message(f"📋 Raw QR: {qr_data}")
    
    def auto_open_door(self, order_id):
        """自动开门流程"""
        self.add_log_message("🚪 Auto-opening door...")
        self.gpio.simulate_door_open()
        
        # 15秒后自动关门
        def auto_close():
            time.sleep(15)
            if self.is_running:
                self.add_log_message("🚪 Auto-closing door...")
                self.gpio.simulate_door_close()
                
                # 更新订单状态为DELIVERED
                result = self.api.update_order_status(order_id, 'DELIVERED')
                if result:
                    self.add_log_message(f"✅ Order {order_id} delivered successfully")
                    self.gpio.beep(0.3)
                else:
                    self.add_log_message(f"❌ Failed to update order {order_id} status")
        
        close_thread = threading.Thread(target=auto_close, daemon=True)
        close_thread.start()
    
    def close_door_and_start(self):
        """关门并开始配送"""
        self.add_log_message("🚪 Closing door and starting delivery...")
        self.gpio.simulate_door_close()
        
        # 更新所有ASSIGNED订单为DELIVERING
        for order in self.current_orders:
            if order.get('status') == 'ASSIGNED':
                result = self.api.update_order_status(order['order_id'], 'DELIVERING')
                if result:
                    self.add_log_message(f"✅ Order {order['order_id']} status updated to DELIVERING")
        
        # 更新机器人状态
        result = self.api.start_delivery()
        if result:
            self.add_log_message("🚚 Delivery started successfully")
    
    def toggle_qr_detection(self):
        """切换二维码检测"""
        self.qr_detection_active = not self.qr_detection_active
        status = "Started" if self.qr_detection_active else "Stopped"
        self.add_log_message(f"🔍 QR Detection {status}")
        
        # 更新按钮文本
        self.buttons['toggle_qr']['text'] = (
            "🔍 Stop QR Detection" if self.qr_detection_active 
            else "🔍 Start QR Detection"
        )
    
    def toggle_camera_view(self):
        """切换摄像头显示"""
        self.show_camera = not self.show_camera
        status = "Shown" if self.show_camera else "Hidden"
        self.add_log_message(f"📷 Camera view {status}")
    
    def add_log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        
        # 保持最多20条日志
        if len(self.log_messages) > 20:
            self.log_messages.pop(0)
    
    def draw_rounded_rect(self, surface, rect, color, radius=10):
        """绘制圆角矩形"""
        try:
            pygame.draw.rect(surface, color, rect, border_radius=radius)
        except:
            # 如果圆角不支持，使用普通矩形
            pygame.draw.rect(surface, color, rect)
    
    def draw_button(self, button_data, mouse_pos):
        """绘制按钮"""
        try:
            color = button_data['hover_color'] if button_data['rect'].collidepoint(mouse_pos) else button_data['color']
            self.draw_rounded_rect(self.screen, button_data['rect'], color)
            
            # 绘制按钮文本
            text_surface = self.fonts['body'].render(button_data['text'], True, self.colors['text_primary'])
            text_rect = text_surface.get_rect(center=button_data['rect'].center)
            self.screen.blit(text_surface, text_rect)
        except Exception as e:
            print(f"⚠️ 按钮绘制失败: {e}")
    
    def draw_status_card(self):
        """绘制状态卡片"""
        try:
            card_rect = pygame.Rect(30, 30, 400, 200)
            self.draw_rounded_rect(self.screen, card_rect, self.colors['card'])
            
            # 标题
            title = self.fonts['heading'].render("🤖 Robot Status", True, self.colors['text_primary'])
            self.screen.blit(title, (50, 50))
            
            # 状态信息
            status_color = {
                'IDLE': self.colors['text_secondary'],
                'LOADING': self.colors['warning'],
                'DELIVERING': self.colors['primary'],
                'MAINTENANCE': self.colors['danger']
            }.get(self.robot_status, self.colors['text_secondary'])
            
            status_text = self.fonts['body'].render(f"Status: {self.robot_status}", True, status_color)
            self.screen.blit(status_text, (50, 90))
            
            # 连接状态
            conn_color = self.colors['success'] if self.connection_status == "Connected" else self.colors['danger']
            conn_text = self.fonts['small'].render(f"Connection: {self.connection_status}", True, conn_color)
            self.screen.blit(conn_text, (50, 120))
            
            # 最后轮询时间
            poll_text = self.fonts['small'].render(f"Last Poll: {self.last_poll_time}", True, self.colors['text_secondary'])
            self.screen.blit(poll_text, (50, 150))
            
            # 订单数量
            orders_text = self.fonts['body'].render(f"Orders: {len(self.current_orders)}", True, self.colors['text_primary'])
            self.screen.blit(orders_text, (50, 180))
        except Exception as e:
            print(f"⚠️ 状态卡片绘制失败: {e}")
    
    def draw_orders_card(self):
        """绘制订单卡片"""
        try:
            card_rect = pygame.Rect(30, 250, 400, 300)
            self.draw_rounded_rect(self.screen, card_rect, self.colors['card'])
            
            # 标题
            title = self.fonts['heading'].render("📦 Current Orders", True, self.colors['text_primary'])
            self.screen.blit(title, (50, 270))
            
            # 订单列表
            y_offset = 310
            for i, order in enumerate(self.current_orders[:5]):  # 最多显示5个订单
                order_text = f"#{order.get('order_id', 'N/A')} - {order.get('status', 'Unknown')}"
                text_surface = self.fonts['small'].render(order_text, True, self.colors['text_primary'])
                self.screen.blit(text_surface, (50, y_offset))
                
                # 配送地址
                delivery = order.get('delivery_location', {})
                address_text = f"  → {delivery.get('building', 'Unknown')}"
                addr_surface = self.fonts['tiny'].render(address_text, True, self.colors['text_secondary'])
                self.screen.blit(addr_surface, (50, y_offset + 20))
                
                y_offset += 45
        except Exception as e:
            print(f"⚠️ 订单卡片绘制失败: {e}")
    
    def draw_log_card(self):
        """绘制日志卡片"""
        try:
            card_rect = pygame.Rect(450, 30, 500, 400)
            self.draw_rounded_rect(self.screen, card_rect, self.colors['card'])
            
            # 标题
            title = self.fonts['heading'].render("📋 System Log", True, self.colors['text_primary'])
            self.screen.blit(title, (470, 50))
            
            # 日志内容
            y_offset = 90
            for log in self.log_messages[-15:]:  # 显示最近15条日志
                text_surface = self.fonts['tiny'].render(log, True, self.colors['text_secondary'])
                self.screen.blit(text_surface, (470, y_offset))
                y_offset += 20
        except Exception as e:
            print(f"⚠️ 日志卡片绘制失败: {e}")
    
    def draw_camera_card(self):
        """绘制摄像头卡片"""
        if not self.show_camera:
            return
            
        try:
            card_rect = pygame.Rect(450, 450, 500, 300)
            self.draw_rounded_rect(self.screen, card_rect, self.colors['card'])
            
            # 标题
            title = self.fonts['heading'].render("📷 Camera Feed", True, self.colors['text_primary'])
            self.screen.blit(title, (470, 470))
            
            # 摄像头画面占位符
            if self.camera_feed is not None:
                # 这里可以显示实际的摄像头画面
                camera_rect = pygame.Rect(470, 500, 460, 230)
                self.draw_rounded_rect(self.screen, camera_rect, self.colors['border'])
                
                # 显示摄像头状态
                status_text = "🟢 Camera Active" if self.qr_detection_active else "🔴 Camera Inactive"
                status_surface = self.fonts['small'].render(status_text, True, self.colors['text_primary'])
                self.screen.blit(status_surface, (480, 520))
            else:
                camera_rect = pygame.Rect(470, 500, 460, 230)
                self.draw_rounded_rect(self.screen, camera_rect, self.colors['border'])
                
                no_feed_text = self.fonts['body'].render("No Camera Feed", True, self.colors['text_secondary'])
                text_rect = no_feed_text.get_rect(center=camera_rect.center)
                self.screen.blit(no_feed_text, text_rect)
        except Exception as e:
            print(f"⚠️ 摄像头卡片绘制失败: {e}")
    
    def draw_control_panel(self):
        """绘制控制面板"""
        try:
            panel_rect = pygame.Rect(30, 570, 400, 200)
            self.draw_rounded_rect(self.screen, panel_rect, self.colors['card'])
            
            # 标题
            title = self.fonts['heading'].render("🎮 Control Panel", True, self.colors['text_primary'])
            self.screen.blit(title, (50, 590))
            
            # 绘制按钮
            mouse_pos = pygame.mouse.get_pos()
            for button_data in self.buttons.values():
                self.draw_button(button_data, mouse_pos)
        except Exception as e:
            print(f"⚠️ 控制面板绘制失败: {e}")
    
    def draw(self):
        """绘制整个界面"""
        try:
            # 背景
            self.screen.fill(self.colors['background'])
            
            # 绘制各个组件
            self.draw_status_card()
            self.draw_orders_card()
            self.draw_log_card()
            self.draw_camera_card()
            self.draw_control_panel()
            
            # 更新显示
            pygame.display.flip()
        except Exception as e:
            print(f"❌ 绘制失败: {e}")
    
    def handle_events(self):
        """处理事件"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    return
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        mouse_pos = pygame.mouse.get_pos()
                        for button_data in self.buttons.values():
                            if button_data['rect'].collidepoint(mouse_pos):
                                button_data['action']()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.toggle_qr_detection()
                    elif event.key == pygame.K_v:
                        self.toggle_camera_view()
                    elif event.key == pygame.K_ESCAPE:
                        self.is_running = False
                        return
        except Exception as e:
            print(f"❌ 事件处理失败: {e}")
    
    def run_gui(self):
        """运行GUI主循环"""
        try:
            clock = pygame.time.Clock()
            
            while self.is_running:
                self.handle_events()
                self.draw()
                clock.tick(60)
            
            pygame.quit()
            sys.exit()
        except Exception as e:
            print(f"❌ GUI运行失败: {e}")
            pygame.quit()
            sys.exit(1)

def main():
    """主函数"""
    try:
        print("🚀 启动现代化机器人GUI...")
        gui = ModernRobotGUI()
        gui.run_gui()
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 