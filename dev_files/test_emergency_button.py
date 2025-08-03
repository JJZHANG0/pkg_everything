#!/usr/bin/env python3
"""
🚨 紧急按钮功能测试脚本
测试紧急按钮API的功能
"""

import requests
import json
import time

def test_emergency_button():
    """测试紧急按钮功能"""
    
    # 配置
    base_url = "http://localhost:8000/api"
    username = "root"
    password = "test123456"
    
    print("🚨 紧急按钮功能测试")
    print("=" * 50)
    
    # 1. 登录获取token
    print("1. 🔐 登录获取访问令牌...")
    try:
        login_response = requests.post(
            f"{base_url}/token/",
            json={"username": username, "password": password},
            timeout=5
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access")
            print(f"✅ 登录成功: {username}")
        else:
            print(f"❌ 登录失败: HTTP {login_response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # 2. 获取初始机器人状态
    print("\n2. 📊 获取初始机器人状态...")
    try:
        status_response = requests.get(
            f"{base_url}/robots/1/status/",
            headers=headers,
            timeout=5
        )
        
        if status_response.status_code == 200:
            initial_status = status_response.json()
            print(f"✅ 初始门状态: {initial_status.get('door_status', 'Unknown')}")
        else:
            print(f"❌ 获取状态失败: HTTP {status_response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取状态异常: {e}")
        return
    
    # 3. 触发紧急按钮
    print("\n3. 🚨 触发紧急按钮...")
    try:
        emergency_response = requests.post(
            f"{base_url}/robots/1/emergency_button/",
            headers=headers,
            timeout=5
        )
        
        if emergency_response.status_code == 200:
            emergency_data = emergency_response.json()
            print(f"✅ 紧急按钮触发成功!")
            print(f"   指令ID: {emergency_data.get('command_id')}")
            print(f"   状态: {emergency_data.get('status')}")
            print(f"   门状态: {emergency_data.get('door_status')}")
            print(f"   消息: {emergency_data.get('message')}")
        else:
            print(f"❌ 紧急按钮触发失败: HTTP {emergency_response.status_code}")
            print(f"   错误: {emergency_response.text}")
            return
    except Exception as e:
        print(f"❌ 紧急按钮触发异常: {e}")
        return
    
    # 4. 验证门状态已更新
    print("\n4. 🔍 验证门状态更新...")
    time.sleep(2)  # 等待状态更新
    
    try:
        final_status_response = requests.get(
            f"{base_url}/robots/1/status/",
            headers=headers,
            timeout=5
        )
        
        if final_status_response.status_code == 200:
            final_status = final_status_response.json()
            final_door_status = final_status.get('door_status', 'Unknown')
            print(f"✅ 最终门状态: {final_door_status}")
            
            if final_door_status == 'OPEN':
                print("🎉 紧急按钮功能测试成功！门已成功开启")
            else:
                print("⚠️ 门状态未按预期更新")
        else:
            print(f"❌ 获取最终状态失败: HTTP {final_status_response.status_code}")
    except Exception as e:
        print(f"❌ 验证状态异常: {e}")
    
    # 5. 测试指令历史
    print("\n5. 📋 检查指令历史...")
    try:
        commands_response = requests.get(
            f"{base_url}/robots/1/get_commands/",
            headers=headers,
            timeout=5
        )
        
        if commands_response.status_code == 200:
            commands_data = commands_response.json()
            pending_commands = commands_data.get('pending_commands', [])
            print(f"✅ 待执行指令数量: {len(pending_commands)}")
            
            # 查找紧急指令
            emergency_commands = [cmd for cmd in pending_commands if cmd.get('command') == 'emergency_open_door']
            if emergency_commands:
                print(f"🚨 发现紧急指令: {len(emergency_commands)} 条")
            else:
                print("ℹ️ 无待执行的紧急指令（已立即完成）")
        else:
            print(f"❌ 获取指令历史失败: HTTP {commands_response.status_code}")
    except Exception as e:
        print(f"❌ 检查指令历史异常: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 紧急按钮功能测试完成")

if __name__ == "__main__":
    test_emergency_button() 