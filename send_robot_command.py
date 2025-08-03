#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 机器人命令发送工具
向连接的机器人发送控制命令
"""

import asyncio
import json
import time
from datetime import datetime

class RobotCommandSender:
    """机器人命令发送器"""
    
    def __init__(self, server_instance):
        self.server = server_instance
    
    async def send_command(self, robot_id, command_type, command_data=None):
        """发送命令到指定机器人"""
        try:
            await self.server.send_command(robot_id, command_type, command_data)
            print(f"✅ 命令已发送: {command_type} -> 机器人 {robot_id}")
            return True
        except Exception as e:
            print(f"❌ 发送命令失败: {e}")
            return False
    
    def get_connected_robots(self):
        """获取已连接的机器人列表"""
        return self.server.get_connected_robots()
    
    def get_robot_status(self, robot_id):
        """获取机器人状态"""
        return self.server.get_robot_status(robot_id)

async def interactive_command_sender(server_instance):
    """交互式命令发送器"""
    sender = RobotCommandSender(server_instance)
    
    print("🔧 机器人命令发送工具")
    print("=" * 50)
    
    while True:
        try:
            # 显示已连接的机器人
            connected_robots = sender.get_connected_robots()
            if not connected_robots:
                print("⚠️ 当前没有机器人连接")
                print("⏳ 等待机器人连接...")
                await asyncio.sleep(5)
                continue
            
            print(f"\n🤖 已连接的机器人: {connected_robots}")
            
            # 显示菜单
            print("\n📋 可用命令:")
            print("1. open_door - 开门")
            print("2. close_door - 关门")
            print("3. start_delivery - 开始配送")
            print("4. stop_robot - 停止机器人")
            print("5. emergency_open_door - 紧急开门")
            print("6. 查看机器人状态")
            print("7. 刷新连接列表")
            print("0. 退出")
            
            # 获取用户输入
            choice = input("\n请选择命令 (0-7): ").strip()
            
            if choice == "0":
                print("👋 退出命令发送工具")
                break
            elif choice == "6":
                # 查看机器人状态
                robot_id = input("请输入机器人ID: ").strip()
                status = sender.get_robot_status(robot_id)
                print(f"🤖 机器人 {robot_id} 状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
            elif choice == "7":
                # 刷新连接列表
                print("🔄 刷新连接列表...")
                continue
            elif choice in ["1", "2", "3", "4", "5"]:
                # 发送命令
                command_map = {
                    "1": "open_door",
                    "2": "close_door", 
                    "3": "start_delivery",
                    "4": "stop_robot",
                    "5": "emergency_open_door"
                }
                
                command = command_map[choice]
                
                # 选择机器人
                if len(connected_robots) == 1:
                    robot_id = connected_robots[0]
                    print(f"🤖 自动选择机器人: {robot_id}")
                else:
                    print(f"🤖 请选择机器人: {connected_robots}")
                    robot_id = input("请输入机器人ID: ").strip()
                
                if robot_id not in connected_robots:
                    print(f"❌ 机器人 {robot_id} 未连接")
                    continue
                
                # 发送命令
                success = await sender.send_command(robot_id, command)
                if success:
                    print(f"✅ 命令 '{command}' 已发送到机器人 {robot_id}")
                else:
                    print(f"❌ 命令发送失败")
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 退出命令发送工具")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

async def batch_command_sender(server_instance):
    """批量命令发送器"""
    sender = RobotCommandSender(server_instance)
    
    print("🔧 批量命令发送工具")
    print("=" * 50)
    
    # 预定义的命令序列
    command_sequences = {
        "1": [
            ("open_door", "开门"),
            ("start_delivery", "开始配送"),
            ("stop_robot", "停止机器人"),
            ("close_door", "关门")
        ],
        "2": [
            ("emergency_open_door", "紧急开门"),
            ("stop_robot", "停止机器人")
        ],
        "3": [
            ("open_door", "开门"),
            ("close_door", "关门")
        ]
    }
    
    print("📋 预定义命令序列:")
    print("1. 完整配送流程")
    print("2. 紧急停止流程")
    print("3. 开关门测试")
    
    choice = input("请选择命令序列 (1-3): ").strip()
    
    if choice not in command_sequences:
        print("❌ 无效选择")
        return
    
    # 获取机器人ID
    connected_robots = sender.get_connected_robots()
    if not connected_robots:
        print("❌ 没有机器人连接")
        return
    
    robot_id = connected_robots[0] if len(connected_robots) == 1 else input("请输入机器人ID: ").strip()
    
    if robot_id not in connected_robots:
        print(f"❌ 机器人 {robot_id} 未连接")
        return
    
    # 执行命令序列
    sequence = command_sequences[choice]
    print(f"🚀 开始执行命令序列到机器人 {robot_id}")
    
    for i, (command, description) in enumerate(sequence, 1):
        print(f"\n{i}. 执行: {description} ({command})")
        
        success = await sender.send_command(robot_id, command)
        if success:
            print(f"   ✅ 成功")
        else:
            print(f"   ❌ 失败")
        
        # 等待一段时间再执行下一个命令
        if i < len(sequence):
            print(f"   ⏳ 等待3秒...")
            await asyncio.sleep(3)
    
    print(f"\n✅ 命令序列执行完成")

def create_command_sender(server_instance):
    """创建命令发送器"""
    print("🔧 机器人命令发送工具")
    print("=" * 50)
    print("1. 交互式命令发送")
    print("2. 批量命令发送")
    print("0. 退出")
    
    choice = input("请选择模式 (0-2): ").strip()
    
    if choice == "1":
        asyncio.run(interactive_command_sender(server_instance))
    elif choice == "2":
        asyncio.run(batch_command_sender(server_instance))
    elif choice == "0":
        print("👋 退出")
    else:
        print("❌ 无效选择")

# 如果直接运行此文件
if __name__ == "__main__":
    print("🔧 机器人命令发送工具")
    print("注意: 此工具需要与WebSocket服务器一起运行")
    print("请确保WebSocket服务器已启动")
    print("=" * 50)
    
    # 这里需要从simple_websocket_server.py导入server_instance
    print("请从simple_websocket_server.py中导入server_instance来使用此工具") 