#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 智能版紧急按钮API测试脚本
自动处理URL格式，更友好的用户体验
"""

import requests
import json
import re

def normalize_url(url):
    """标准化URL格式"""
    # 移除空白字符
    url = url.strip()
    
    # 如果没有协议前缀，添加http://
    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    
    # 如果没有端口号，添加:8000
    if re.match(r'https?://[^:]+$', url):
        url = f"{url}:8000"
    
    return url

def test_emergency_button():
    """测试紧急按钮API"""
    
    print("🚨 智能版紧急按钮API测试")
    print("=" * 50)
    
    # 获取配置
    server_input = input("请输入服务器地址 (IP或域名，如: 192.168.110.148): ").strip()
    if not server_input:
        server_input = "localhost"
    
    # 智能处理URL
    SERVER_URL = normalize_url(server_input)
    
    robot_id_input = input("请输入机器人ID (默认: 1): ").strip()
    ROBOT_ID = int(robot_id_input) if robot_id_input else 1
    
    username = input("请输入用户名 (默认: root): ").strip() or "root"
    password = input("请输入密码 (默认: root): ").strip() or "root"
    
    print(f"\n📋 最终配置:")
    print(f"   服务器: {SERVER_URL}")
    print(f"   机器人ID: {ROBOT_ID}")
    print(f"   用户名: {username}")
    print(f"   密码: {'*' * len(password)}")
    print("=" * 50)
    
    try:
        # 1. 测试连接
        print("🔍 测试服务器连接...")
        try:
            test_response = requests.get(f"{SERVER_URL}/api/", timeout=5)
            print("✅ 服务器连接正常")
        except Exception as e:
            print(f"⚠️ 服务器连接警告: {e}")
            print("继续尝试登录...")
        
        # 2. 登录获取token
        print("\n🔐 正在登录...")
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": username, "password": password},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"📝 错误信息: {login_response.text}")
            print("\n💡 可能的解决方案:")
            print("   1. 检查用户名和密码是否正确")
            print("   2. 确认服务器地址和端口")
            print("   3. 检查网络连接")
            return False
            
        token = login_response.json()["access"]
        print("✅ 登录成功！")
        
        # 3. 测试紧急按钮
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
            print("\n📋 响应详情:")
            print(f"   📝 消息: {data.get('message', 'N/A')}")
            print(f"   🚪 门状态: {data.get('door_status', 'N/A')}")
            print(f"   🆔 命令ID: {data.get('command_id', 'N/A')}")
            print(f"   ⚡ 状态: {data.get('status', 'N/A')}")
            print(f"   🚨 紧急标志: {data.get('emergency', 'N/A')}")
            return True
        else:
            print(f"❌ 紧急按钮测试失败: {emergency_response.status_code}")
            print(f"📝 错误信息: {emergency_response.text}")
            print("\n💡 可能的解决方案:")
            print("   1. 检查机器人ID是否存在")
            print("   2. 确认用户有操作权限")
            print("   3. 检查API路径是否正确")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误：无法连接到服务器")
        print("💡 请检查:")
        print("   1. 服务器地址是否正确")
        print("   2. 服务器是否正在运行")
        print("   3. 网络连接是否正常")
        return False
    except requests.exceptions.Timeout:
        print("❌ 超时错误：请求超时")
        print("💡 请检查网络连接或稍后重试")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    success = test_emergency_button()
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！紧急按钮API工作正常！")
    else:
        print("❌ 测试失败！请检查配置和网络连接。")
        print("\n📞 如需帮助，请提供以下信息:")
        print("   1. 错误信息截图")
        print("   2. 服务器地址和端口")
        print("   3. 网络环境信息") 