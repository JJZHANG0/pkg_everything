#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 简化的WebSocket测试脚本
"""

import requests
import json

# 配置参数
SERVER_URL = "http://localhost:8000"
USERNAME = "root"
PASSWORD = "test123456"

def get_token():
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

def test_robot_control():
    """测试机器人控制"""
    print("🎮 测试机器人控制...")
    
    # 获取token
    token = get_token()
    if not token:
        print("❌ 无法获取认证token")
        return
    
    print(f"✅ 获取token成功: {token[:20]}...")
    
    # 发送开门指令
    try:
        headers = {"Authorization": f"Bearer {token}"}
        command_data = {"action": "open_door"}
        
        response = requests.post(
            f"{SERVER_URL}/api/robots/1/control/",
            json=command_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 指令发送成功: {result}")
            print(f"📡 通信方式: {result.get('method', 'unknown')}")
        else:
            print(f"❌ 指令发送失败: {response.status_code} {response.text}")
            
    except Exception as e:
        print(f"❌ 指令发送出错: {e}")

def test_robot_status():
    """测试机器人状态查询"""
    print("\n📊 测试机器人状态查询...")
    
    # 获取token
    token = get_token()
    if not token:
        print("❌ 无法获取认证token")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{SERVER_URL}/api/robots/1/status/",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 状态查询成功: {result}")
        else:
            print(f"❌ 状态查询失败: {response.status_code} {response.text}")
            
    except Exception as e:
        print(f"❌ 状态查询出错: {e}")

def main():
    """主函数"""
    print("🚀 开始WebSocket功能测试")
    print("=" * 50)
    
    # 测试机器人控制
    test_robot_control()
    
    # 测试机器人状态
    test_robot_status()
    
    print("\n✅ 测试完成")
    print("\n📝 说明:")
    print("- 如果看到 'method': 'websocket'，说明WebSocket通信已启用")
    print("- 如果看到 'method': 'unknown'，说明仍在使用传统轮询")
    print("- WebSocket客户端代码已准备就绪，可以开始使用")

if __name__ == "__main__":
    main() 