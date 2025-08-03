#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 紧急按钮通知测试脚本
模拟机器人紧急按钮触发，测试前端通知功能
"""

import requests
import time
import json

def test_emergency_notification():
    """测试紧急按钮通知功能"""
    
    SERVER_URL = "http://localhost:8000"
    ROBOT_ID = 1
    USERNAME = "root"
    PASSWORD = "root"
    
    print("🧪 紧急按钮通知测试")
    print("=" * 50)
    
    try:
        # 1. 登录
        print("🔐 正在登录...")
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            return False
            
        token = login_response.json()["access"]
        print("✅ 登录成功！")
        
        # 2. 触发紧急按钮
        print("\n🚨 触发紧急按钮...")
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
            print("✅ 紧急按钮触发成功！")
            print(f"📝 响应消息: {data.get('message', 'N/A')}")
            print(f"🆔 命令ID: {data.get('command_id', 'N/A')}")
            
            # 3. 等待几秒让前端检测到
            print("\n⏳ 等待前端检测紧急按钮事件...")
            time.sleep(5)
            
            # 4. 检查系统日志
            print("\n📋 检查系统日志...")
            logs_response = requests.get(
                f"{SERVER_URL}/api/logs/?log_type=ROBOT_CONTROL&level=WARNING&limit=5",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                emergency_logs = [log for log in logs_data.get('results', []) 
                                if '紧急按钮' in log.get('message', '')]
                
                if emergency_logs:
                    print("✅ 找到紧急按钮日志:")
                    for log in emergency_logs[:3]:  # 显示最近3条
                        print(f"   - {log.get('message', 'N/A')} ({log.get('timestamp', 'N/A')})")
                else:
                    print("⚠️ 未找到紧急按钮相关日志")
            
            print("\n🎯 测试完成！")
            print("💡 请检查前端Dispatcher页面是否显示紧急按钮通知弹窗")
            print("💡 如果浏览器支持，还应该收到系统通知")
            
            return True
        else:
            print(f"❌ 紧急按钮触发失败: {emergency_response.status_code}")
            print(f"📝 错误信息: {emergency_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def simulate_multiple_emergency_triggers():
    """模拟多次紧急按钮触发"""
    
    SERVER_URL = "http://localhost:8000"
    ROBOT_ID = 1
    USERNAME = "root"
    PASSWORD = "root"
    
    print("🔄 模拟多次紧急按钮触发")
    print("=" * 50)
    
    try:
        # 登录
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            return False
            
        token = login_response.json()["access"]
        print("✅ 登录成功！")
        
        # 触发3次紧急按钮，每次间隔10秒
        for i in range(3):
            print(f"\n🚨 第{i+1}次触发紧急按钮...")
            
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
                print(f"✅ 第{i+1}次触发成功！命令ID: {data.get('command_id', 'N/A')}")
            else:
                print(f"❌ 第{i+1}次触发失败: {emergency_response.status_code}")
            
            if i < 2:  # 不是最后一次
                print("⏳ 等待10秒后触发下一次...")
                time.sleep(10)
        
        print("\n🎯 多次触发测试完成！")
        print("💡 请检查前端是否收到多次通知")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🧪 紧急按钮通知测试工具")
    print("=" * 50)
    
    print("选择测试模式:")
    print("   1. 单次紧急按钮触发测试")
    print("   2. 多次紧急按钮触发测试")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        test_emergency_notification()
    elif choice == "2":
        simulate_multiple_emergency_triggers()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 