#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 机器人WebSocket测试客户端
供同事测试WebSocket连接使用
"""

import asyncio
import websockets
import json
import time
import random
from datetime import datetime

class RobotTestClient:
    """机器人测试客户端"""
    
    def __init__(self, server_url, robot_id):
        self.server_url = server_url
        self.robot_id = robot_id
        self.websocket = None
        self.running = False
        
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            print(f"🔌 连接到服务器: {self.server_url}")
            self.websocket = await websockets.connect(self.server_url)
            print("✅ 连接成功")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def send_heartbeat(self):
        """发送心跳消息"""
        heartbeat = {
            "type": "heartbeat",
            "robot_id": self.robot_id,
            "timestamp": time.time(),
            "status": "online"
        }
        await self.websocket.send(json.dumps(heartbeat))
        print(f"💓 发送心跳: {self.robot_id}")
    
    async def send_status_update(self):
        """发送状态更新"""
        status_data = {
            "type": "status_update",
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
        await self.websocket.send(json.dumps(status_data))
        print(f"📊 发送状态更新: {status_data['data']}")
    
    async def send_qr_scanned(self, qr_data=None):
        """发送二维码扫描结果"""
        if qr_data is None:
            qr_data = {
                "order_id": f"order_{random.randint(1000, 9999)}",
                "qr_content": f"qr_content_{random.randint(100, 999)}",
                "scan_time": datetime.now().isoformat()
            }
        
        qr_message = {
            "type": "qr_scanned",
            "robot_id": self.robot_id,
            "qr_data": qr_data,
            "timestamp": time.time()
        }
        await self.websocket.send(json.dumps(qr_message))
        print(f"📱 发送二维码扫描: {qr_data}")
    
    async def send_command_result(self, command_id, result="success", message="命令执行成功"):
        """发送命令执行结果"""
        result_data = {
            "type": "command_result",
            "robot_id": self.robot_id,
            "command_id": command_id,
            "result": result,
            "message": message,
            "timestamp": time.time()
        }
        await self.websocket.send(json.dumps(result_data))
        print(f"🔧 发送命令结果: {result} - {message}")
    
    async def handle_message(self, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type', 'unknown')
            
            print(f"📥 收到消息: {message_type}")
            
            if message_type == 'connection_established':
                print(f"✅ 连接确认: {data.get('message')}")
                
            elif message_type == 'heartbeat_ack':
                print(f"💓 心跳确认")
                
            elif message_type == 'status_ack':
                print(f"📊 状态确认")
                
            elif message_type == 'command':
                command = data.get('command')
                command_id = data.get('command_id')
                print(f"🔧 收到命令: {command}")
                
                # 模拟命令执行
                await asyncio.sleep(2)  # 模拟执行时间
                
                # 发送执行结果
                if command == 'open_door':
                    await self.send_command_result(command_id, "success", "门已打开")
                elif command == 'close_door':
                    await self.send_command_result(command_id, "success", "门已关闭")
                elif command == 'start_delivery':
                    await self.send_command_result(command_id, "success", "开始配送")
                elif command == 'stop_robot':
                    await self.send_command_result(command_id, "success", "机器人已停止")
                else:
                    await self.send_command_result(command_id, "success", f"命令 {command} 执行成功")
                    
            elif message_type == 'error':
                print(f"❌ 错误消息: {data.get('message')}")
                
            else:
                print(f"📄 其他消息: {data}")
                
        except json.JSONDecodeError:
            print(f"❌ 无效的JSON格式: {message}")
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")
    
    async def run(self):
        """运行客户端"""
        if not await self.connect():
            return
        
        self.running = True
        print("🤖 机器人客户端启动")
        
        try:
            # 启动消息监听
            async def listen_messages():
                async for message in self.websocket:
                    await self.handle_message(message)
            
            # 启动定期任务
            async def periodic_tasks():
                heartbeat_count = 0
                status_count = 0
                
                while self.running:
                    try:
                        # 每30秒发送一次心跳
                        if heartbeat_count % 30 == 0:
                            await self.send_heartbeat()
                        
                        # 每60秒发送一次状态更新
                        if status_count % 60 == 0:
                            await self.send_status_update()
                        
                        heartbeat_count += 1
                        status_count += 1
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"❌ 定期任务出错: {e}")
                        break
            
            # 并发运行监听和定期任务
            await asyncio.gather(
                listen_messages(),
                periodic_tasks()
            )
            
        except websockets.exceptions.ConnectionClosed:
            print("🔌 连接已关闭")
        except Exception as e:
            print(f"❌ 客户端运行出错: {e}")
        finally:
            self.running = False
            if self.websocket:
                await self.websocket.close()
            print("🛑 客户端已停止")

async def main():
    """主函数"""
    print("🤖 机器人WebSocket测试客户端")
    print("=" * 50)
    
    # 配置连接参数
    server_url = "ws://localhost:8001/robot/1"  # 同事需要修改为实际的服务器地址
    robot_id = "1"
    
    print(f"📡 服务器地址: {server_url}")
    print(f"🤖 机器人ID: {robot_id}")
    print("=" * 50)
    
    # 创建并运行客户端
    client = RobotTestClient(server_url, robot_id)
    await client.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 客户端已停止")
    except Exception as e:
        print(f"❌ 客户端启动失败: {e}") 