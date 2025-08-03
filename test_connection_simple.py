#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 简单的WebSocket连接测试脚本
解决兼容性问题
"""

import asyncio
import websockets
import json
import requests

# 配置参数 - 请修改为你的实际IP地址
SERVER_IP = "192.168.110.148"  # 替换为你的IP地址
SERVER_PORT = 8000
ROBOT_ID = 1
USERNAME = "root"
PASSWORD = "test123456"

async def get_token():
    """获取JWT token"""
    try:
        response = requests.post(
            f"http://{SERVER_IP}:{SERVER_PORT}/api/token/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('access')
        else:
            print(f"❌ 获取token失败: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取token出错: {e}")
        return None

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔗 开始WebSocket连接测试...")
    
    # 获取token
    token = await get_token()
    if not token:
        print("❌ 无法获取认证token")
        return False
    
    print(f"✅ 获取token成功: {token[:20]}...")
    
    # 构建WebSocket URL
    ws_url = f"ws://{SERVER_IP}:{SERVER_PORT}/ws/robot/{ROBOT_ID}/?token={token}&robot_id={ROBOT_ID}"
    print(f"🔌 连接URL: {ws_url}")
    
    try:
        # 连接WebSocket
        print("📡 正在连接WebSocket...")
        websocket = await websockets.connect(ws_url)
        print("✅ WebSocket连接成功!")
        
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
            "timestamp": 1234567890
        }
        await websocket.send(json.dumps(heartbeat_message))
        
        # 等待心跳响应
        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        response_data = json.loads(response)
        print(f"📥 心跳响应: {response_data}")
        
        # 关闭连接
        await websocket.close()
        print("🔌 WebSocket连接已关闭")
        
        return True
        
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket连接关闭: {e}")
        return False
    except asyncio.TimeoutError:
        print("❌ 等待响应超时")
        return False
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 WebSocket连接测试")
    print("=" * 50)
    print(f"📡 服务器地址: {SERVER_IP}:{SERVER_PORT}")
    print(f"🤖 机器人ID: {ROBOT_ID}")
    print("=" * 50)
    
    success = await test_websocket_connection()
    
    if success:
        print("\n✅ 连接测试成功!")
        print("🎉 现在可以使用WebSocket进行实时通信了!")
    else:
        print("\n❌ 连接测试失败!")
        print("🔧 请检查网络连接和服务器状态")

if __name__ == "__main__":
    asyncio.run(main()) 