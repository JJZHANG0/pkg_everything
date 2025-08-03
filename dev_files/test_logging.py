#!/usr/bin/env python3
"""
测试后端日志功能
验证日志是否同时写入数据库和文件
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

def test_robot_control_logging():
    """测试机器人控制日志"""
    log_test("🤖 开始测试机器人控制日志...")
    
    # 测试开门操作
    try:
        response = requests.post(f"{API_BASE}/api/robots/1/control/", 
                               json={"action": "open_door"})
        if response.status_code == 200:
            log_test("✅ 机器人开门成功，日志已记录")
        else:
            log_test(f"❌ 机器人开门失败: {response.json()}")
    except Exception as e:
        log_test(f"❌ 机器人开门异常: {e}")
    
    time.sleep(1)
    
    # 测试关门操作
    try:
        response = requests.post(f"{API_BASE}/api/robots/1/control/", 
                               json={"action": "close_door"})
        if response.status_code == 200:
            log_test("✅ 机器人关门成功，日志已记录")
        else:
            log_test(f"❌ 机器人关门失败: {response.json()}")
    except Exception as e:
        log_test(f"❌ 机器人关门异常: {e}")

def test_order_logging():
    """测试订单状态更新日志"""
    log_test("📦 开始测试订单状态更新日志...")
    
    # 获取订单列表
    try:
        response = requests.get(f"{API_BASE}/api/dispatch/orders/")
        if response.status_code == 200:
            orders = response.json()
            if orders:
                order = orders[0]
                order_id = order['id']
                
                # 更新订单状态
                response = requests.patch(
                    f"{API_BASE}/api/dispatch/orders/{order_id}/",
                    json={"status": "ASSIGNED"}
                )
                if response.status_code == 200:
                    log_test(f"✅ 订单 #{order_id} 状态更新为 ASSIGNED，日志已记录")
                else:
                    log_test(f"❌ 订单状态更新失败: {response.json()}")
            else:
                log_test("⚠️ 没有订单可测试")
        else:
            log_test(f"❌ 获取订单列表失败: {response.status_code}")
    except Exception as e:
        log_test(f"❌ 订单测试异常: {e}")

def check_log_files():
    """检查日志文件"""
    log_test("📋 检查日志文件...")
    
    import os
    
    # 检查后端日志文件
    backend_log_file = "logs/system_backend.log"
    if os.path.exists(backend_log_file):
        with open(backend_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            log_test(f"✅ 后端日志文件存在，共 {len(lines)} 行")
            if lines:
                log_test("📝 最近的日志内容:")
                for line in lines[-5:]:  # 显示最后5行
                    print(f"   {line.strip()}")
    else:
        log_test("❌ 后端日志文件不存在")
    
    # 检查前端日志文件
    frontend_log_file = "logs/frontend_operations.log"
    if os.path.exists(frontend_log_file):
        with open(frontend_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            log_test(f"✅ 前端日志文件存在，共 {len(lines)} 行")
    else:
        log_test("❌ 前端日志文件不存在")

def main():
    """主测试函数"""
    log_test("🚀 开始测试后端日志功能...")
    
    # 等待服务启动
    log_test("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 测试机器人控制日志
    test_robot_control_logging()
    
    # 测试订单日志
    test_order_logging()
    
    # 检查日志文件
    check_log_files()
    
    log_test("🎉 日志功能测试完成！")
    log_test("💡 现在可以查看 logs/system_backend.log 文件")

if __name__ == "__main__":
    main() 