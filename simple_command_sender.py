#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 简单命令发送工具
直接向WebSocket服务器发送命令
"""

import asyncio
import websockets
import json
import time
import sys

async def send_command_to_server(server_url, robot_id, command):
    """向服务器发送命令"""
    try:
        # 连接到服务器的命令端点
        command_url = f"ws://localhost:8001/command"
        
        async with websockets.connect(command_url) as websocket:
            print(f"🔌 连接到命令服务器: {command_url}")
            
            # 发送命令
            command_message = {
                "type": "send_command",
                "target_robot": robot_id,
                "command": command,
                "timestamp": time.time()
            }
            
            print(f"📤 发送命令: {command} -> 机器人 {robot_id}")
            await websocket.send(json.dumps(command_message))
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 收到响应: {response}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时")
                
    except Exception as e:
        print(f"❌ 发送命令失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("🔧 简单命令发送工具")
        print("=" * 50)
        print("用法: python3 simple_command_sender.py <机器人ID> <命令>")
        print("")
        print("示例:")
        print("  python3 simple_command_sender.py 1 open_door")
        print("  python3 simple_command_sender.py 1 close_door")
        print("  python3 simple_command_sender.py 1 start_delivery")
        print("")
        print("可用命令:")
        print("  open_door           - 开门")
        print("  close_door          - 关门")
        print("  start_delivery      - 开始配送")
        print("  stop_robot          - 停止机器人")
        print("  emergency_open_door - 紧急开门")
        return
    
    robot_id = sys.argv[1]
    command = sys.argv[2]
    
    # 验证命令
    valid_commands = [
        "open_door", "close_door", "start_delivery", 
        "stop_robot", "emergency_open_door"
    ]
    
    if command not in valid_commands:
        print(f"❌ 无效命令: {command}")
        print(f"可用命令: {', '.join(valid_commands)}")
        return
    
    # 发送命令
    print(f"🚀 发送命令: {command} -> 机器人 {robot_id}")
    asyncio.run(send_command_to_server("ws://localhost:8001", robot_id, command))

if __name__ == "__main__":
    main() 