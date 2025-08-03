#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 简单的WebSocket连接测试
模拟同事的环境，测试连接是否正常
"""

import asyncio
import websockets
import json
import requests
from urllib.parse import urlencode

# 配置参数
SERVER_URL = 'http://localhost:8000/api'
ROBOT_ID = 1
USERNAME = 'root'
PASSWORD = 'test123456'

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔗 开始WebSocket连接测试...")
    
    # 获取token
    try:
        response = requests.post(
            f"{SERVER_URL}/token/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            token = response.json().get('access')
            print(f"✅ 获取token成功: {token[:20]}...")
        else:
            print(f"❌ 获取token失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取token出错: {e}")
        return False
    
    # 构建WebSocket URL（兼容旧版本websockets）
    params = urlencode({
        'token': token,
        'robot_id': ROBOT_ID
    })
    ws_url = f"ws://localhost:8000/ws/robot/{ROBOT_ID}/?{params}"
    
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
    print(f"📡 服务器地址: localhost:8000")
    print(f"🤖 机器人ID: {ROBOT_ID}")
    print("=" * 50)
    
    success = await test_websocket_connection()
    
    if success:
        print("\n✅ 连接测试成功!")
        print("🎉 现在可以使用WebSocket进行实时通信了!")
        print("\n📋 给同事的说明:")
        print("1. 使用我提供的 '同事代码适配版本.py'")
        print("2. 确保IP地址是: 192.168.110.148:8000")
        print("3. 直接运行即可，无需额外配置")
    else:
        print("\n❌ 连接测试失败!")
        print("🔧 请检查网络连接和服务器状态")

if __name__ == "__main__":
    asyncio.run(main()) 