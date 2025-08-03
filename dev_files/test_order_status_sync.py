#!/usr/bin/env python3
"""
测试订单状态与机器人状态同步
验证start_delivery操作是否正确更新订单状态
"""

import requests
import json
import time
from datetime import datetime

# 配置
API_BASE = "http://localhost:8000"

def log_test(message):
    """记录测试日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_order_status_sync():
    """测试订单状态同步"""
    log_test("🔄 开始测试订单状态与机器人状态同步...")
    
    # 1. 获取当前订单列表
    try:
        response = requests.get(f"{API_BASE}/api/dispatch/orders/")
        if response.status_code == 200:
            orders = response.json()
            log_test(f"✅ 获取订单列表成功，共 {len(orders)} 个订单")
            
            if orders:
                # 2. 检查订单状态
                for order in orders:
                    log_test(f"📦 订单 #{order['id']}: 状态={order['status']}, 机器人={order.get('robot', 'None')}")
                
                # 3. 将第一个订单状态设置为ASSIGNED（这会设置机器人为LOADING）
                order = orders[0]
                order_id = order['id']
                
                log_test(f"🔄 将订单 #{order_id} 状态设置为 ASSIGNED...")
                response = requests.patch(
                    f"{API_BASE}/api/dispatch/orders/{order_id}/",
                    json={"status": "ASSIGNED"}
                )
                
                if response.status_code == 200:
                    log_test("✅ 订单状态更新为 ASSIGNED 成功")
                    
                    # 4. 等待一下，然后检查机器人状态
                    time.sleep(2)
                    
                    # 5. 现在尝试开始配送
                    log_test("🚀 开始执行 start_delivery 操作...")
                    response = requests.post(f"{API_BASE}/api/robots/1/control/", 
                                           json={"action": "start_delivery"})
                    
                    if response.status_code == 200:
                        result = response.json()
                        log_test(f"✅ 机器人开始配送成功: {result['message']}")
                        
                        # 6. 等待一下，然后检查订单状态是否已更新
                        time.sleep(2)
                        
                        # 7. 重新获取订单列表，检查状态变化
                        response = requests.get(f"{API_BASE}/api/dispatch/orders/")
                        if response.status_code == 200:
                            updated_orders = response.json()
                            log_test("📋 检查订单状态更新:")
                            
                            for order in updated_orders:
                                status_icon = "✅" if order['status'] == 'DELIVERING' else "❌"
                                log_test(f"   {status_icon} 订单 #{order['id']}: {order['status']}")
                            
                            # 8. 检查机器人状态
                            log_test("🤖 检查机器人状态:")
                            response = requests.get(f"{API_BASE}/api/robots/1/status/")
                            if response.status_code == 200:
                                robot_status = response.json()
                                log_test(f"   🤖 机器人状态: {robot_status['status']}")
                            else:
                                log_test(f"   ❌ 获取机器人状态失败: {response.status_code}")
                        else:
                            log_test(f"❌ 重新获取订单列表失败: {response.status_code}")
                    else:
                        log_test(f"❌ 机器人开始配送失败: {response.json()}")
                else:
                    log_test(f"❌ 订单状态更新失败: {response.json()}")
            else:
                log_test("⚠️ 没有订单可测试")
        else:
            log_test(f"❌ 获取订单列表失败: {response.status_code}")
    except Exception as e:
        log_test(f"❌ 测试异常: {e}")

def main():
    """主测试函数"""
    log_test("🚀 开始测试订单状态同步功能...")
    
    # 等待服务启动
    log_test("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 测试订单状态同步
    test_order_status_sync()
    
    log_test("🎉 测试完成！")
    log_test("💡 现在可以访问前端页面 http://localhost:3000 进行手动测试")

if __name__ == "__main__":
    main() 