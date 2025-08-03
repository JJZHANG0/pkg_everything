#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 兼容旧版本websockets的WebSocket客户端
解决 'extra_headers' 参数错误问题
"""

import asyncio
import websockets
import json
import logging
import time
from typing import Optional, Dict, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class CompatibleRobotWebSocketClient:
    """兼容旧版本websockets的ROS小车WebSocket客户端"""
    
    def __init__(self, server_url: str, robot_id: int, token: str):
        """
        初始化WebSocket客户端
        
        Args:
            server_url: 服务器URL (例如: ws://localhost:8000)
            robot_id: 机器人ID
            token: JWT认证token
        """
        self.server_url = server_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.robot_id = robot_id
        self.token = token
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.running = False
        
        # 构建WebSocket URL（将token作为查询参数）
        params = urlencode({
            'token': token,
            'robot_id': robot_id
        })
        self.ws_url = f"{self.server_url}/ws/robot/{robot_id}/?{params}"
        
        # 回调函数
        self.on_command_received = None
        self.on_notification_received = None
        self.on_connected = None
        self.on_disconnected = None
    
    async def connect(self):
        """连接到WebSocket服务器（兼容旧版本）"""
        try:
            logger.info(f"正在连接到WebSocket服务器: {self.ws_url}")
            
            # 使用兼容的方式连接，不传递extra_headers
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            self.running = True
            
            logger.info("WebSocket连接成功")
            
            if self.on_connected:
                await self.on_connected()
            
            # 开始接收消息
            await self._receive_messages()
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """断开WebSocket连接"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.connected = False
        
        if self.on_disconnected:
            await self.on_disconnected()
        
        logger.info("WebSocket连接已断开")
    
    async def _receive_messages(self):
        """接收消息循环"""
        try:
            while self.running and self.websocket:
                message = await self.websocket.recv()
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket连接已关闭")
            self.connected = False
        except Exception as e:
            logger.error(f"接收消息时出错: {e}")
            self.connected = False
    
    async def _handle_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type', '')
            
            logger.info(f"收到消息: {message_type}")
            
            if message_type == 'command':
                await self._handle_command(data)
            elif message_type == 'notification':
                await self._handle_notification(data)
            elif message_type == 'connection_established':
                logger.info("WebSocket连接已建立")
            elif message_type == 'error':
                logger.error(f"服务器错误: {data.get('message', '')}")
            else:
                logger.warning(f"未知消息类型: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("消息格式错误")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    async def _handle_command(self, data: Dict[str, Any]):
        """处理指令消息"""
        command_id = data.get('command_id')
        command = data.get('command')
        command_data = data.get('data', {})
        
        logger.info(f"收到指令: {command} (ID: {command_id})")
        
        if self.on_command_received:
            await self.on_command_received(command_id, command, command_data)
    
    async def _handle_notification(self, data: Dict[str, Any]):
        """处理通知消息"""
        message = data.get('message', '')
        level = data.get('level', 'info')
        notification_data = data.get('data', {})
        
        logger.info(f"收到通知 [{level}]: {message}")
        
        if self.on_notification_received:
            await self.on_notification_received(message, level, notification_data)
    
    async def send_status_update(self, status_data: Dict[str, Any]):
        """发送状态更新"""
        if not self.connected or not self.websocket:
            logger.warning("WebSocket未连接，无法发送状态更新")
            return
        
        message = {
            'type': 'status_update',
            **status_data
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info("状态更新已发送")
        except Exception as e:
            logger.error(f"发送状态更新失败: {e}")
    
    async def send_command_result(self, command_id: int, result: str):
        """发送指令执行结果"""
        if not self.connected or not self.websocket:
            logger.warning("WebSocket未连接，无法发送指令结果")
            return
        
        message = {
            'type': 'command_result',
            'command_id': command_id,
            'result': result
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"指令结果已发送: {result}")
        except Exception as e:
            logger.error(f"发送指令结果失败: {e}")
    
    async def send_heartbeat(self):
        """发送心跳消息"""
        if not self.connected or not self.websocket:
            return
        
        message = {
            'type': 'heartbeat',
            'timestamp': time.time()
        }
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"发送心跳失败: {e}")
    
    async def start_heartbeat(self, interval: int = 30):
        """开始心跳循环"""
        while self.running and self.connected:
            await self.send_heartbeat()
            await asyncio.sleep(interval)

# 使用示例
async def example_usage():
    """使用示例"""
    
    # 配置参数
    SERVER_URL = "ws://192.168.110.148:8000"  # 替换为你的IP地址
    ROBOT_ID = 1
    TOKEN = "your_jwt_token_here"  # 需要先获取token
    
    # 创建客户端
    client = CompatibleRobotWebSocketClient(SERVER_URL, ROBOT_ID, TOKEN)
    
    # 设置回调函数
    async def on_command_received(command_id, command, data):
        """处理接收到的指令"""
        print(f"收到指令: {command} (ID: {command_id})")
        
        # 模拟执行指令
        if command == 'open_door':
            # 执行开门操作
            result = "door_open"  # 或 "door_closed" 取决于实际门状态
            await client.send_command_result(command_id, result)
        elif command == 'close_door':
            # 执行关门操作
            result = "door_closed"
            await client.send_command_result(command_id, result)
        elif command == 'start_delivery':
            # 开始配送
            await client.send_command_result(command_id, "delivery_started")
        elif command == 'stop_robot':
            # 停止机器人
            await client.send_command_result(command_id, "robot_stopped")
    
    async def on_notification_received(message, level, data):
        """处理接收到的通知"""
        print(f"收到通知 [{level}]: {message}")
    
    async def on_connected():
        """连接建立回调"""
        print("WebSocket连接已建立")
        
        # 发送初始状态
        await client.send_status_update({
            'status': 'IDLE',
            'battery': 85,
            'door_status': 'CLOSED',
            'location': {'x': 0, 'y': 0}
        })
    
    async def on_disconnected():
        """连接断开回调"""
        print("WebSocket连接已断开")
    
    # 设置回调
    client.on_command_received = on_command_received
    client.on_notification_received = on_notification_received
    client.on_connected = on_connected
    client.on_disconnected = on_disconnected
    
    try:
        # 连接并运行
        await client.connect()
        
        # 启动心跳
        heartbeat_task = asyncio.create_task(client.start_heartbeat())
        
        # 保持运行
        while client.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("正在关闭连接...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage()) 