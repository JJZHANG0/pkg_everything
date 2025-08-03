#!/usr/bin/env python3
"""
测试新的机器人控制机制
验证服务器控制机器人的完整流程
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

def print_step(step_name):
    """打印测试步骤"""
    print(f"\n{'='*50}")
    print(f"🔍 测试步骤: {step_name}")
    print(f"{'='*50}")

def print_response(response, title="响应"):
    """打印API响应"""
    print(f"\n📋 {title}:")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"数据: {response.text}")

def test_robot_control_flow():
    """测试机器人控制流程"""
    
    print("🚀 开始测试新的机器人控制机制")
    
    # 1. 发送开门指令
    print_step("1. 发送开门指令")
    control_data = {
        "action": "open_door"
    }
    
    response = requests.post(f"{BASE_URL}/robots/1/control/", json=control_data)
    print_response(response, "发送开门指令")
    
    if response.status_code != 200:
        print("❌ 发送开门指令失败")
        return
    
    command_data = response.json()
    command_id = command_data.get('command_id')
    print(f"✅ 开门指令发送成功，指令ID: {command_id}")
    
    # 2. 机器人获取指令
    print_step("2. 机器人获取指令")
    response = requests.get(f"{BASE_URL}/robots/1/get_commands/")
    print_response(response, "获取指令")
    
    if response.status_code != 200:
        print("❌ 获取指令失败")
        return
    
    commands_data = response.json()
    pending_commands = commands_data.get('pending_commands', [])
    print(f"✅ 获取到 {len(pending_commands)} 个待执行指令")
    
    if not pending_commands:
        print("❌ 没有找到待执行指令")
        return
    
    # 3. 机器人执行指令
    print_step("3. 机器人执行开门指令")
    execute_data = {
        "command_id": command_id,
        "result": "开门成功"
    }
    
    response = requests.post(f"{BASE_URL}/robots/1/execute_command/", json=execute_data)
    print_response(response, "执行指令")
    
    if response.status_code != 200:
        print("❌ 执行指令失败")
        return
    
    print("✅ 开门指令执行成功")
    
    # 4. 再次获取指令（应该为空）
    print_step("4. 验证指令已执行")
    response = requests.get(f"{BASE_URL}/robots/1/get_commands/")
    print_response(response, "再次获取指令")
    
    if response.status_code == 200:
        commands_data = response.json()
        remaining_commands = commands_data.get('pending_commands', [])
        if len(remaining_commands) == 0:
            print("✅ 指令已成功执行并清除")
        else:
            print(f"❌ 仍有 {len(remaining_commands)} 个待执行指令")

def test_multiple_commands():
    """测试多个指令的队列处理"""
    print("\n" + "="*60)
    print("🔄 测试多个指令的队列处理")
    print("="*60)
    
    # 发送多个指令
    commands = [
        {"action": "close_door"},
        {"action": "start_delivery"},
        {"action": "stop_robot"}
    ]
    
    command_ids = []
    
    for i, cmd in enumerate(commands):
        print_step(f"发送指令 {i+1}: {cmd['action']}")
        response = requests.post(f"{BASE_URL}/robots/1/control/", json=cmd)
        print_response(response, f"发送指令 {cmd['action']}")
        
        if response.status_code == 200:
            command_id = response.json().get('command_id')
            command_ids.append(command_id)
            print(f"✅ 指令 {cmd['action']} 发送成功，ID: {command_id}")
        else:
            print(f"❌ 指令 {cmd['action']} 发送失败")
    
    # 获取所有指令
    print_step("获取所有待执行指令")
    response = requests.get(f"{BASE_URL}/robots/1/get_commands/")
    print_response(response, "获取所有指令")
    
    if response.status_code == 200:
        commands_data = response.json()
        pending_commands = commands_data.get('pending_commands', [])
        print(f"✅ 队列中有 {len(pending_commands)} 个待执行指令")
        
        # 按顺序执行指令
        for i, command in enumerate(pending_commands):
            print_step(f"执行指令 {i+1}: {command['command']}")
            execute_data = {
                "command_id": command['command_id'],
                "result": f"执行 {command['command']} 成功"
            }
            
            response = requests.post(f"{BASE_URL}/robots/1/execute_command/", json=execute_data)
            print_response(response, f"执行指令 {command['command']}")
            
            if response.status_code == 200:
                print(f"✅ 指令 {command['command']} 执行成功")
            else:
                print(f"❌ 指令 {command['command']} 执行失败")

def test_command_status():
    """测试指令状态管理"""
    print("\n" + "="*60)
    print("📊 测试指令状态管理")
    print("="*60)
    
    # 发送一个指令
    print_step("发送测试指令")
    control_data = {"action": "open_door"}
    response = requests.post(f"{BASE_URL}/robots/1/control/", json=control_data)
    
    if response.status_code == 200:
        command_id = response.json().get('command_id')
        print(f"✅ 测试指令发送成功，ID: {command_id}")
        
        # 尝试重复执行同一指令
        print_step("尝试重复执行同一指令")
        execute_data = {
            "command_id": command_id,
            "result": "第一次执行"
        }
        
        response1 = requests.post(f"{BASE_URL}/robots/1/execute_command/", json=execute_data)
        print_response(response1, "第一次执行")
        
        response2 = requests.post(f"{BASE_URL}/robots/1/execute_command/", json=execute_data)
        print_response(response2, "第二次执行（应该失败）")
        
        if response2.status_code == 400:
            print("✅ 重复执行被正确阻止")
        else:
            print("❌ 重复执行没有被阻止")
    else:
        print("❌ 发送测试指令失败")

if __name__ == "__main__":
    try:
        # 测试基本控制流程
        test_robot_control_flow()
        
        # 测试多个指令队列
        test_multiple_commands()
        
        # 测试指令状态管理
        test_command_status()
        
        print("\n" + "="*60)
        print("🎉 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc() 