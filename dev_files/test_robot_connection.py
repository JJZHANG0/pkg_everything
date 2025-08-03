#!/usr/bin/env python3
import requests
import json
import time

def test_robot_connection():
    """测试机器人客户端与后端的连接"""
    
    base_url = "http://localhost:8000"
    robot_id = 1
    
    print("🤖 测试机器人客户端连接...")
    
    # 1. 测试获取机器人当前订单
    try:
        print(f"\n📡 测试获取机器人 {robot_id} 的当前订单...")
        response = requests.get(f"{base_url}/api/robots/{robot_id}/current_orders/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取机器人订单信息")
            print(f"   机器人状态: {data.get('status', 'Unknown')}")
            print(f"   订单数量: {len(data.get('current_orders', []))}")
            
            if data.get('current_orders'):
                for order in data['current_orders']:
                    print(f"   - 订单 {order.get('order_id')}: {order.get('status')}")
        else:
            print(f"❌ 获取订单失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    # 2. 测试接收订单
    try:
        print(f"\n📦 测试机器人 {robot_id} 接收订单...")
        response = requests.post(f"{base_url}/api/robots/{robot_id}/receive_orders/", 
                               json={"action": "receive"})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功接收订单")
            print(f"   接收到的订单: {data}")
        else:
            print(f"❌ 接收订单失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    # 3. 测试开始配送
    try:
        print(f"\n🚚 测试机器人 {robot_id} 开始配送...")
        response = requests.post(f"{base_url}/api/robots/{robot_id}/start_delivery/", 
                               json={"action": "close_door_and_start"})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功开始配送")
            print(f"   配送信息: {data}")
        else:
            print(f"❌ 开始配送失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")

def test_order_status_updates():
    """测试订单状态更新是否触发机器人通知"""
    
    print("\n🔄 测试订单状态更新...")
    
    # 1. 登录获取token
    try:
        login_response = requests.post(
            "http://localhost:8000/api/token/",
            json={"username": "root", "password": "test123456"}
        )
        
        if login_response.status_code != 200:
            print("❌ 登录失败")
            return
            
        token = login_response.json()['access']
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # 2. 更新订单状态为ASSIGNED
        print("📝 更新订单状态为ASSIGNED...")
        update_response = requests.patch(
            "http://localhost:8000/api/dispatch/orders/1/",
            json={"status": "ASSIGNED"},
            headers=headers
        )
        
        if update_response.status_code == 200:
            data = update_response.json()
            print("✅ 订单状态更新成功")
            if "order_data" in data:
                print(f"📦 订单数据已发送: 订单ID {data['order_data']['order_id']}")
                print(f"   学生: {data['order_data']['student']['name']}")
                print(f"   配送地址: {data['order_data']['delivery_location']['building']}")
        else:
            print(f"❌ 状态更新失败: {update_response.status_code}")
            print(update_response.text)
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_robot_connection()
    test_order_status_updates()
    print("\n🎯 测试完成！") 