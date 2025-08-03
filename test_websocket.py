#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 WebSocket功能测试脚本
测试ROS小车WebSocket通信功能
"""

import asyncio
import websockets
import json
import time
import requests

# 配置参数
SERVER_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
ROBOT_ID = 1
USERNAME = "root"
PASSWORD = "test123456"

async def get_token():
    """获取JWT token"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/token/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('access')
        else:
            print(f"获取token失败: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"获取token出错: {e}")
        return None

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔗 测试WebSocket连接...")
    
    # 获取token
    token = await get_token()
    if not token:
        print("❌ 无法获取认证token")
        return
    
    print(f"✅ 获取token成功: {token[:20]}...")
    
    # 构建WebSocket URL
    params = f"token={token}&robot_id={ROBOT_ID}"
    ws_uri = f"{WS_URL}/ws/robot/{ROBOT_ID}/?{params}"
    
    try:
        print(f"🔌 连接到: {ws_uri}")
        websocket = await websockets.connect(ws_uri)
        print("✅ WebSocket连接成功")
        
        # 发送状态更新
        status_message = {
            "type": "status_update",
            "status": "IDLE",
            "battery": 85,
            "door_status": "CLOSED",
            "location": {"x": 10.5, "y": 20.3}
        }
        
        print("📤 发送状态更新...")
        await websocket.send(json.dumps(status_message))
        
        # 等待响应
        print("⏳ 等待服务器响应...")
        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        response_data = json.loads(response)
        print(f"📥 收到响应: {response_data}")
        
        # 发送心跳
        print("💓 发送心跳...")
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(heartbeat_message))
        
        # 等待心跳响应
        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        response_data = json.loads(response)
        print(f"📥 心跳响应: {response_data}")
        
        # 关闭连接
        await websocket.close()
        print("🔌 WebSocket连接已关闭")
        
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket连接关闭: {e}")
    except asyncio.TimeoutError:
        print("❌ 等待响应超时")
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")

async def test_command_sending():
    """测试指令发送"""
    print("\n🎮 测试指令发送...")
    
    # 获取token
    token = await get_token()
    if not token:
        print("❌ 无法获取认证token")
        return
    
    # 发送开门指令
    try:
        headers = {"Authorization": f"Bearer {token}"}
        command_data = {"action": "open_door"}
        
        response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/control/",
            json=command_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 指令发送成功: {result}")
        else:
            print(f"❌ 指令发送失败: {response.status_code} {response.text}")
            
    except Exception as e:
        print(f"❌ 指令发送出错: {e}")

async def main():
    """主函数"""
    print("🚀 开始WebSocket功能测试")
    print("=" * 50)
    
    # 测试WebSocket连接
    await test_websocket_connection()
    
    # 测试指令发送
    await test_command_sending()
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 