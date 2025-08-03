#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📱 二维码扫描API测试脚本
测试机器人扫描二维码并上报结果的完整流程
"""

import requests
import json
import base64
import hashlib
import time

def generate_test_qr_data(order_id=1, student_id=3, secret_key="django-insecure-ov1(-wqc0-vjxyzc*1b@jitb0_r20v32#jr%v8fmi6h#ja!ooj"):
    """生成测试用的二维码数据"""
    # 创建payload
    payload = {
        "order_id": order_id,
        "student_id": student_id,
        "timestamp": int(time.time())
    }
    
    # 编码payload
    payload_str = json.dumps(payload)
    payload_b64 = base64.b64encode(payload_str.encode()).decode()
    
    # 生成签名
    signature = hashlib.sha256((payload_str + secret_key).encode()).hexdigest()
    
    return {
        "payload": payload_b64,
        "signature": signature
    }

def test_qr_scan_api():
    """测试二维码扫描API"""
    
    print("📱 二维码扫描API测试")
    print("=" * 50)
    
    # 配置
    SERVER_URL = "http://localhost:8000"
    ROBOT_ID = 1
    
    try:
        # 1. 登录获取token
        print("🔐 正在登录...")
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": "root", "password": "root"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"📝 错误信息: {login_response.text}")
            return False
            
        token = login_response.json()["access"]
        print("✅ 登录成功！")
        
        # 2. 生成测试二维码数据
        print("\n🔍 生成测试二维码数据...")
        qr_data = generate_test_qr_data(order_id=2, student_id=2)
        print(f"📦 Payload (base64): {qr_data['payload']}")
        print(f"🔏 Signature: {qr_data['signature']}")
        
        # 解码payload查看内容
        payload_str = base64.b64decode(qr_data['payload']).decode()
        print(f"📄 解码后的payload: {payload_str}")
        
        # 3. 测试二维码扫描API
        print("\n📱 测试二维码扫描API...")
        qr_message = {
            "qr_data": qr_data
        }
        
        scan_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/qr_scanned/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=qr_message,
            timeout=10
        )
        
        if scan_response.status_code == 200:
            result = scan_response.json()
            print("✅ 二维码扫描成功！")
            print("\n📋 响应详情:")
            print(f"   📝 消息: {result.get('message', 'N/A')}")
            print(f"   🆔 订单ID: {result.get('order_id', 'N/A')}")
            print(f"   📊 状态: {result.get('status', 'N/A')}")
            print(f"   ⏰ 扫描时间: {result.get('qr_scanned_at', 'N/A')}")
            return True
        else:
            print(f"❌ 二维码扫描失败: {scan_response.status_code}")
            print(f"📝 错误信息: {scan_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误：无法连接到服务器")
        return False
    except requests.exceptions.Timeout:
        print("❌ 超时错误：请求超时")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_invalid_qr_data():
    """测试无效的二维码数据"""
    
    print("\n🧪 测试无效二维码数据")
    print("=" * 30)
    
    SERVER_URL = "http://localhost:8000"
    ROBOT_ID = 1
    
    try:
        # 登录
        login_response = requests.post(
            f"{SERVER_URL}/api/token/",
            headers={"Content-Type": "application/json"},
            json={"username": "root", "password": "root"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ 登录失败，跳过无效数据测试")
            return
            
        token = login_response.json()["access"]
        
        # 测试无效的二维码数据
        invalid_qr_data = {
            "payload": "invalid_base64_data",
            "signature": "invalid_signature"
        }
        
        qr_message = {
            "qr_data": invalid_qr_data
        }
        
        scan_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/qr_scanned/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=qr_message,
            timeout=10
        )
        
        print(f"📊 无效数据测试结果: {scan_response.status_code}")
        print(f"📝 错误信息: {scan_response.text}")
        
    except Exception as e:
        print(f"❌ 无效数据测试异常: {e}")

def main():
    """主函数"""
    print("🤖 二维码扫描API完整测试")
    print("=" * 50)
    
    # 测试正常流程
    success = test_qr_scan_api()
    
    # 测试无效数据
    test_invalid_qr_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！二维码扫描API工作正常！")
    else:
        print("❌ 测试失败！请检查配置和网络连接。")

if __name__ == "__main__":
    main() 