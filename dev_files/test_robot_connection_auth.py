#!/usr/bin/env python3
import requests
import json
import time

def test_robot_connection_with_auth():
    """测试机器人客户端与后端的连接（带认证）"""
    
    base_url = "http://localhost:8000"
    robot_id = 1
    
    print("🤖 测试机器人客户端连接（带认证）...")
    
    # 1. 获取JWT token
    try:
        print("🔐 获取认证token...")
        auth_response = requests.post(
            f"{base_url}/api/token/",
            json={"username": "root", "password": "test123456"}
        )
        
        if auth_response.status_code != 200:
            print("❌ 认证失败")
            return
            
        token = auth_response.json()['access']
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        print("✅ 认证成功")
        
    except Exception as e:
        print(f"❌ 认证异常: {e}")
        return
    
    # 2. 测试获取机器人当前订单
    try:
        print(f"\n📡 测试获取机器人 {robot_id} 的当前订单...")
        response = requests.get(f"{base_url}/api/robots/{robot_id}/current_orders/", headers=headers)
        
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
    
    # 3. 测试接收订单
    try:
        print(f"\n📦 测试机器人 {robot_id} 接收订单...")
        response = requests.post(f"{base_url}/api/robots/{robot_id}/receive_orders/", 
                               json={"action": "receive"}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功接收订单")
            print(f"   接收到的订单: {data}")
        else:
            print(f"❌ 接收订单失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    # 4. 测试开始配送
    try:
        print(f"\n🚚 测试机器人 {robot_id} 开始配送...")
        response = requests.post(f"{base_url}/api/robots/{robot_id}/start_delivery/", 
                               json={"action": "close_door_and_start"}, headers=headers)
        
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
                
                # 等待3秒，然后检查机器人是否收到订单
                print("⏳ 等待3秒检查机器人是否收到订单...")
                time.sleep(3)
                
                # 检查机器人当前订单
                robot_response = requests.get(
                    "http://localhost:8000/api/robots/1/current_orders/",
                    headers=headers
                )
                
                if robot_response.status_code == 200:
                    robot_data = robot_response.json()
                    print(f"🤖 机器人当前状态: {robot_data.get('status')}")
                    print(f"📦 机器人订单数量: {len(robot_data.get('current_orders', []))}")
                else:
                    print(f"❌ 获取机器人状态失败: {robot_response.status_code}")
        else:
            print(f"❌ 状态更新失败: {update_response.status_code}")
            print(update_response.text)
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_robot_connection_with_auth()
    test_order_status_updates()
    print("\n🎯 测试完成！") 