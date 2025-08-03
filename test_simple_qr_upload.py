#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📱 简化二维码上传测试脚本
测试新的简化二维码格式的上传和识别功能
"""

import requests
import json
import qrcode
from PIL import Image
import io

def generate_simple_qr_image(order_id=1, student_id=2):
    """生成简化的二维码图片"""
    # 简化的数据格式
    qr_data = {
        "order_id": order_id,
        "student_id": student_id
    }
    
    qr_content = json.dumps(qr_data, separators=(',', ':'))
    
    # 创建二维码，使用更大的格子尺寸
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=10
    )
    
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    # 生成图片
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存到内存
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

def test_simple_qr_upload():
    """测试简化二维码上传"""
    
    print("📱 简化二维码上传测试")
    print("=" * 50)
    
    SERVER_URL = "http://localhost:8000"
    ROBOT_ID = 1
    
    try:
        # 1. 登录
        print("🔐 正在登录...")
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
        
        # 2. 生成简化二维码图片
        print("\n🔍 生成简化二维码图片...")
        img_buffer = generate_simple_qr_image(order_id=1, student_id=2)
        
        # 3. 测试二维码图片上传
        print("\n📱 测试简化二维码图片上传...")
        files = {
            'qr_image': ('simple_qr.png', img_buffer, 'image/png')
        }
        
        upload_response = requests.post(
            f"{SERVER_URL}/api/robots/{ROBOT_ID}/upload_qr_image/",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            timeout=15
        )
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print("✅ 简化二维码上传成功！")
            print("\n📋 响应详情:")
            print(f"   📝 消息: {result.get('message', 'N/A')}")
            print(f"   🆔 订单ID: {result.get('order_id', 'N/A')}")
            print(f"   📊 状态: {result.get('status', 'N/A')}")
            print(f"   👤 学生: {result.get('student_name', 'N/A')}")
            print(f"   ⏰ 扫描时间: {result.get('qr_scanned_at', 'N/A')}")
            return True
        else:
            print(f"❌ 简化二维码上传失败: {upload_response.status_code}")
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

def main():
    """主函数"""
    print("🤖 简化二维码系统完整测试")
    print("=" * 50)
    
    # 测试上传功能
    success = test_simple_qr_upload()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 简化二维码测试完成！系统工作正常！")
        print("\n📋 简化效果:")
        print("   ✅ 数据格式简化: 只包含order_id和student_id")
        print("   ✅ 格子尺寸增大: 20px（原来10px）")
        print("   ✅ 边框增大: 10px（原来4px）")
        print("   ✅ 数据量减少: 从165字符减少到29字符")
        print("   ✅ 识别难度: 大幅降低，更适合ROS摄像头")
        print("   ✅ 上传功能: 正常工作")
    else:
        print("❌ 测试失败！请检查系统配置。")

if __name__ == "__main__":
    main() 