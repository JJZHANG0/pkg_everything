#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔌 简化WebSocket服务器
绕过Django问题，提供基本的WebSocket通信功能
"""

import asyncio
import websockets
import json
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websocket_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 存储连接的机器人
connected_robots = {}
# 存储命令队列
command_queue = {}

class SimpleWebSocketServer:
    """简化的WebSocket服务器"""
    
    def __init__(self):
        self.connected_robots = {}
        self.command_queue = {}
        self.logger = logging.getLogger(__name__)
    
    async def handle_robot_connection(self, websocket, path):
        """处理机器人连接"""
        try:
            # 解析路径获取机器人ID
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'robot':
                robot_id = path_parts[1]
            else:
                robot_id = 'unknown'
            
            self.logger.info(f"🤖 机器人 {robot_id} 尝试连接")
            
            # 存储连接
            self.connected_robots[robot_id] = {
                'websocket': websocket,
                'connected_at': datetime.now(),
                'last_heartbeat': datetime.now()
            }
            
            # 发送连接确认
            welcome_message = {
                "type": "connection_established",
                "robot_id": robot_id,
                "message": "连接成功",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(welcome_message))
            
            self.logger.info(f"✅ 机器人 {robot_id} 连接成功")
            
            # 处理消息
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(robot_id, data)
                except json.JSONDecodeError:
                    self.logger.error(f"❌ 无效的JSON格式: {message}")
                    error_response = {
                        "type": "error",
                        "message": "无效的JSON格式",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(error_response))
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🤖 机器人 {robot_id} 断开连接")
        except Exception as e:
            self.logger.error(f"❌ 处理连接时出错: {e}")
        finally:
            # 清理连接
            if robot_id in self.connected_robots:
                del self.connected_robots[robot_id]
                self.logger.info(f"🧹 清理机器人 {robot_id} 的连接")
    
    async def handle_message(self, robot_id, data):
        """处理接收到的消息"""
        message_type = data.get('type', 'unknown')
        
        self.logger.info(f"📥 收到机器人 {robot_id} 的消息: {message_type}")
        
        if message_type == 'heartbeat':
            await self.handle_heartbeat(robot_id, data)
        elif message_type == 'status_update':
            await self.handle_status_update(robot_id, data)
        elif message_type == 'command_result':
            await self.handle_command_result(robot_id, data)
        elif message_type == 'qr_scanned':
            await self.handle_qr_scanned(robot_id, data)
        else:
            # 发送确认消息
            ack_message = {
                "type": "ack",
                "message_id": data.get('message_id'),
                "message": "消息已收到",
                "timestamp": time.time()
            }
            await self.send_to_robot(robot_id, ack_message)
    
    async def handle_heartbeat(self, robot_id, data):
        """处理心跳消息"""
        if robot_id in self.connected_robots:
            self.connected_robots[robot_id]['last_heartbeat'] = datetime.now()
        
        # 发送心跳响应
        heartbeat_response = {
            "type": "heartbeat_ack",
            "robot_id": robot_id,
            "timestamp": time.time()
        }
        await self.send_to_robot(robot_id, heartbeat_response)
    
    async def handle_status_update(self, robot_id, data):
        """处理状态更新"""
        status_data = data.get('data', {})
        self.logger.info(f"📊 机器人 {robot_id} 状态更新: {status_data}")
        
        # 发送状态确认
        status_ack = {
            "type": "status_ack",
            "robot_id": robot_id,
            "timestamp": time.time()
        }
        await self.send_to_robot(robot_id, status_ack)
    
    async def handle_command_result(self, robot_id, data):
        """处理命令执行结果"""
        command_id = data.get('command_id')
        result = data.get('result')
        message = data.get('message', '')
        
        self.logger.info(f"🔧 机器人 {robot_id} 命令执行结果: {result} - {message}")
        
        # 发送结果确认
        result_ack = {
            "type": "command_result_ack",
            "command_id": command_id,
            "timestamp": time.time()
        }
        await self.send_to_robot(robot_id, result_ack)
    
    async def handle_qr_scanned(self, robot_id, data):
        """处理二维码扫描"""
        qr_data = data.get('qr_data', {})
        self.logger.info(f"📱 机器人 {robot_id} 扫描二维码: {qr_data}")
        
        # 发送扫描确认
        qr_ack = {
            "type": "qr_scan_ack",
            "robot_id": robot_id,
            "timestamp": time.time()
        }
        await self.send_to_robot(robot_id, qr_ack)
    
    async def send_to_robot(self, robot_id, message):
        """向机器人发送消息"""
        if robot_id in self.connected_robots:
            try:
                websocket = self.connected_robots[robot_id]['websocket']
                await websocket.send(json.dumps(message))
                self.logger.info(f"📤 向机器人 {robot_id} 发送消息: {message.get('type')}")
            except Exception as e:
                self.logger.error(f"❌ 向机器人 {robot_id} 发送消息失败: {e}")
        else:
            self.logger.warning(f"⚠️ 机器人 {robot_id} 未连接")
    
    async def send_command(self, robot_id, command_type, command_data=None):
        """向机器人发送命令"""
        command_message = {
            "type": "command",
            "command": command_type,
            "command_id": f"cmd_{int(time.time())}",
            "data": command_data or {},
            "timestamp": time.time()
        }
        await self.send_to_robot(robot_id, command_message)
    
    def get_connected_robots(self):
        """获取已连接的机器人列表"""
        return list(self.connected_robots.keys())
    
    def get_robot_status(self, robot_id):
        """获取机器人状态"""
        if robot_id in self.connected_robots:
            robot_info = self.connected_robots[robot_id]
            return {
                "connected": True,
                "connected_at": robot_info['connected_at'].isoformat(),
                "last_heartbeat": robot_info['last_heartbeat'].isoformat()
            }
        return {"connected": False}

# 创建服务器实例
server_instance = SimpleWebSocketServer()

async def main():
    """启动WebSocket服务器"""
    print("🚀 启动简化WebSocket服务器...")
    print("📡 监听端口: 8001")
    print("🔗 机器人连接地址: ws://localhost:8001/robot/{robot_id}")
    print("=" * 50)
    
    # 启动WebSocket服务器
    start_server = await websockets.serve(
        server_instance.handle_robot_connection, 
        "0.0.0.0", 
        8001
    )
    
    print("✅ WebSocket服务器启动成功")
    print("⏳ 等待机器人连接...")
    
    # 启动命令发送任务
    command_task = asyncio.create_task(command_sender_task())
    
    # 等待服务器运行
    await asyncio.gather(
        asyncio.Future(),  # 保持服务器运行
        command_task
    )

async def command_sender_task():
    """命令发送任务"""
    await asyncio.sleep(2)  # 等待服务器启动
    
    while True:
        try:
            # 显示已连接的机器人
            connected_robots = server_instance.get_connected_robots()
            
            if connected_robots:
                print(f"\n🤖 已连接的机器人: {connected_robots}")
                print("📋 可用命令:")
                print("  - open_door: 开门")
                print("  - close_door: 关门")
                print("  - start_delivery: 开始配送")
                print("  - stop_robot: 停止机器人")
                print("  - emergency_open_door: 紧急开门")
                print("  - 输入 'help' 查看帮助")
                print("  - 输入 'status' 查看机器人状态")
                print("  - 输入 'quit' 退出")
                
                # 获取用户输入
                try:
                    user_input = input("\n请输入命令 (格式: 机器人ID 命令): ").strip()
                    
                    if user_input.lower() == 'quit':
                        print("👋 退出命令发送")
                        break
                    elif user_input.lower() == 'help':
                        print_help()
                        continue
                    elif user_input.lower() == 'status':
                        for robot_id in connected_robots:
                            status = server_instance.get_robot_status(robot_id)
                            print(f"🤖 机器人 {robot_id}: {json.dumps(status, indent=2, ensure_ascii=False)}")
                        continue
                    elif user_input.lower() == '':
                        continue
                    
                    # 解析命令
                    parts = user_input.split()
                    if len(parts) >= 2:
                        robot_id = parts[0]
                        command = parts[1]
                        
                        if robot_id in connected_robots:
                            await server_instance.send_command(robot_id, command)
                            print(f"✅ 命令已发送: {command} -> 机器人 {robot_id}")
                        else:
                            print(f"❌ 机器人 {robot_id} 未连接")
                    else:
                        print("❌ 命令格式错误，请使用: 机器人ID 命令")
                        
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 退出命令发送")
                    break
            else:
                print("⏳ 等待机器人连接...")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"❌ 命令发送任务错误: {e}")
            await asyncio.sleep(1)

def print_help():
    """打印帮助信息"""
    print("\n📖 命令发送帮助:")
    print("格式: 机器人ID 命令")
    print("示例:")
    print("  1 open_door     # 向机器人1发送开门命令")
    print("  2 close_door    # 向机器人2发送关门命令")
    print("  1 start_delivery # 向机器人1发送开始配送命令")
    print("")
    print("可用命令:")
    print("  open_door           - 开门")
    print("  close_door          - 关门")
    print("  start_delivery      - 开始配送")
    print("  stop_robot          - 停止机器人")
    print("  emergency_open_door - 紧急开门")
    print("")
    print("特殊命令:")
    print("  help   - 显示此帮助")
    print("  status - 查看所有机器人状态")
    print("  quit   - 退出命令发送")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}") 