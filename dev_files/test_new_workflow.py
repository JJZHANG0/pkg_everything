#!/usr/bin/env python3
import requests
import json
import time

def test_new_workflow():
    """测试新的业务流程"""
    
    print("🧪 测试新的业务流程...")
    
    # 1. 登录获取token
    try:
        print("🔐 获取认证token...")
        auth_response = requests.post(
            "http://localhost:8000/api/token/",
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
    
    # 2. 测试完整流程
    print("\n🔄 开始测试完整流程...")
    
    # 步骤1: 将订单状态改为ASSIGNED
    print("📝 步骤1: 更新订单状态为ASSIGNED...")
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
        return
    
    # 等待3秒
    print("⏳ 等待3秒...")
    time.sleep(3)
    
    # 步骤2: 检查机器人状态
    print("\n🤖 步骤2: 检查机器人状态...")
    robot_response = requests.get(
        "http://localhost:8000/api/robots/1/current_orders/",
        headers=headers
    )
    
    if robot_response.status_code == 200:
        robot_data = robot_response.json()
        print(f"🤖 机器人状态: {robot_data.get('status')}")
        print(f"📦 机器人订单数量: {len(robot_data.get('current_orders', []))}")
        
        if robot_data.get('status') == 'LOADING':
            print("✅ 机器人已进入装货状态")
        else:
            print("⚠️ 机器人状态异常")
    else:
        print(f"❌ 获取机器人状态失败: {robot_response.status_code}")
    
    # 步骤3: 模拟关门并开始配送
    print("\n🚪 步骤3: 模拟关门并开始配送...")
    print("💡 在机器人GUI中点击 'Close Door & Start' 按钮")
    print("💡 或者按 'R' 键开始二维码检测")
    
    # 等待用户操作
    input("\n⏸️ 请在机器人GUI中操作，然后按回车继续...")
    
    # 步骤4: 检查配送状态
    print("\n🚚 步骤4: 检查配送状态...")
    robot_response = requests.get(
        "http://localhost:8000/api/robots/1/current_orders/",
        headers=headers
    )
    
    if robot_response.status_code == 200:
        robot_data = robot_response.json()
        print(f"🤖 机器人状态: {robot_data.get('status')}")
        
        for order in robot_data.get('current_orders', []):
            print(f"📦 订单 {order.get('order_id')}: {order.get('status')}")
    
    print("\n🎯 测试完成！")
    print("\n📋 业务流程总结:")
    print("1. ✅ 订单状态更新为ASSIGNED → 自动分配给机器人")
    print("2. ✅ 机器人状态变为LOADING")
    print("3. 🔄 人工点击关门按钮 → 状态更新为DELIVERING")
    print("4. 🔄 检测到二维码 → 自动开门")
    print("5. 🔄 15秒后自动关门 → 状态更新为DELIVERED")

if __name__ == "__main__":
    test_new_workflow() 