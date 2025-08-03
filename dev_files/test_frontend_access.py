#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

def test_frontend_access():
    """测试前端访问"""
    print("🌐 前端访问测试")
    print("=" * 50)
    
    # 测试前端页面
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端页面访问成功")
        else:
            print(f"❌ 前端页面访问失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 前端页面访问异常: {e}")
    
    # 测试后端API
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API访问成功")
        else:
            print(f"❌ 后端API访问失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 后端API访问异常: {e}")
    
    # 测试机器人状态API
    try:
        # 先获取token
        auth_response = requests.post(
            "http://localhost:8000/api/token/",
            json={"username": "root", "password": "test123456"},
            timeout=5
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 测试机器人状态
            robot_response = requests.get(
                "http://localhost:8000/api/robots/1/status/",
                headers=headers,
                timeout=5
            )
            
            if robot_response.status_code == 200:
                robot_data = robot_response.json()
                print(f"✅ 机器人状态API访问成功")
                print(f"   机器人状态: {robot_data.get('status')}")
                print(f"   当前位置: {robot_data.get('current_location')}")
                print(f"   电池电量: {robot_data.get('battery_level')}%")
                print(f"   门状态: {robot_data.get('door_status')}")
            else:
                print(f"❌ 机器人状态API访问失败: HTTP {robot_response.status_code}")
        else:
            print(f"❌ 认证失败: HTTP {auth_response.status_code}")
            
    except Exception as e:
        print(f"❌ 机器人状态API访问异常: {e}")

def test_robot_control():
    """测试机器人控制"""
    print("\n🤖 机器人控制测试")
    print("=" * 50)
    
    try:
        # 获取token
        auth_response = requests.post(
            "http://localhost:8000/api/token/",
            json={"username": "root", "password": "test123456"},
            timeout=5
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 测试开门
            open_response = requests.post(
                "http://localhost:8000/api/robots/1/control/",
                json={"action": "open_door"},
                headers=headers,
                timeout=5
            )
            
            if open_response.status_code == 200:
                print("✅ 机器人开门控制成功")
            else:
                print(f"❌ 机器人开门控制失败: HTTP {open_response.status_code}")
            
            # 测试关门
            close_response = requests.post(
                "http://localhost:8000/api/robots/1/control/",
                json={"action": "close_door"},
                headers=headers,
                timeout=5
            )
            
            if close_response.status_code == 200:
                print("✅ 机器人关门控制成功")
            else:
                print(f"❌ 机器人关门控制失败: HTTP {close_response.status_code}")
                
        else:
            print(f"❌ 认证失败: HTTP {auth_response.status_code}")
            
    except Exception as e:
        print(f"❌ 机器人控制测试异常: {e}")

def main():
    """主函数"""
    print("🚀 机器人配送系统前端测试")
    print("=" * 60)
    
    test_frontend_access()
    test_robot_control()
    
    print("\n" + "=" * 60)
    print("📋 测试完成！")
    print("🌐 前端地址: http://localhost:3000")
    print("🔧 后端API: http://localhost:8000")
    print("📖 使用指南: 查看 SYSTEM_USAGE_GUIDE.md")

if __name__ == "__main__":
    main() 