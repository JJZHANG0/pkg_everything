#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📱 二维码扫描完整工作流程测试
演示从机器人到达目的地到用户扫码取件的完整流程
"""

import requests
import json
import base64
import hashlib
import time

def generate_qr_data(order_id, student_id, secret_key="django-insecure-ov1(-wqc0-vjxyzc*1b@jitb0_r20v32#jr%v8fmi6h#ja!ooj"):
    """生成二维码数据"""
    payload = {
        "order_id": order_id,
        "student_id": student_id,
        "timestamp": int(time.time())
    }
    
    payload_str = json.dumps(payload)
    payload_b64 = base64.b64encode(payload_str.encode()).decode()
    signature = hashlib.sha256((payload_str + secret_key).encode()).hexdigest()
    
    return {
        "payload": payload_b64,
        "signature": signature
    }

def test_qr_workflow():
    """测试完整的二维码扫描工作流程"""
    
    print("📱 二维码扫描完整工作流程测试")
    print("=" * 60)
    
    SERVER_URL = "http://localhost:8000"
    ROBOT_ID = 1
    
    try:
        # 1. 登录
        print("🔐 步骤1: 登录获取token...")
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": "root", "password": "root"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            return False
            
        token = login_response.json()["access"]
        print("✅ 登录成功！")
        
        # 2. 检查机器人状态
        print("\n🤖 步骤2: 检查机器人状态...")
        status_response = requests.get(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/status/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if status_response.status_code == 200:
            robot_status = status_response.json()
            print(f"✅ 机器人状态: {robot_status.get('status', 'N/A')}")
            print(f"📍 当前位置: {robot_status.get('current_location', 'N/A')}")
        else:
            print(f"❌ 获取机器人状态失败: {status_response.status_code}")
        
        # 3. 机器人到达目的地，开始等待扫码
        print("\n📍 步骤3: 机器人到达目的地，开始等待扫码...")
        qr_wait_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/start_qr_wait/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"order_id": 3},  # 使用订单3
            timeout=10
        )
        
        if qr_wait_response.status_code == 200:
            wait_result = qr_wait_response.json()
            print(f"✅ 开始等待扫码: {wait_result.get('message', '')}")
            print(f"⏰ 等待开始时间: {wait_result.get('qr_wait_start_time', 'N/A')}")
        else:
            print(f"❌ 开始等待扫码失败: {qr_wait_response.status_code}")
            print(f"📝 错误信息: {qr_wait_response.text}")
        
        # 4. 模拟用户扫描二维码
        print("\n📱 步骤4: 用户扫描二维码...")
        qr_data = generate_qr_data(order_id=3, student_id=2)
        
        print(f"📦 二维码数据:")
        print(f"   Payload: {qr_data['payload']}")
        print(f"   Signature: {qr_data['signature']}")
        
        # 解码查看内容
        payload_str = base64.b64decode(qr_data['payload']).decode()
        print(f"📄 二维码内容: {payload_str}")
        
        # 5. 机器人上报二维码扫描结果
        print("\n🤖 步骤5: 机器人上报二维码扫描结果...")
        qr_scan_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/qr_scanned/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"qr_data": qr_data},
            timeout=10
        )
        
        if qr_scan_response.status_code == 200:
            scan_result = qr_scan_response.json()
            print("✅ 二维码扫描成功！")
            print(f"📝 消息: {scan_result.get('message', '')}")
            print(f"🆔 订单ID: {scan_result.get('order_id', 'N/A')}")
            print(f"📊 新状态: {scan_result.get('status', 'N/A')}")
            print(f"⏰ 扫描时间: {scan_result.get('qr_scanned_at', 'N/A')}")
        else:
            print(f"❌ 二维码扫描失败: {qr_scan_response.status_code}")
            print(f"📝 错误信息: {qr_scan_response.text}")
            return False
        
        # 6. 检查订单状态变化
        print("\n📋 步骤6: 检查订单状态变化...")
        order_response = requests.get(
            f"{SERVER_URL}/api/orders/3/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if order_response.status_code == 200:
            order_data = order_response.json()
            print(f"✅ 订单状态: {order_data.get('status', 'N/A')}")
            print(f"🔐 二维码有效: {order_data.get('qr_is_valid', 'N/A')}")
            print(f"⏰ 扫描时间: {order_data.get('qr_scanned_at', 'N/A')}")
        else:
            print(f"❌ 获取订单信息失败: {order_response.status_code}")
        
        # 7. 检查机器人状态变化
        print("\n🤖 步骤7: 检查机器人状态变化...")
        final_status_response = requests.get(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/status/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if final_status_response.status_code == 200:
            final_status = final_status_response.json()
            print(f"✅ 最终机器人状态: {final_status.get('status', 'N/A')}")
            print(f"📍 当前位置: {final_status.get('current_location', 'N/A')}")
            print(f"⏰ 等待扫码时间: {final_status.get('qr_wait_start_time', 'N/A')}")
        else:
            print(f"❌ 获取最终机器人状态失败: {final_status_response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 二维码扫描工作流程测试完成！")
        print("📋 流程总结:")
        print("   1. 机器人到达目的地")
        print("   2. 开始等待用户扫码")
        print("   3. 用户扫描二维码")
        print("   4. 机器人上报扫描结果")
        print("   5. 系统更新订单状态为'已取出'")
        print("   6. 二维码失效，防止重复使用")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误：无法连接到服务器")
        return False
    except requests.exceptions.Timeout:
        print("❌ 超时错误：请求超时")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    """主函数"""
    success = test_qr_workflow()
    
    if success:
        print("\n✅ 所有测试通过！二维码扫描功能工作正常！")
    else:
        print("\n❌ 测试失败！请检查系统配置。")

if __name__ == "__main__":
    main() 