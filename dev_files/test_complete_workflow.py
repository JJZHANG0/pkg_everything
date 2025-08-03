#!/usr/bin/env python3
"""
完整的工作流程测试脚本
测试新的订单状态流程：PENDING -> ASSIGNED -> DELIVERING -> DELIVERED -> PICKED_UP
以及超时处理：DELIVERED -> CANCELLED
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

def test_complete_workflow():
    """测试完整的工作流程"""
    
    print("🚀 开始测试完整的工作流程")
    
    # 1. 创建订单
    print_step("1. 创建订单")
    order_data = {
        "student": 1,  # 假设学生ID为1
        "package_description": "测试包裹",
        "pickup_location": "图书馆",
        "delivery_location": "宿舍楼",
        "status": "PENDING"
    }
    
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    print_response(response, "创建订单")
    
    if response.status_code != 201:
        print("❌ 创建订单失败")
        return
    
    order = response.json()
    order_id = order['id']
    print(f"✅ 订单创建成功，ID: {order_id}")
    
    # 2. 分配订单给机器人
    print_step("2. 分配订单给机器人")
    assign_data = {
        "status": "ASSIGNED"
    }
    
    response = requests.patch(f"{BASE_URL}/dispatch/orders/{order_id}/", json=assign_data)
    print_response(response, "分配订单")
    
    if response.status_code != 200:
        print("❌ 分配订单失败")
        return
    
    print("✅ 订单分配成功")
    
    # 3. 检查机器人状态
    print_step("3. 检查机器人状态")
    response = requests.get(f"{BASE_URL}/robots/1/status/")
    print_response(response, "机器人状态")
    
    if response.status_code == 200:
        robot_status = response.json()
        print(f"✅ 机器人状态: {robot_status.get('status', '未知')}")
    
    # 4. 开始配送
    print_step("4. 开始配送")
    control_data = {
        "action": "start_delivery"
    }
    
    response = requests.post(f"{BASE_URL}/robots/1/control/", json=control_data)
    print_response(response, "开始配送")
    
    if response.status_code != 200:
        print("❌ 开始配送失败")
        return
    
    print("✅ 配送开始成功")
    
    # 5. 检查订单状态
    print_step("5. 检查订单状态")
    response = requests.get(f"{BASE_URL}/orders/{order_id}/")
    print_response(response, "订单状态")
    
    if response.status_code == 200:
        order_status = response.json()
        print(f"✅ 订单状态: {order_status.get('status', '未知')}")
    
    # 6. 机器人到达目的地
    print_step("6. 机器人到达目的地")
    arrived_data = {
        "order_id": order_id
    }
    
    response = requests.post(f"{BASE_URL}/robots/1/arrived_at_destination/", json=arrived_data)
    print_response(response, "到达目的地")
    
    if response.status_code != 200:
        print("❌ 到达目的地失败")
        return
    
    print("✅ 机器人到达目的地成功")
    
    # 7. 检查订单状态（应该是DELIVERED）
    print_step("7. 检查订单状态（已送达）")
    response = requests.get(f"{BASE_URL}/orders/{order_id}/")
    print_response(response, "订单状态")
    
    if response.status_code == 200:
        order_status = response.json()
        current_status = order_status.get('status', '未知')
        print(f"✅ 订单状态: {current_status}")
        
        if current_status != 'DELIVERED':
            print("❌ 订单状态不正确，应该是DELIVERED")
            return
    
    # 8. 扫描二维码（模拟用户取包裹）
    print_step("8. 扫描二维码")
    qr_data = {
        "qr_data": f"order_{order_id}",
        "order_id": order_id
    }
    
    response = requests.post(f"{BASE_URL}/robots/1/qr_scanned/", json=qr_data)
    print_response(response, "扫描二维码")
    
    if response.status_code != 200:
        print("❌ 扫描二维码失败")
        return
    
    print("✅ 二维码扫描成功")
    
    # 9. 检查最终订单状态（应该是PICKED_UP）
    print_step("9. 检查最终订单状态（已取出）")
    response = requests.get(f"{BASE_URL}/orders/{order_id}/")
    print_response(response, "最终订单状态")
    
    if response.status_code == 200:
        order_status = response.json()
        final_status = order_status.get('status', '未知')
        print(f"✅ 最终订单状态: {final_status}")
        
        if final_status == 'PICKED_UP':
            print("🎉 完整流程测试成功！")
        else:
            print(f"❌ 最终状态不正确，期望PICKED_UP，实际{final_status}")

def test_timeout_workflow():
    """测试超时流程"""
    print("\n" + "="*60)
    print("🕐 开始测试超时流程")
    print("="*60)
    
    # 1. 创建新订单
    print_step("1. 创建新订单")
    order_data = {
        "student": 1,
        "package_description": "超时测试包裹",
        "pickup_location": "图书馆",
        "delivery_location": "宿舍楼",
        "status": "PENDING"
    }
    
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    print_response(response, "创建订单")
    
    if response.status_code != 201:
        print("❌ 创建订单失败")
        return
    
    order = response.json()
    order_id = order['id']
    print(f"✅ 订单创建成功，ID: {order_id}")
    
    # 2. 快速完成到DELIVERED状态
    print_step("2. 快速完成到DELIVERED状态")
    
    # 分配订单
    assign_data = {"status": "ASSIGNED"}
    response = requests.patch(f"{BASE_URL}/dispatch/orders/{order_id}/", json=assign_data)
    if response.status_code != 200:
        print("❌ 分配订单失败")
        return
    
    # 开始配送
    control_data = {"action": "start_delivery"}
    response = requests.post(f"{BASE_URL}/robots/1/control/", json=control_data)
    if response.status_code != 200:
        print("❌ 开始配送失败")
        return
    
    # 到达目的地
    arrived_data = {"order_id": order_id}
    response = requests.post(f"{BASE_URL}/robots/1/arrived_at_destination/", json=arrived_data)
    if response.status_code != 200:
        print("❌ 到达目的地失败")
        return
    
    print("✅ 订单状态已更新为DELIVERED")
    
    # 3. 模拟超时自动返航
    print_step("3. 模拟超时自动返航")
    auto_return_data = {}
    
    response = requests.post(f"{BASE_URL}/robots/1/auto_return/", json=auto_return_data)
    print_response(response, "自动返航")
    
    if response.status_code != 200:
        print("❌ 自动返航失败")
        return
    
    print("✅ 自动返航成功")
    
    # 4. 检查订单状态（应该是CANCELLED）
    print_step("4. 检查订单状态（已作废）")
    response = requests.get(f"{BASE_URL}/orders/{order_id}/")
    print_response(response, "超时订单状态")
    
    if response.status_code == 200:
        order_status = response.json()
        timeout_status = order_status.get('status', '未知')
        print(f"✅ 超时订单状态: {timeout_status}")
        
        if timeout_status == 'CANCELLED':
            print("🎉 超时流程测试成功！")
        else:
            print(f"❌ 超时状态不正确，期望CANCELLED，实际{timeout_status}")

if __name__ == "__main__":
    try:
        # 测试完整流程
        test_complete_workflow()
        
        # 测试超时流程
        test_timeout_workflow()
        
        print("\n" + "="*60)
        print("🎉 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc() 