#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模拟浏览器请求测试
"""

import requests
import json

def test_browser_simulation():
    """模拟浏览器请求"""
    print("🌐 模拟浏览器请求测试...")
    
    # 模拟浏览器的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000',
        'Referer': 'http://localhost:3000/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    
    # 测试OPTIONS请求（CORS预检）
    print("🔍 测试CORS预检请求...")
    try:
        response = requests.options(
            "http://localhost:8000/api/token/",
            headers=headers,
            timeout=5
        )
        print(f"✅ OPTIONS请求成功，状态码: {response.status_code}")
        print(f"📋 CORS头: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ OPTIONS请求失败: {e}")
        return False
    
    # 测试POST请求
    print("\n🔍 测试POST登录请求...")
    try:
        login_data = {
            "username": "root",
            "password": "root"
        }
        
        response = requests.post(
            "http://localhost:8000/api/token/",
            json=login_data,
            headers=headers,
            timeout=5
        )
        
        print(f"✅ POST请求成功，状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功，获取到token")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ POST请求失败: {e}")
        return False

def test_different_urls():
    """测试不同的URL格式"""
    print("\n🔍 测试不同的URL格式...")
    
    urls_to_test = [
        "http://localhost:8000/api/token/",
        "http://127.0.0.1:8000/api/token/",
        "http://0.0.0.0:8000/api/token/",
    ]
    
    for url in urls_to_test:
        print(f"\n📡 测试URL: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ 可访问，状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 不可访问: {e}")

def main():
    """主函数"""
    print("🚀 开始模拟浏览器请求测试...")
    print("=" * 50)
    
    # 测试浏览器模拟请求
    browser_ok = test_browser_simulation()
    
    # 测试不同URL
    test_different_urls()
    
    print("\n" + "=" * 50)
    if browser_ok:
        print("🎉 浏览器模拟请求成功！")
        print("💡 如果前端仍然失败，可能是其他网络问题")
    else:
        print("⚠️ 浏览器模拟请求失败")

if __name__ == "__main__":
    main() 