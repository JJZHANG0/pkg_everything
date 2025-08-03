#!/usr/bin/env python3
import requests
import json

def test_order_status_update():
    """测试订单状态更新功能"""
    
    # 1. 获取JWT token
    login_data = {
        "username": "root",
        "password": "test123456"  # 重置后的密码
    }
    
    try:
        token_response = requests.post(
            "http://localhost:8000/api/token/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if token_response.status_code != 200:
            print(f"❌ 登录失败: {token_response.status_code}")
            print(token_response.text)
            return
        
        token_data = token_response.json()
        access_token = token_data['access']
        print("✅ 登录成功，获取到token")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 测试订单状态更新
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # 测试状态：PENDING -> ASSIGNED -> DELIVERING -> DELIVERED -> PENDING
    test_statuses = ["PENDING", "ASSIGNED", "DELIVERING", "DELIVERED", "PENDING"]
    
    for status in test_statuses:
        try:
            print(f"\n🔄 测试更新订单状态为: {status}")
            
            response = requests.patch(
                "http://localhost:8000/api/dispatch/orders/1/",
                json={"status": status},
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ 状态更新成功: {status}")
                data = response.json()
                if "order_data" in data:
                    print(f"📦 收到订单数据: 订单ID {data['order_data']['order_id']}")
            else:
                print(f"❌ 状态更新失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🧪 开始测试订单状态更新功能...")
    test_order_status_update()
    print("\n🎯 测试完成！") 