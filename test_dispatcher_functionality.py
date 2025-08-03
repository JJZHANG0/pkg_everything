#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Dispatcher页面功能
"""

import requests
import json
import time

def test_dispatcher_functionality():
    """测试Dispatcher页面功能"""
    print("🔍 测试Dispatcher页面功能...")
    
    # 获取token
    try:
        token_response = requests.post(
            "http://localhost:8000/api/token/",
            json={"username": "root", "password": "root"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if token_response.status_code != 200:
            print(f"❌ 获取token失败: {token_response.status_code}")
            return False
            
        token_data = token_response.json()
        access_token = token_data['access']
        print(f"✅ 获取token成功")
        
    except Exception as e:
        print(f"❌ 获取token错误: {e}")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 测试1: 获取机器人状态
    print("\n🔍 测试1: 获取机器人状态...")
    try:
        status_response = requests.get(
            "http://localhost:8000/api/robots/1/status/",
            headers=headers,
            timeout=5
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ 机器人状态获取成功")
            print(f"📋 机器人名称: {status_data['name']}")
            print(f"📋 当前状态: {status_data['status']}")
            print(f"📋 电池电量: {status_data['battery_level']}%")
            print(f"📋 门状态: {status_data['door_status']}")
            print(f"📋 当前位置: {status_data['current_location']}")
            print(f"📋 当前订单数: {len(status_data['current_orders'])}")
        else:
            print(f"❌ 机器人状态获取失败: {status_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 机器人状态获取错误: {e}")
        return False
    
    # 测试2: 发送机器人控制指令
    print("\n🔍 测试2: 发送机器人控制指令...")
    try:
        control_response = requests.post(
            "http://localhost:8000/api/robots/1/control/",
            json={"action": "open_door"},
            headers=headers,
            timeout=5
        )
        
        if control_response.status_code == 200:
            control_data = control_response.json()
            print(f"✅ 机器人控制指令发送成功")
            print(f"📋 指令ID: {control_data['command_id']}")
            print(f"📋 指令类型: {control_data['action']}")
            print(f"📋 指令状态: {control_data['status']}")
        else:
            print(f"❌ 机器人控制指令发送失败: {control_response.status_code}")
            print(f"📋 错误信息: {control_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 机器人控制指令发送错误: {e}")
        return False
    
    # 测试3: 获取调度订单
    print("\n🔍 测试3: 获取调度订单...")
    try:
        orders_response = requests.get(
            "http://localhost:8000/api/dispatch/orders/",
            headers=headers,
            timeout=5
        )
        
        if orders_response.status_code == 200:
            orders_data = orders_response.json()
            print(f"✅ 调度订单获取成功")
            print(f"📋 订单数量: {len(orders_data)}")
            for order in orders_data[:3]:  # 只显示前3个订单
                print(f"  - 订单ID: {order['id']}, 状态: {order['status']}")
        else:
            print(f"❌ 调度订单获取失败: {orders_response.status_code}")
            print(f"📋 错误信息: {orders_response.text}")
            
    except Exception as e:
        print(f"❌ 调度订单获取错误: {e}")
    
    print("\n🎉 Dispatcher页面功能测试完成！")
    return True

def main():
    """主函数"""
    print("🚀 开始测试Dispatcher页面功能...")
    print("=" * 50)
    
    success = test_dispatcher_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Dispatcher页面功能正常！")
        print("💡 现在可以在浏览器中正常使用Dispatcher页面了")
    else:
        print("❌ Dispatcher页面功能存在问题")

if __name__ == "__main__":
    main() 