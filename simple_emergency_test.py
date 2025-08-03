#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 简化版紧急按钮API测试脚本
快速测试紧急按钮功能
"""

import requests
import json

def test_emergency_button():
    """测试紧急按钮API"""
    
    # 配置参数 - 请根据实际情况修改
    SERVER_URL = "http://192.168.110.148:8000"  # 修改为你的服务器地址（包含协议和端口）
    ROBOT_ID = 1                          # 修改为你的机器人ID
    USERNAME = "root"                     # 修改为你的用户名
    PASSWORD = "root"                     # 修改为你的密码
    
    print("🚨 紧急按钮API快速测试")
    print("=" * 40)
    print(f"📡 服务器地址: {SERVER_URL}")
    print(f"🤖 机器人ID: {ROBOT_ID}")
    print(f"👤 用户名: {USERNAME}")
    print("=" * 40)
    
    try:
        # 1. 登录获取token
        print("🔐 正在登录...")
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"📝 错误信息: {login_response.text}")
            return False
            
        token = login_response.json()["access"]
        print("✅ 登录成功！")
        
        # 2. 测试紧急按钮
        print("\n🚨 测试紧急按钮...")
        emergency_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/emergency_button/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"action": "emergency_open_door"},
            timeout=10
        )
        
        if emergency_response.status_code == 200:
            data = emergency_response.json()
            print("✅ 紧急按钮测试成功！")
            print(f"📝 响应消息: {data.get('message', 'N/A')}")
            print(f"🚪 门状态: {data.get('door_status', 'N/A')}")
            print(f"🆔 命令ID: {data.get('command_id', 'N/A')}")
            return True
        else:
            print(f"❌ 紧急按钮测试失败: {emergency_response.status_code}")
            print(f"📝 错误信息: {emergency_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    success = test_emergency_button()
    if success:
        print("\n🎉 测试完成！API工作正常！")
    else:
        print("\n❌ 测试失败！请检查配置和网络连接。") 