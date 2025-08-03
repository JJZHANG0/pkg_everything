#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 模拟同事机器人的WebSocket连接测试
测试我们的WebSocket系统是否正常工作
"""

import asyncio
import websockets
import json
import requests
import time
from urllib.parse import urlencode

# 配置参数
SERVER_URL = 'http://localhost:8000/api'
ROBOT_ID = 1
USERNAME = 'root'
PASSWORD = 'test123456'

class MockRobotClient:
    """模拟机器人客户端"""
    
    def __init__(self):
        self.token = None
        self.websocket = None
        self.connected = False
        self.running = False
        
    async def get_token(self):
        """获取JWT token"""
        try:
            response = requests.post(
                f"{SERVER_URL}/token/",
                json={"username": USERNAME, "password": PASSWORD},
                timeout=5
            )
            if response.status_code == 200:
                self.token = response.json().get('access')
                print(f"✅ 获取token成功: {self.token[:20]}...")
                return True
            else:
                print(f"❌ 获取token失败: {response.status_code} {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取token出错: {e}")
            return False
    
    async def connect_websocket(self):
        """连接WebSocket"""
        if not self.token:
            if not await self.get_token():
                return False
        
        # 构建WebSocket URL（兼容旧版本websockets）
        params = urlencode({
            'token': self.token,
            'robot_id': ROBOT_ID
        })
        ws_url = f"ws://localhost:8000/ws/robot/{ROBOT_ID}/?{params}"
        
        print(f"🔌 连接WebSocket: {ws_url}")
        
        try:
            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            self.running = True
            print("✅ WebSocket连接成功!")
            return True
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            return False
    
    async def send_status_update(self, status_data):
        """发送状态更新"""
        if not self.connected or not self.websocket:
            return
        
        message = {
            'type': 'status_update',
            **status_data
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 状态更新已发送: {status_data['status']}")
        except Exception as e:
            print(f"❌ 发送状态更新失败: {e}")
    
    async def send_command_result(self, command_id, result):
        """发送指令执行结果"""
        if not self.connected or not self.websocket:
            return
        
        message = {
            'type': 'command_result',
            'command_id': command_id,
            'result': result
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 指令结果已发送: {result}")
        except Exception as e:
            print(f"❌ 发送指令结果失败: {e}")
    
    async def handle_command(self, command_data):
        """处理接收到的指令"""
        command = command_data.get('command')
        command_id = command_data.get('command_id')
        param = command_data.get('param')
        
        print(f"📥 收到指令: {command} (ID: {command_id})")
        
        # 模拟执行指令
        if command == 'open_door':
            print("🚪 执行开门操作...")
            await asyncio.sleep(1)  # 模拟执行时间
            await self.send_command_result(command_id, "door_open")
            
        elif command == 'close_door':
            print("🚪 执行关门操作...")
            await asyncio.sleep(1)  # 模拟执行时间
            await self.send_command_result(command_id, "door_closed")
            
        elif command == 'start_delivery':
            print("🚚 开始配送...")
            await asyncio.sleep(1)  # 模拟执行时间
            await self.send_command_result(command_id, "delivery_started")
            
        elif command == 'stop_robot':
            print("🛑 停止机器人...")
            await asyncio.sleep(1)  # 模拟执行时间
            await self.send_command_result(command_id, "robot_stopped")
            
        elif command == 'emergency_open_door':
            print("🚨 紧急开门!")
            await asyncio.sleep(0.5)  # 模拟执行时间
            await self.send_command_result(command_id, "door_open")
            
        elif command == 'upload_qr':
            print("📷 上传二维码图片...")
            await asyncio.sleep(2)  # 模拟拍照和上传时间
            await self.send_command_result(command_id, "qr_upload_success")
            
        elif command == 'navigate':
            print(f"🧭 导航到: {param}")
            await asyncio.sleep(1)  # 模拟执行时间
            await self.send_command_result(command_id, "navigation_started")
            
        else:
            print(f"❓ 未知指令: {command}")
            await self.send_command_result(command_id, "unknown_command")
    
    async def receive_messages(self):
        """接收消息循环"""
        try:
            while self.running and self.websocket:
                message = await self.websocket.recv()
                print(f"📥 收到消息: {message}")
                
                try:
                    data = json.loads(message)
                    message_type = data.get('type', '')
                    
                    if message_type == 'command':
                        await self.handle_command(data)
                    elif message_type == 'notification':
                        print(f"📢 通知: {data.get('message', '')}")
                    elif message_type == 'connection_established':
                        print("🔗 WebSocket连接已建立")
                    elif message_type == 'error':
                        print(f"❌ 服务器错误: {data.get('message', '')}")
                    else:
                        print(f"📋 其他消息: {message_type}")
                        
                except json.JSONDecodeError:
                    print("❌ 消息格式错误")
                except Exception as e:
                    print(f"❌ 处理消息失败: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket连接已关闭")
            self.connected = False
        except Exception as e:
            print(f"❌ 接收消息出错: {e}")
            self.connected = False
    
    async def send_heartbeat(self):
        """发送心跳"""
        if not self.connected or not self.websocket:
            return
        
        message = {
            'type': 'heartbeat',
            'timestamp': time.time()
        }
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            print(f"❌ 发送心跳失败: {e}")
    
    async def start_heartbeat(self, interval=30):
        """开始心跳循环"""
        while self.running and self.connected:
            await self.send_heartbeat()
            await asyncio.sleep(interval)
    
    async def run(self):
        """运行机器人客户端"""
        print("🤖 启动模拟机器人客户端...")
        
        # 连接WebSocket
        if not await self.connect_websocket():
            print("❌ 无法连接WebSocket，退出")
            return
        
        # 发送初始状态
        await self.send_status_update({
            'status': 'IDLE',
            'battery': 85,
            'door_status': 'CLOSED',
            'location': {'x': 10.5, 'y': 20.3}
        })
        
        # 启动心跳
        heartbeat_task = asyncio.create_task(self.start_heartbeat())
        
        # 开始接收消息
        await self.receive_messages()
        
        # 清理
        heartbeat_task.cancel()
        if self.websocket:
            await self.websocket.close()
        
        print("🔚 模拟机器人客户端已停止")

async def main():
    """主函数"""
    print("🚀 WebSocket连接测试")
    print("=" * 50)
    print("📡 服务器地址: localhost:8000")
    print(f"🤖 机器人ID: {ROBOT_ID}")
    print("=" * 50)
    
    robot = MockRobotClient()
    
    try:
        await robot.run()
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断，正在停止...")
        robot.running = False
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 