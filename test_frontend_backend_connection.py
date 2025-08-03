#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试前端和后端的连接
"""

import requests
import json

def test_backend_api():
    """测试后端API"""
    print("🔍 测试后端API连接...")
    
    # 测试API是否可访问
    try:
        response = requests.get("http://localhost:8000/api/token/", timeout=5)
        print(f"✅ API可访问，状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ API不可访问: {e}")
        return False
    
    # 测试登录API
    try:
        login_data = {
            "username": "root",
            "password": "root"
        }
        
        response = requests.post(
            "http://localhost:8000/api/token/",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"🔐 登录测试状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功，获取到token")
            print(f"📋 Access token: {data.get('access', '')[:50]}...")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def test_frontend_access():
    """测试前端访问"""
    print("\n🌐 测试前端访问...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"✅ 前端可访问，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 前端不可访问: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试前端和后端连接...")
    print("=" * 50)
    
    # 测试后端
    backend_ok = test_backend_api()
    
    # 测试前端
    frontend_ok = test_frontend_access()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"🔧 后端API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"🌐 前端页面: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有服务都正常运行！")
        print("💡 如果前端登录仍然失败，可能是浏览器CORS问题")
    else:
        print("\n⚠️ 存在问题，请检查Docker服务状态")

if __name__ == "__main__":
    main() 