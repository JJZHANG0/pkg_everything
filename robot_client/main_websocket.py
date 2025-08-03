#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ROS小车WebSocket版本主程序
使用WebSocket替代轮询进行实时通信
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any
from websocket_client import RobotWebSocketClient
from network.api_client import APIClient
from utils.logger import setup_logger

# 设置日志
setup_logger()
logger = logging.getLogger(__name__)

# 配置参数
SERVER_URL = "http://localhost:8000"
ROBOT_ID = 1
USERNAME = "root"
PASSWORD = "test123456"

class RobotWebSocketController:
    """ROS小车WebSocket控制器"""
    
    def __init__(self):
        self.api_client = APIClient(SERVER_URL, USERNAME, PASSWORD)
        self.ws_client = None
        self.token = None
        self.running = False
        
        # 机器人状态
        self.robot_status = {
            'status': 'IDLE',
            'battery': 85,
            'door_status': 'CLOSED',
            'location': {'x': 0, 'y': 0}
        }
    
    async def initialize(self):
        """初始化连接"""
        try:
            # 获取认证token
            self.token = await self.api_client.get_token()
            if not self.token:
                logger.error("获取认证token失败")
                return False
            
            # 创建WebSocket客户端
            self.ws_client = RobotWebSocketClient(
                SERVER_URL, 
                ROBOT_ID, 
                self.token
            )
            
            # 设置回调函数
            self.ws_client.on_command_received = self.handle_command
            self.ws_client.on_notification_received = self.handle_notification
            self.ws_client.on_connected = self.on_connected
            self.ws_client.on_disconnected = self.on_disconnected
            
            return True
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    async def start(self):
        """启动WebSocket通信"""
        if not await self.initialize():
            return
        
        self.running = True
        
        try:
            # 连接到WebSocket服务器
            await self.ws_client.connect()
            
            # 启动心跳
            heartbeat_task = asyncio.create_task(self.ws_client.start_heartbeat())
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭...")
        except Exception as e:
            logger.error(f"运行出错: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止WebSocket通信"""
        self.running = False
        if self.ws_client:
            await self.ws_client.disconnect()
    
    async def handle_command(self, command_id: int, command: str, data: Dict[str, Any]):
        """处理接收到的指令"""
        logger.info(f"收到指令: {command} (ID: {command_id})")
        
        try:
            if command == 'open_door':
                await self.execute_open_door(command_id)
            elif command == 'close_door':
                await self.execute_close_door(command_id)
            elif command == 'start_delivery':
                await self.execute_start_delivery(command_id, data)
            elif command == 'stop_robot':
                await self.execute_stop_robot(command_id)
            elif command == 'emergency_open_door':
                await self.execute_emergency_open_door(command_id)
            else:
                logger.warning(f"未知指令: {command}")
                await self.ws_client.send_command_result(command_id, "unknown_command")
                
        except Exception as e:
            logger.error(f"执行指令失败: {e}")
            await self.ws_client.send_command_result(command_id, f"error: {str(e)}")
    
    async def handle_notification(self, message: str, level: str, data: Dict[str, Any]):
        """处理接收到的通知"""
        logger.info(f"收到通知 [{level}]: {message}")
        # 这里可以添加通知处理逻辑，比如显示在GUI上
    
    async def on_connected(self):
        """连接建立回调"""
        logger.info("WebSocket连接已建立")
        
        # 发送初始状态
        await self.ws_client.send_status_update(self.robot_status)
    
    async def on_disconnected(self):
        """连接断开回调"""
        logger.info("WebSocket连接已断开")
    
    async def execute_open_door(self, command_id: int):
        """执行开门指令"""
        logger.info("执行开门指令")
        
        try:
            # 这里应该调用实际的硬件控制代码
            # 例如: await self.hardware_controller.open_door()
            
            # 模拟硬件操作
            await asyncio.sleep(2)  # 模拟开门时间
            
            # 检查门是否真的打开了（这里应该从硬件获取真实状态）
            door_opened = True  # 假设门成功打开
            
            if door_opened:
                self.robot_status['door_status'] = 'OPEN'
                result = "door_open"
                logger.info("门已成功打开")
            else:
                result = "door_closed"
                logger.warning("门打开失败")
            
            # 发送执行结果
            await self.ws_client.send_command_result(command_id, result)
            
            # 更新状态
            await self.ws_client.send_status_update(self.robot_status)
            
        except Exception as e:
            logger.error(f"开门失败: {e}")
            await self.ws_client.send_command_result(command_id, f"error: {str(e)}")
    
    async def execute_close_door(self, command_id: int):
        """执行关门指令"""
        logger.info("执行关门指令")
        
        try:
            # 这里应该调用实际的硬件控制代码
            # 例如: await self.hardware_controller.close_door()
            
            # 模拟硬件操作
            await asyncio.sleep(2)  # 模拟关门时间
            
            # 检查门是否真的关闭了（这里应该从硬件获取真实状态）
            door_closed = True  # 假设门成功关闭
            
            if door_closed:
                self.robot_status['door_status'] = 'CLOSED'
                result = "door_closed"
                logger.info("门已成功关闭")
            else:
                result = "door_open"
                logger.warning("门关闭失败")
            
            # 发送执行结果
            await self.ws_client.send_command_result(command_id, result)
            
            # 更新状态
            await self.ws_client.send_status_update(self.robot_status)
            
        except Exception as e:
            logger.error(f"关门失败: {e}")
            await self.ws_client.send_command_result(command_id, f"error: {str(e)}")
    
    async def execute_start_delivery(self, command_id: int, data: Dict[str, Any]):
        """执行开始配送指令"""
        logger.info("执行开始配送指令")
        
        try:
            # 更新机器人状态
            self.robot_status['status'] = 'DELIVERING'
            
            # 这里应该调用实际的导航代码
            # 例如: await self.navigation_controller.start_delivery(data.get('target'))
            
            # 模拟配送过程
            target = data.get('target', {})
            logger.info(f"开始配送到目标: {target}")
            
            # 发送执行结果
            await self.ws_client.send_command_result(command_id, "delivery_started")
            
            # 更新状态
            await self.ws_client.send_status_update(self.robot_status)
            
        except Exception as e:
            logger.error(f"开始配送失败: {e}")
            await self.ws_client.send_command_result(command_id, f"error: {str(e)}")
    
    async def execute_stop_robot(self, command_id: int):
        """执行停止机器人指令"""
        logger.info("执行停止机器人指令")
        
        try:
            # 更新机器人状态
            self.robot_status['status'] = 'IDLE'
            
            # 这里应该调用实际的停止代码
            # 例如: await self.navigation_controller.stop()
            
            logger.info("机器人已停止")
            
            # 发送执行结果
            await self.ws_client.send_command_result(command_id, "robot_stopped")
            
            # 更新状态
            await self.ws_client.send_status_update(self.robot_status)
            
        except Exception as e:
            logger.error(f"停止机器人失败: {e}")
            await self.ws_client.send_command_result(command_id, f"error: {str(e)}")
    
    async def execute_emergency_open_door(self, command_id: int):
        """执行紧急开门指令"""
        logger.info("执行紧急开门指令")
        
        try:
            # 紧急开门逻辑
            await self.execute_open_door(command_id)
            
        except Exception as e:
            logger.error(f"紧急开门失败: {e}")
            await self.ws_client.send_command_result(command_id, f"error: {str(e)}")
    
    async def update_status_periodically(self, interval: int = 60):
        """定期更新状态"""
        while self.running:
            try:
                # 更新电池状态（模拟）
                self.robot_status['battery'] = max(0, self.robot_status['battery'] - 1)
                
                # 更新位置（模拟）
                # 这里应该从实际的定位系统获取位置
                
                # 发送状态更新
                if self.ws_client and self.ws_client.connected:
                    await self.ws_client.send_status_update(self.robot_status)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"更新状态失败: {e}")
                await asyncio.sleep(interval)
    
    async def simulate_qr_scan(self, order_id: int):
        """模拟二维码扫描"""
        try:
            # 模拟扫描二维码
            qr_data = {
                'order_id': order_id,
                'scanned_at': time.time(),
                'location': self.robot_status['location']
            }
            
            # 发送二维码扫描结果
            await self.ws_client.send_qr_scanned(order_id, qr_data)
            
            logger.info(f"模拟扫描订单 {order_id} 的二维码")
            
        except Exception as e:
            logger.error(f"模拟二维码扫描失败: {e}")

async def main():
    """主函数"""
    logger.info("启动ROS小车WebSocket控制器")
    
    controller = RobotWebSocketController()
    
    try:
        # 启动状态更新任务
        status_task = asyncio.create_task(controller.update_status_periodically())
        
        # 启动主控制器
        await controller.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"主程序出错: {e}")
    finally:
        await controller.stop()
        logger.info("ROS小车WebSocket控制器已停止")

if __name__ == "__main__":
    asyncio.run(main()) 