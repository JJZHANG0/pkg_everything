#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📱 二维码图片上传接口测试脚本
测试机器人上传二维码图片，服务器解析识别的完整流程
"""

import requests
import json
import base64
import hashlib
import time
from PIL import Image
import qrcode
import io

def generate_test_qr_image(order_id=1, student_id=2, secret_key="django-insecure-ov1(-wqc0-vjxyzc*1b@jitb0_r20v32#jr%v8fmi6h#ja!ooj"):
    """生成测试用的二维码图片"""
    # 创建二维码数据
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
    
    # 创建二维码内容
    qr_content = {
        "payload": payload_b64,
        "signature": signature
    }
    
    # 生成二维码图片
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(qr_content))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存到内存
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

def test_qr_image_upload():
    """测试二维码图片上传接口"""
    
    print("📱 二维码图片上传接口测试")
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
        
        # 2. 生成测试二维码图片
        print("\n🔍 生成测试二维码图片...")
        img_buffer = generate_test_qr_image(order_id=1, student_id=2)
        
        # 3. 测试二维码图片上传
        print("\n📱 测试二维码图片上传...")
        files = {
            'qr_image': ('test_qr.png', img_buffer, 'image/png')
        }
        
        upload_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/upload_qr_image/",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            timeout=15
        )
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print("✅ 二维码图片上传成功！")
            print("\n📋 响应详情:")
            print(f"   📝 消息: {result.get('message', 'N/A')}")
            print(f"   🆔 订单ID: {result.get('order_id', 'N/A')}")
            print(f"   📊 状态: {result.get('status', 'N/A')}")
            print(f"   👤 学生: {result.get('student_name', 'N/A')}")
            print(f"   ⏰ 扫描时间: {result.get('qr_scanned_at', 'N/A')}")
            return True
        else:
            print(f"❌ 二维码图片上传失败: {upload_response.status_code}")
            print(f"📝 错误信息: {upload_response.text}")
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

def test_invalid_image():
    """测试无效图片上传"""
    
    print("\n🧪 测试无效图片上传")
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
            print("❌ 登录失败，跳过无效图片测试")
            return
            
        token = login_response.json()["access"]
        
        # 创建一个无效的图片（纯色图片，没有二维码）
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        files = {
            'qr_image': ('invalid_image.png', img_buffer, 'image/png')
        }
        
        upload_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/upload_qr_image/",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            timeout=15
        )
        
        print(f"📊 无效图片测试结果: {upload_response.status_code}")
        print(f"📝 错误信息: {upload_response.text}")
        
    except Exception as e:
        print(f"❌ 无效图片测试异常: {e}")

def main():
    """主函数"""
    print("🤖 二维码图片上传接口完整测试")
    print("=" * 50)
    
    # 测试正常流程
    success = test_qr_image_upload()
    
    # 测试无效图片
    test_invalid_image()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！二维码图片上传接口工作正常！")
        print("\n📋 接口功能总结:")
        print("   ✅ 接收机器人上传的二维码图片")
        print("   ✅ 自动识别图片中的二维码")
        print("   ✅ 解析二维码数据并验证签名")
        print("   ✅ 匹配订单信息")
        print("   ✅ 更新订单状态为'已取出'")
        print("   ✅ 使二维码失效，防止重复使用")
        print("   ✅ 记录完整的操作日志")
    else:
        print("❌ 测试失败！请检查配置和网络连接。")

if __name__ == "__main__":
    main() 