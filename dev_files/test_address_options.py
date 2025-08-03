#!/usr/bin/env python3
"""
测试地址选项修改
"""

import requests
import json

def test_address_options():
    """测试地址选项是否正确修改"""
    
    # 测试前端地址选项
    print("🔍 测试前端地址选项...")
    
    try:
        # 获取前端页面
        response = requests.get('http://localhost:3000')
        if response.status_code == 200:
            print("✅ 前端服务正常")
            
            # 检查是否包含新的地址选项
            content = response.text
            if 'ORIGIN' in content:
                print("✅ 前端包含 ORIGIN 地址选项")
            else:
                print("❌ 前端未找到 ORIGIN 地址选项")
                
            if 'Lauridsen Barrack' in content:
                print("✅ 前端包含 Lauridsen Barrack 地址选项")
            else:
                print("❌ 前端未找到 Lauridsen Barrack 地址选项")
                
            # 检查是否移除了旧的地址选项
            old_addresses = ['Library', 'Dorm A', 'Cafeteria', 'Engineering', 'Admin Office', 'Dorm B']
            found_old = []
            for addr in old_addresses:
                if addr in content:
                    found_old.append(addr)
            
            if found_old:
                print(f"⚠️  前端仍包含旧地址选项: {found_old}")
            else:
                print("✅ 前端已移除所有旧地址选项")
                
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试前端时出错: {e}")
    
    # 测试后端API
    print("\n🔍 测试后端API...")
    
    try:
        # 测试创建订单API
        order_data = {
            "package_type": "Box",
            "weight": "1kg",
            "fragile": False,
            "description": "Test package",
            "pickup": {
                "building": "ORIGIN",
                "instructions": "Test pickup"
            },
            "delivery": {
                "building": "Lauridsen Barrack"
            },
            "speed": "Standard",
            "schedule_date": "2025-08-01",
            "schedule_time": "10:00:00"
        }
        
        response = requests.post(
            'http://localhost:8000/api/orders/',
            json=order_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("✅ 后端API接受新的地址选项")
            order = response.json()
            print(f"✅ 订单创建成功，ID: {order.get('id')}")
            print(f"   取件地址: {order.get('pickup_building')}")
            print(f"   配送地址: {order.get('delivery_building')}")
        else:
            print(f"❌ 后端API拒绝新的地址选项: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试后端API时出错: {e}")
    
    print("\n🎉 地址选项测试完成！")

if __name__ == "__main__":
    test_address_options() 