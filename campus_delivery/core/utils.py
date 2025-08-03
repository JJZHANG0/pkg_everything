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

def generate_qr_code(data: dict) -> str:
    """
    生成二维码并返回 base64 编码 PNG 字符串
    :param data: dict，通常包含 payload(base64字符串) + signature
    :return: base64格式的 PNG 图像字符串（可直接用 <img src=...> 显示）
    """
    qr = qrcode.make(json.dumps(data, ensure_ascii=False))
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"
