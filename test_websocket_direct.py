#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔌 直接WebSocket连接测试
绕过登录问题，直接测试WebSocket连接
"""

import asyncio
import websockets
import json
import time

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔌 开始测试WebSocket连接...")
    
    # WebSocket连接URL
    ws_url = "ws://localhost:8000/ws/robot/1/"
    
    try:
        print(f"📡 连接到: {ws_url}")
        
        # 建立WebSocket连接
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket连接成功！")
            
            # 发送测试消息
            test_message = {
                "type": "heartbeat",
                "data": {
                    "robot_id": "1",
                    "timestamp": time.time(),
                    "status": "online"
                }
            }
            
            print(f"📤 发送消息: {json.dumps(test_message, ensure_ascii=False)}")
            await websocket.send(json.dumps(test_message))
            
            # 等待响应
            print("⏳ 等待响应...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 收到响应: {response}")
            
            # 保持连接一段时间
            print("🔄 保持连接10秒...")
            await asyncio.sleep(10)
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket连接被拒绝 - 后端服务可能未启动")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket连接失败 - 状态码: {e.status_code}")
    except asyncio.TimeoutError:
        print("❌ 等待响应超时")
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")

async def test_websocket_monitor():
    """测试WebSocket监控连接"""
    print("\n🔍 测试WebSocket监控连接...")
    
    # WebSocket监控URL
    ws_url = "ws://localhost:8000/ws/monitor/"
    
    try:
        print(f"📡 连接到监控: {ws_url}")
        
        # 建立WebSocket连接
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket监控连接成功！")
            
            # 等待监控数据
            print("⏳ 等待监控数据...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 收到监控数据: {response}")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket监控连接被拒绝")
    except Exception as e:
        print(f"❌ WebSocket监控测试失败: {e}")

async def main():
    """主函数"""
    print("🚀 WebSocket直接连接测试")
    print("=" * 50)
    
    # 测试机器人WebSocket连接
    await test_websocket_connection()
    
    # 测试监控WebSocket连接
    await test_websocket_monitor()
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 