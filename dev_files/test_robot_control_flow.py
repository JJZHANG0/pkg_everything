#!/usr/bin/env python3
"""
测试机器人控制流程
验证开门/关门指令的完整流程
"""

import requests
import time
import json

def test_robot_control_flow():
    """测试机器人控制流程"""
    
    # 配置
    BASE_URL = "http://localhost:8000"
    
    # 获取认证token
    print("🔐 获取认证token...")
    token_response = requests.post(f'{BASE_URL}/api/token/', {
        'username': 'root',
        'password': 'test123456'
    })
    
    if token_response.status_code != 200:
        print("❌ 认证失败")
        return
    
    token = token_response.json()['access']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ 认证成功")
    
    # 1. 获取机器人初始状态
    print("\n1️⃣ 获取机器人初始状态...")
    status_response = requests.get(f'{BASE_URL}/api/robots/1/status/', headers=headers)
    if status_response.status_code == 200:
        initial_status = status_response.json()
        print(f"   初始门状态: {initial_status.get('door_status', 'Unknown')}")
        print(f"   初始机器人状态: {initial_status.get('status', 'Unknown')}")
    else:
        print(f"   ❌ 获取状态失败: {status_response.status_code}")
        return
    
    # 2. 发送开门指令
    print("\n2️⃣ 发送开门指令...")
    open_door_response = requests.post(f'{BASE_URL}/api/robots/1/control/', 
                                     headers=headers,
                                     json={'action': 'open_door'})
    
    if open_door_response.status_code == 200:
        open_door_data = open_door_response.json()
        command_id = open_door_data.get('command_id')
        print(f"   ✅ 开门指令发送成功，指令ID: {command_id}")
    else:
        print(f"   ❌ 开门指令发送失败: {open_door_response.status_code}")
        return
    
    # 3. 等待并检查指令执行状态
    print("\n3️⃣ 等待指令执行...")
    max_wait = 30  # 最多等待30秒
    for i in range(max_wait):
        time.sleep(1)
        
        # 检查机器人状态
        status_response = requests.get(f'{BASE_URL}/api/robots/1/status/', headers=headers)
        if status_response.status_code == 200:
            current_status = status_response.json()
            door_status = current_status.get('door_status', 'Unknown')
            
            print(f"   第{i+1}秒 - 门状态: {door_status}")
            
            if door_status == 'OPEN':
                print("   ✅ 开门指令执行成功！")
                break
        else:
            print(f"   ❌ 获取状态失败: {status_response.status_code}")
    
    # 4. 发送关门指令
    print("\n4️⃣ 发送关门指令...")
    close_door_response = requests.post(f'{BASE_URL}/api/robots/1/control/', 
                                      headers=headers,
                                      json={'action': 'close_door'})
    
    if close_door_response.status_code == 200:
        close_door_data = close_door_response.json()
        command_id = close_door_data.get('command_id')
        print(f"   ✅ 关门指令发送成功，指令ID: {command_id}")
    else:
        print(f"   ❌ 关门指令发送失败: {close_door_response.status_code}")
        return
    
    # 5. 等待并检查关门指令执行状态
    print("\n5️⃣ 等待关门指令执行...")
    for i in range(max_wait):
        time.sleep(1)
        
        # 检查机器人状态
        status_response = requests.get(f'{BASE_URL}/api/robots/1/status/', headers=headers)
        if status_response.status_code == 200:
            current_status = status_response.json()
            door_status = current_status.get('door_status', 'Unknown')
            
            print(f"   第{i+1}秒 - 门状态: {door_status}")
            
            if door_status == 'CLOSED':
                print("   ✅ 关门指令执行成功！")
                break
        else:
            print(f"   ❌ 获取状态失败: {status_response.status_code}")
    
    # 6. 检查指令历史
    print("\n6️⃣ 检查指令历史...")
    commands_response = requests.get(f'{BASE_URL}/api/robots/1/get_commands/', headers=headers)
    if commands_response.status_code == 200:
        commands_data = commands_response.json()
        pending_commands = commands_data.get('pending_commands', [])
        print(f"   待执行指令数量: {len(pending_commands)}")
        
        if len(pending_commands) == 0:
            print("   ✅ 所有指令都已执行完成")
        else:
            print("   ⚠️ 还有待执行的指令")
            for cmd in pending_commands:
                print(f"     - {cmd.get('command_display')} (ID: {cmd.get('command_id')})")
    else:
        print(f"   ❌ 获取指令历史失败: {commands_response.status_code}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_robot_control_flow() 