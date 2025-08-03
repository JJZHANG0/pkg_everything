import qrcode
import base64
import json
import hashlib
from io import BytesIO
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY  # 🔐 用于签名

def generate_signed_payload(order_id, student_id, student_name=None, delivery_info=None):
    """
    构建签名数据结构：包含更多订单和用户信息
    """
    payload = {
        "order_id": order_id,
        "student_id": student_id,
        "student_name": student_name or "",
        "delivery_building": delivery_info.get('building', '') if delivery_info else '',
        "delivery_room": delivery_info.get('room', '') if delivery_info else '',
        "package_type": delivery_info.get('package_type', '') if delivery_info else ''
    }

    # ✅ 为了签名稳定性，保证 JSON key 顺序一致
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    # 🔐 使用 SECRET_KEY 生成签名
    signature = hashlib.sha256((payload_str + SECRET_KEY).encode()).hexdigest()

    return {
        "payload": base64.b64encode(payload_str.encode()).decode(),  # ✅ QR code 中用 base64 编码
        "signature": signature,
        "payload_data": payload_str  # 新增：返回解码后的数据用于存储
    }

def generate_simple_qr_code(order_id, student_id):
    """生成简单的二维码 - 只包含订单ID和学生ID"""
    # 简化的数据格式，只包含必要信息
    qr_data = {
        "order_id": order_id,
        "student_id": student_id
    }
    
    return json.dumps(qr_data, separators=(',', ':'))

def generate_qr_code(signed_data):
    """生成二维码图片 - 使用简化格式"""
    from PIL import Image
    import qrcode
    
    # 使用简化的数据格式
    qr_content = signed_data.get('payload_data', '')
    
    # 创建二维码，使用更大的格子尺寸和更宽松的设置
    qr = qrcode.QRCode(
        version=1,           # 使用最小版本
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 低纠错级别
        box_size=15,         # 增大格子尺寸
        border=8             # 增大边框
    )
    
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    # 生成图片
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 转换为base64
    import base64
    import io
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
