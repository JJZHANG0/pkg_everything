#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_robot_current_orders():
    """测试机器人当前订单API"""
    print("🔍 测试机器人当前订单API...")
    
    # 获取机器人列表
    response = requests.get(f"{BASE_URL}/robots/")
    print(f"机器人列表响应: {response.status_code}")
    
    if response.status_code == 200:
        robots = response.json()
        print(f"找到 {len(robots)} 个机器人")
        
        if robots:
            robot_id = robots[0]['id']
            print(f"使用机器人 ID: {robot_id}")
            
            # 测试当前订单API
            response = requests.get(f"{BASE_URL}/robots/{robot_id}/current_orders/")
            print(f"当前订单API响应: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 机器人当前订单数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ 错误: {response.text}")
    else:
        print(f"❌ 获取机器人列表失败: {response.text}")

def test_receive_orders():
    """测试接收订单API"""
    print("\n📦 测试接收订单API...")
    
    # 获取机器人列表
    response = requests.get(f"{BASE_URL}/robots/")
    if response.status_code == 200:
        robots = response.json()
        if robots:
            robot_id = robots[0]['id']
            
            # 测试接收订单
            data = {"order_ids": [1, 2, 3]}  # 假设的订单ID
            response = requests.post(f"{BASE_URL}/robots/{robot_id}/receive_orders/", json=data)
            print(f"接收订单API响应: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 订单分配成功:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ 错误: {response.text}")

if __name__ == "__main__":
    test_robot_current_orders()
    test_receive_orders() 