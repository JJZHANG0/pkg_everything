#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 自动清理命令队列脚本
定时清理已完成的命令和超时命令
"""

import requests
import time
import json
from datetime import datetime

class CommandQueueCleaner:
    def __init__(self, server_url="http://localhost:8000", robot_id=1):
        self.server_url = server_url
        self.robot_id = robot_id
        self.token = None
        
    def login(self, username="root", password="root"):
        """登录获取token"""
        try:
            response = requests.post(
                f"{self.server_url}/api/token/",
                headers={"Content-Type": "application/json"},
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                self.token = response.json()["access"]
                print(f"✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def cleanup_queue(self):
        """清理命令队列"""
        if not self.token:
            print("❌ 请先登录")
            return False
            
        try:
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/cleanup_command_queue/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 队列清理完成:")
                print(f"   - 已删除完成命令: {data.get('completed_deleted', 0)}")
                print(f"   - 超时命令处理: {data.get('timeout_commands', 0)}")
                print(f"   - 已删除失败命令: {data.get('failed_deleted', 0)}")
                print(f"   - 总计删除: {data.get('total_deleted', 0)}")
                return True
            else:
                print(f"❌ 清理失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 清理异常: {e}")
            return False
    
    def get_queue_status(self):
        """获取队列状态"""
        if not self.token:
            print("❌ 请先登录")
            return False
            
        try:
            response = requests.get(
                f"{self.server_url}/api/robots/{self.robot_id}/get_commands/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 队列状态:")
                print(f"   - 待执行命令: {data.get('command_count', 0)}")
                print(f"   - 超时处理: {data.get('timeout_processed', 0)}")
                return data.get('command_count', 0)
            else:
                print(f"❌ 获取状态失败: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ 获取状态异常: {e}")
            return 0
    
    def run_cleanup_loop(self, interval_minutes=5):
        """运行清理循环"""
        print(f"🚀 开始自动清理循环 (间隔: {interval_minutes}分钟)")
        print("=" * 50)
        
        while True:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n⏰ [{current_time}] 执行清理...")
                
                # 获取队列状态
                pending_count = self.get_queue_status()
                
                # 执行清理
                if self.cleanup_queue():
                    print(f"✅ 清理完成，当前待执行命令: {pending_count}")
                else:
                    print("❌ 清理失败")
                
                print(f"⏳ 等待 {interval_minutes} 分钟后继续...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 用户中断，停止清理循环")
                break
            except Exception as e:
                print(f"❌ 循环异常: {e}")
                print("⏳ 等待1分钟后重试...")
                time.sleep(60)

def main():
    """主函数"""
    print("🤖 命令队列自动清理工具")
    print("=" * 50)
    
    # 配置参数
    server_url = input("请输入服务器地址 (默认: http://localhost:8000): ").strip()
    if not server_url:
        server_url = "http://localhost:8000"
    
    robot_id = input("请输入机器人ID (默认: 1): ").strip()
    if not robot_id:
        robot_id = 1
    else:
        robot_id = int(robot_id)
    
    username = input("请输入用户名 (默认: root): ").strip() or "root"
    password = input("请输入密码 (默认: root): ").strip() or "root"
    
    interval = input("请输入清理间隔分钟数 (默认: 5): ").strip()
    if not interval:
        interval = 5
    else:
        interval = int(interval)
    
    print(f"\n📋 配置信息:")
    print(f"   服务器: {server_url}")
    print(f"   机器人ID: {robot_id}")
    print(f"   用户名: {username}")
    print(f"   清理间隔: {interval}分钟")
    print("=" * 50)
    
    # 创建清理器
    cleaner = CommandQueueCleaner(server_url, robot_id)
    
    # 登录
    if not cleaner.login(username, password):
        print("❌ 登录失败，无法继续")
        return
    
    # 选择模式
    print("\n🔧 选择运行模式:")
    print("   1. 单次清理")
    print("   2. 自动循环清理")
    
    mode = input("请选择 (1/2): ").strip()
    
    if mode == "1":
        # 单次清理
        print("\n🧹 执行单次清理...")
        cleaner.cleanup_queue()
    elif mode == "2":
        # 循环清理
        cleaner.run_cleanup_loop(interval)
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 