#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 HTTP API直接测试
绕过登录问题，直接测试后端HTTP API连接
"""

import requests
import json
import time

def test_backend_connection():
    """测试后端连接"""
    print("🌐 测试后端HTTP连接...")
    
    base_url = "http://localhost:8000"
    
    # 测试基本连接
    try:
        print(f"📡 连接到: {base_url}")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ 后端响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端 - 服务可能未启动")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 HTTP API直接连接测试")
    print("=" * 50)
    
    # 测试基本连接
    test_backend_connection()
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main() 