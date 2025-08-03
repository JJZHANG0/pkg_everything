#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from config import Config
from utils.logger import RobotLogger
from hardware.gpio_controller import GPIOController
from hardware.camera_scanner import CameraScanner
from network.api_client import APIClient

class SimpleRobotGUI:
    """简化的机器人GUI界面 - 使用tkinter"""
    
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("🤖 Robot Delivery System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='white', background='#1a1a1a')
        self.style.configure('Status.TLabel', font=('Arial', 12), foreground='white', background='#1a1a1a')
        self.style.configure('Card.TFrame', background='#2a2a2a', relief='raised', borderwidth=1)
        
        # 初始化组件
        self.logger = RobotLogger()
        self.gpio = GPIOController(self.logger)
        self.camera = CameraScanner(self.logger)
        self.api = APIClient(self.logger)
        
        # 状态变量
        self.is_running = True
        self.robot_status = "IDLE"
        self.current_orders = []
        self.last_poll_time = "Never"
        self.connection_status = "Disconnected"
        self.qr_detection_active = False
        
        # 创建界面
        self.create_widgets()
        
        # 启动后台线程
        self.start_background_threads()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_label = ttk.Label(self.root, text="🤖 Robot Delivery System", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧面板
        left_frame = ttk.Frame(main_frame, style='Card.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # 右侧面板
        right_frame = ttk.Frame(main_frame, style='Card.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 左侧内容
        self.create_status_panel(left_frame)
        self.create_orders_panel(left_frame)
        self.create_control_panel(left_frame)
        
        # 右侧内容
        self.create_log_panel(right_frame)
    
    def create_status_panel(self, parent):
        """创建状态面板"""
        # 状态卡片
        status_frame = ttk.Frame(parent, style='Card.TFrame')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        # 标题
        ttk.Label(status_frame, text="🤖 Robot Status", style='Title.TLabel').pack(pady=5)
        
        # 状态信息
        self.status_label = ttk.Label(status_frame, text="Status: IDLE", style='Status.TLabel')
        self.status_label.pack(anchor='w', padx=10)
        
        self.connection_label = ttk.Label(status_frame, text="Connection: Disconnected", style='Status.TLabel')
        self.connection_label.pack(anchor='w', padx=10)
        
        self.poll_label = ttk.Label(status_frame, text="Last Poll: Never", style='Status.TLabel')
        self.poll_label.pack(anchor='w', padx=10)
        
        self.orders_label = ttk.Label(status_frame, text="Orders: 0", style='Status.TLabel')
        self.orders_label.pack(anchor='w', padx=10)
    
    def create_orders_panel(self, parent):
        """创建订单面板"""
        # 订单卡片
        orders_frame = ttk.Frame(parent, style='Card.TFrame')
        orders_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 标题
        ttk.Label(orders_frame, text="📦 Current Orders", style='Title.TLabel').pack(pady=5)
        
        # 订单列表
        self.orders_text = scrolledtext.ScrolledText(
            orders_frame, 
            height=8, 
            bg='#2a2a2a', 
            fg='white', 
            font=('Arial', 10),
            state='disabled'
        )
        self.orders_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        # 控制卡片
        control_frame = ttk.Frame(parent, style='Card.TFrame')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # 标题
        ttk.Label(control_frame, text="🎮 Control Panel", style='Title.TLabel').pack(pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        # 按钮
        self.close_door_btn = tk.Button(
            button_frame, 
            text="🚪 Close Door & Start", 
            command=self.close_door_and_start,
            bg='#007AFF', fg='white', font=('Arial', 12, 'bold'),
            width=20, height=2
        )
        self.close_door_btn.pack(pady=5)
        
        self.qr_btn = tk.Button(
            button_frame, 
            text="🔍 Start QR Detection", 
            command=self.toggle_qr_detection,
            bg='#34C759', fg='white', font=('Arial', 12, 'bold'),
            width=20, height=2
        )
        self.qr_btn.pack(pady=5)
        
        # 快捷键提示
        ttk.Label(control_frame, text="Shortcuts: R=QR Detection, ESC=Exit", style='Status.TLabel').pack(pady=5)
    
    def create_log_panel(self, parent):
        """创建日志面板"""
        # 日志卡片
        log_frame = ttk.Frame(parent, style='Card.TFrame')
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 标题
        ttk.Label(log_frame, text="📋 System Log", style='Title.TLabel').pack(pady=5)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            bg='#2a2a2a', 
            fg='white', 
            font=('Consolas', 10),
            state='disabled'
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 绑定键盘事件
        self.root.bind('<Key>', self.handle_keypress)
    
    def start_background_threads(self):
        """启动后台线程"""
        # 服务器轮询线程
        poll_thread = threading.Thread(target=self.poll_server_loop, daemon=True)
        poll_thread.start()
        
        # 摄像头线程
        camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        camera_thread.start()
    
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
        
        # 更新UI
        self.root.after(0, self.update_status_display)
    
    def handle_server_data(self, data):
        """处理服务器数据"""
        old_order_count = len(self.current_orders)
        self.robot_status = data.get('status', 'IDLE')
        self.current_orders = data.get('current_orders', [])
        
        # 检测新订单
        if len(self.current_orders) > old_order_count:
            self.add_log_message("🔔 New order received!")
            self.gpio.beep(0.3)
        
        # 更新UI
        self.root.after(0, self.update_orders_display)
    
    def camera_loop(self):
        """摄像头循环"""
        while self.is_running:
            if self.qr_detection_active and self.camera.camera_available:
                try:
                    frame = self.camera.capture_frame()
                    if frame is not None:
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
        self.qr_btn.config(text="🔍 Stop QR Detection" if self.qr_detection_active else "🔍 Start QR Detection")
    
    def handle_keypress(self, event):
        """处理键盘事件"""
        if event.keysym == 'r' or event.keysym == 'R':
            self.toggle_qr_detection()
        elif event.keysym == 'Escape':
            self.on_closing()
    
    def add_log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 在主线程中更新UI
        self.root.after(0, lambda: self.update_log_display(log_entry))
    
    def update_status_display(self):
        """更新状态显示"""
        self.status_label.config(text=f"Status: {self.robot_status}")
        self.connection_label.config(text=f"Connection: {self.connection_status}")
        self.poll_label.config(text=f"Last Poll: {self.last_poll_time}")
        self.orders_label.config(text=f"Orders: {len(self.current_orders)}")
    
    def update_orders_display(self):
        """更新订单显示"""
        self.orders_text.config(state='normal')
        self.orders_text.delete(1.0, tk.END)
        
        if not self.current_orders:
            self.orders_text.insert(tk.END, "No orders\n")
        else:
            for order in self.current_orders:
                order_id = order.get('order_id', 'N/A')
                status = order.get('status', 'Unknown')
                delivery = order.get('delivery_location', {})
                building = delivery.get('building', 'Unknown')
                
                self.orders_text.insert(tk.END, f"#{order_id} - {status}\n")
                self.orders_text.insert(tk.END, f"  → {building}\n\n")
        
        self.orders_text.config(state='disabled')
    
    def update_log_display(self, log_entry):
        """更新日志显示"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 保持最多100行日志
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete(1.0, f"{len(lines)-100}.0")
        
        self.log_text.config(state='disabled')
    
    def on_closing(self):
        """关闭程序"""
        self.add_log_message("🛑 Shutting down robot GUI...")
        self.is_running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行GUI"""
        try:
            self.add_log_message("🚀 Robot GUI started successfully")
            self.root.mainloop()
        except Exception as e:
            print(f"❌ GUI运行失败: {e}")

def main():
    """主函数"""
    try:
        print("🚀 启动简化机器人GUI...")
        gui = SimpleRobotGUI()
        gui.run()
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")

if __name__ == "__main__":
    main() 