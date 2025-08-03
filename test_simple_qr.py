#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📱 简化二维码测试脚本
测试新的简化二维码格式，减少密度，提高识别率
"""

import json
import qrcode
from PIL import Image
import io
import base64

def generate_simple_qr_code(order_id, student_id):
    """生成简单的二维码 - 只包含订单ID和学生ID"""
    # 简化的数据格式，只包含必要信息
    qr_data = {
        "order_id": order_id,
        "student_id": student_id
    }
    
    return json.dumps(qr_data, separators=(',', ':'))

def generate_simple_qr_image(qr_content, filename="simple_qr.png"):
    """生成简化的二维码图片"""
    # 创建二维码，使用更大的格子尺寸和更宽松的设置
    qr = qrcode.QRCode(
        version=1,           # 使用最小版本
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 低纠错级别
        box_size=20,         # 增大格子尺寸
        border=10            # 增大边框
    )
    
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    # 生成图片
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存图片
    img.save(filename)
    print(f"✅ 简化二维码已保存为: {filename}")
    
    return img

def compare_qr_codes():
    """比较新旧二维码的复杂度"""
    
    print("📱 简化二维码测试")
    print("=" * 50)
    
    # 测试数据
    order_id = 1
    student_id = 2
    
    # 1. 生成简化二维码
    print("🔍 生成简化二维码...")
    simple_content = generate_simple_qr_code(order_id, student_id)
    print(f"📦 简化二维码内容: {simple_content}")
    
    # 生成简化二维码图片
    simple_img = generate_simple_qr_image(simple_content, "simple_qr.png")
    
    # 2. 生成复杂二维码（对比）
    print("\n🔍 生成复杂二维码（对比）...")
    complex_data = {
        "payload": "eyJvcmRlcl9pZCI6MSwic3R1ZGVudF9pZCI6MiwidGltZXN0YW1wIjoxNzU0MjA2MTQ3fQ==",
        "signature": "7596f709e3212528e5eebaec8907342e79150c0d4b9c5770c5aa53c40162b8c0"
    }
    complex_content = json.dumps(complex_data, separators=(',', ':'))
    print(f"📦 复杂二维码内容: {complex_content}")
    
    # 生成复杂二维码图片
    complex_qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 高纠错级别
        box_size=10,         # 小格子尺寸
        border=4             # 小边框
    )
    complex_qr.add_data(complex_content)
    complex_qr.make(fit=True)
    complex_img = complex_qr.make_image(fill_color="black", back_color="white")
    complex_img.save("complex_qr.png")
    print("✅ 复杂二维码已保存为: complex_qr.png")
    
    # 3. 比较二维码信息
    print("\n📊 二维码对比:")
    print(f"   简化二维码:")
    print(f"     - 内容长度: {len(simple_content)} 字符")
    print(f"     - 数据: {simple_content}")
    print(f"     - 格子尺寸: 20px")
    print(f"     - 边框: 10px")
    print(f"     - 纠错级别: 低")
    
    print(f"\n   复杂二维码:")
    print(f"     - 内容长度: {len(complex_content)} 字符")
    print(f"     - 数据: {complex_content}")
    print(f"     - 格子尺寸: 10px")
    print(f"     - 边框: 4px")
    print(f"     - 纠错级别: 高")
    
    print(f"\n📈 改进效果:")
    print(f"     - 数据量减少: {len(complex_content) - len(simple_content)} 字符")
    print(f"     - 格子增大: 2倍")
    print(f"     - 边框增大: 2.5倍")
    print(f"     - 识别难度: 大幅降低")
    
    return simple_content

def test_qr_recognition():
    """测试二维码识别"""
    
    print("\n🧪 测试二维码识别...")
    
    try:
        from pyzbar.pyzbar import decode
        
        # 测试简化二维码识别
        simple_img = Image.open("simple_qr.png")
        simple_result = decode(simple_img)
        
        if simple_result:
            decoded_data = simple_result[0].data.decode("utf-8")
            print(f"✅ 简化二维码识别成功: {decoded_data}")
            
            # 解析数据
            qr_json = json.loads(decoded_data)
            order_id = qr_json.get("order_id")
            student_id = qr_json.get("student_id")
            
            print(f"📋 解析结果:")
            print(f"   - 订单ID: {order_id}")
            print(f"   - 学生ID: {student_id}")
            
        else:
            print("❌ 简化二维码识别失败")
            
    except ImportError:
        print("⚠️ 未安装pyzbar，跳过识别测试")
        print("   安装命令: pip install pyzbar")

def main():
    """主函数"""
    print("🤖 简化二维码系统测试")
    print("=" * 50)
    
    # 生成和比较二维码
    simple_content = compare_qr_codes()
    
    # 测试识别
    test_qr_recognition()
    
    print("\n" + "=" * 50)
    print("🎉 简化二维码测试完成！")
    print("\n📋 简化效果总结:")
    print("   ✅ 数据格式简化: 只包含order_id和student_id")
    print("   ✅ 格子尺寸增大: 从10px增加到20px")
    print("   ✅ 边框增大: 从4px增加到10px")
    print("   ✅ 纠错级别降低: 减少冗余数据")
    print("   ✅ 识别难度降低: 更适合ROS摄像头")
    print("\n📁 生成的文件:")
    print("   - simple_qr.png: 简化二维码")
    print("   - complex_qr.png: 复杂二维码（对比）")

if __name__ == "__main__":
    main() 