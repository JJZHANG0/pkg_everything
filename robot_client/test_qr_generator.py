#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import qrcode
import json
import os

def generate_test_qr_code():
    """生成测试用的二维码"""
    
    # 测试数据
    test_data = {
        "order_id": 1,
        "student_id": 2,
        "student_name": "张三",
        "delivery_building": "宿舍楼A",
        "delivery_room": "101",
        "package_type": "书籍",
        "signature": "abc123def456ghi789"
    }
    
    # 转换为JSON字符串
    json_data = json.dumps(test_data, ensure_ascii=False)
    
    # 创建二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)
    
    # 创建图像
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存图像
    filename = "test_qr_code.png"
    img.save(filename)
    
    print(f"✅ 测试二维码已生成: {filename}")
    print(f"📋 二维码数据: {json_data}")
    print(f"📱 请将此二维码展示给摄像头进行扫描测试")
    
    return filename

if __name__ == "__main__":
    generate_test_qr_code() 