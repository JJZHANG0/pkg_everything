#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime

class TestSimpleGUI:
    """最简单的测试GUI"""
    
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("🤖 Robot Test GUI")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # 状态变量
        self.is_running = True
        
        # 创建界面
        self.create_widgets()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_label = tk.Label(self.root, text="🤖 Robot Test GUI", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#1a1a1a')
        title_label.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="Status: Ready", 
                                    font=('Arial', 12), 
                                    fg='white', bg='#1a1a1a')
        self.status_label.pack(pady=5)
        
        # 按钮
        self.test_btn = tk.Button(self.root, text="🔧 Test Button", 
                                 command=self.test_function,
                                 bg='#007AFF', fg='white', 
                                 font=('Arial', 12, 'bold'),
                                 width=20, height=2)
        self.test_btn.pack(pady=10)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            self.root, 
            bg='#2a2a2a', 
            fg='white', 
            font=('Consolas', 10),
            height=15
        )
        self.log_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 添加初始日志
        self.add_log("🚀 Test GUI started successfully")
        self.add_log("✅ Basic interface loaded")
    
    def test_function(self):
        """测试功能"""
        self.add_log("🔧 Test button clicked!")
        self.status_label.config(text="Status: Testing...")
        
        # 模拟一些操作
        def simulate_work():
            time.sleep(2)
            self.add_log("⏳ Simulated work completed")
            self.root.after(0, lambda: self.status_label.config(text="Status: Ready"))
        
        work_thread = threading.Thread(target=simulate_work, daemon=True)
        work_thread.start()
    
    def add_log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def on_closing(self):
        """关闭程序"""
        self.add_log("🛑 Shutting down test GUI...")
        self.is_running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行GUI"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"❌ GUI运行失败: {e}")

def main():
    """主函数"""
    try:
        print("🚀 启动测试GUI...")
        gui = TestSimpleGUI()
        gui.run()
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")

if __name__ == "__main__":
    main() 