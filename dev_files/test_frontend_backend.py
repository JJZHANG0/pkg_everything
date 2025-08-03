#!/usr/bin/env python3
"""
前后端集成测试脚本
测试机器人控制和订单管理功能
"""

import requests
import json
import time
from datetime import datetime

# 配置
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"

def log_test(message):
    """记录测试日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_backend_api():
    """测试后端API"""
    log_test("🔧 开始测试后端API...")
    
    # 1. 测试机器人状态
    try:
        response = requests.get(f"{API_BASE}/api/robots/1/status/")
        if response.status_code == 200:
            robot_status = response.json()
            log_test(f"✅ 机器人状态获取成功: {robot_status['status']}")
            return robot_status
        else:
            log_test(f"❌ 机器人状态获取失败: {response.status_code}")
            return None
    except Exception as e:
        log_test(f"❌ 机器人状态获取异常: {e}")
        return None

def test_robot_control():
    """测试机器人控制"""
    log_test("🤖 开始测试机器人控制...")
    
    # 1. 测试开门
    try:
        response = requests.post(f"{API_BASE}/api/robots/1/control/", 
                               json={"action": "open_door"})
        if response.status_code == 200:
            log_test("✅ 机器人开门成功")
        else:
            log_test(f"❌ 机器人开门失败: {response.json()}")
    except Exception as e:
        log_test(f"❌ 机器人开门异常: {e}")
    
    time.sleep(1)
    
    # 2. 测试关门
    try:
        response = requests.post(f"{API_BASE}/api/robots/1/control/", 
                               json={"action": "close_door"})
        if response.status_code == 200:
            log_test("✅ 机器人关门成功")
        else:
            log_test(f"❌ 机器人关门失败: {response.json()}")
    except Exception as e:
        log_test(f"❌ 机器人关门异常: {e}")

def test_order_workflow():
    """测试订单工作流程"""
    log_test("📦 开始测试订单工作流程...")
    
    # 1. 获取订单列表
    try:
        response = requests.get(f"{API_BASE}/api/dispatch/orders/")
        if response.status_code == 200:
            orders = response.json()
            log_test(f"✅ 获取订单列表成功，共 {len(orders)} 个订单")
            
            if orders:
                # 测试第一个订单的状态更新
                order = orders[0]
                order_id = order['id']
                
                # 更新订单状态为ASSIGNED（这会自动设置机器人为LOADING状态）
                response = requests.patch(
                    f"{API_BASE}/api/dispatch/orders/{order_id}/",
                    json={"status": "ASSIGNED"}
                )
                if response.status_code == 200:
                    log_test(f"✅ 订单 #{order_id} 状态更新为 ASSIGNED 成功")
                    
                    # 等待一下，然后尝试开始配送
                    time.sleep(2)
                    
                    # 现在机器人状态应该是LOADING，可以开始配送
                    response = requests.post(f"{API_BASE}/api/robots/1/control/", 
                                           json={"action": "start_delivery"})
                    if response.status_code == 200:
                        log_test("✅ 机器人开始配送成功")
                    else:
                        log_test(f"❌ 机器人开始配送失败: {response.json()}")
                else:
                    log_test(f"❌ 订单状态更新失败: {response.json()}")
            else:
                log_test("⚠️ 没有订单可测试")
        else:
            log_test(f"❌ 获取订单列表失败: {response.status_code}")
    except Exception as e:
        log_test(f"❌ 订单工作流程测试异常: {e}")

def test_system_logs():
    """测试系统日志"""
    log_test("📋 开始测试系统日志...")
    
    try:
        response = requests.get(f"{API_BASE}/api/logs/")
        if response.status_code == 200:
            logs = response.json()
            log_test(f"✅ 获取系统日志成功，共 {len(logs)} 条日志")
            
            # 显示最近的几条日志
            recent_logs = logs[:5]
            for log in recent_logs:
                log_test(f"   📝 {log.get('message', 'N/A')}")
        else:
            log_test(f"❌ 获取系统日志失败: {response.status_code}")
    except Exception as e:
        log_test(f"❌ 系统日志测试异常: {e}")

def main():
    """主测试函数"""
    log_test("🚀 开始前后端集成测试...")
    
    # 等待服务启动
    log_test("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 测试后端API
    robot_status = test_backend_api()
    
    if robot_status:
        # 测试机器人控制
        test_robot_control()
        
        # 测试订单工作流程
        test_order_workflow()
        
        # 测试系统日志
        test_system_logs()
    
    log_test("🎉 测试完成！")
    log_test("💡 提示：现在可以访问前端页面 http://localhost:3000 进行手动测试")

if __name__ == "__main__":
    main() 