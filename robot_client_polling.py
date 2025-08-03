#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 机器人轮询客户端
使用HTTP轮询方式与服务器通信
"""

import requests
import json
import time
import random
from datetime import datetime

class RobotPollingClient:
    """机器人轮询客户端"""
    
    def __init__(self, server_url, robot_id):
        self.server_url = server_url
        self.robot_id = robot_id
        self.running = False
        
    def send_heartbeat(self):
        """发送心跳消息"""
        try:
            heartbeat_data = {
                "robot_id": self.robot_id,
                "timestamp": time.time(),
                "status": "online"
            }
            
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/heartbeat/",
                json=heartbeat_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"💓 心跳发送成功: {self.robot_id}")
            else:
                print(f"❌ 心跳发送失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 心跳发送错误: {e}")
    
    def send_status_update(self):
        """发送状态更新"""
        try:
            status_data = {
                "robot_id": self.robot_id,
                "data": {
                    "battery": random.randint(60, 100),
                    "location": f"Building {random.choice(['A', 'B', 'C'])}",
                    "door_status": random.choice(["open", "closed"]),
                    "speed": random.randint(0, 5),
                    "temperature": random.uniform(20, 30)
                },
                "timestamp": time.time()
            }
            
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/update_status/",
                json=status_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"📊 状态更新成功: {status_data['data']}")
            else:
                print(f"❌ 状态更新失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 状态更新错误: {e}")
    
    def check_commands(self):
        """检查是否有新命令"""
        try:
            response = requests.get(
                f"{self.server_url}/api/robots/{self.robot_id}/commands/",
                timeout=5
            )
            
            if response.status_code == 200:
                commands = response.json()
                if commands:
                    print(f"📥 收到命令: {commands}")
                    # 处理命令
                    for command in commands:
                        self.execute_command(command)
                else:
                    print("⏳ 暂无新命令")
            else:
                print(f"❌ 获取命令失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 检查命令错误: {e}")
    
    def execute_command(self, command):
        """执行命令"""
        try:
            command_type = command.get('command')
            command_id = command.get('command_id')
            
            print(f"🔧 执行命令: {command_type}")
            
            # 模拟命令执行
            time.sleep(2)  # 模拟执行时间
            
            # 发送执行结果
            result_data = {
                "robot_id": self.robot_id,
                "command_id": command_id,
                "result": "success",
                "message": f"命令 {command_type} 执行成功",
                "timestamp": time.time()
            }
            
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/execute_command/",
                json=result_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 命令执行结果已发送: {command_type}")
            else:
                print(f"❌ 命令执行结果发送失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 命令执行错误: {e}")
    
    def upload_qr_image(self, image_path=None):
        """上传二维码图片进行识别"""
        try:
            if image_path is None:
                # 模拟图片路径（实际应该是机器人拍照得到的图片）
                image_path = "test_qr_code.png"
                print(f"📸 使用模拟图片: {image_path}")
            
            # 检查图片文件是否存在
            import os
            if not os.path.exists(image_path):
                print(f"❌ 图片文件不存在: {image_path}")
                return False
            
            # 准备上传文件
            with open(image_path, 'rb') as f:
                files = {'qr_image': (os.path.basename(image_path), f, 'image/png')}
                
                response = requests.post(
                    f"{self.server_url}/api/robots/{self.robot_id}/upload_qr_image/",
                    files=files,
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📱 二维码图片识别成功: {result.get('message', '')}")
                print(f"🆔 订单ID: {result.get('order_id', 'N/A')}")
                print(f"👤 学生: {result.get('student_name', 'N/A')}")
                return True
            else:
                print(f"❌ 二维码图片识别失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 二维码图片上传错误: {e}")
            return False
    
    def run(self):
        """运行客户端"""
        print(f"🤖 机器人轮询客户端启动")
        print(f"📡 服务器地址: {self.server_url}")
        print(f"🤖 机器人ID: {self.robot_id}")
        print("=" * 50)
        
        self.running = True
        
        while self.running:
            try:
                # 发送心跳
                self.send_heartbeat()
                
                # 发送状态更新
                self.send_status_update()
                
                # 检查命令
                self.check_commands()
                
                # 随机上传二维码图片（模拟）
                if random.random() < 0.1:  # 10%概率
                    self.upload_qr_image()
                
                # 等待5秒
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n🛑 客户端停止")
                self.running = False
                break
            except Exception as e:
                print(f"❌ 运行错误: {e}")
                time.sleep(5)

def main():
    """主函数"""
    print("🤖 机器人轮询客户端")
    print("=" * 50)
    
    # 配置
    server_url = "http://localhost:8000"  # 修改为你的服务器地址
    robot_id = "1"  # 修改为你的机器人ID
    
    print(f"📡 服务器地址: {server_url}")
    print(f"🤖 机器人ID: {robot_id}")
    print("=" * 50)
    
    # 创建客户端
    client = RobotPollingClient(server_url, robot_id)
    
    # 运行客户端
    client.run()

if __name__ == "__main__":
    main() 