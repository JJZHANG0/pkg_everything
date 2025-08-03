#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔐 登录测试脚本
测试前端登录功能
"""

import requests
import json

def test_login():
    """测试登录功能"""
    print("🔐 开始登录测试...")
    
    # 测试数据
    test_users = [
        {"username": "root", "password": "test123456"},
        {"username": "7", "password": "test123456"},
        {"username": "5566", "password": "test123456"},
    ]
    
    base_url = "http://localhost:8000/api"
    
    for user in test_users:
        print(f"\n📝 测试用户: {user['username']}")
        
        try:
            # 测试登录
            response = requests.post(
                f"{base_url}/token/",
                json=user,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 登录成功!")
                print(f"Access Token: {data.get('access', '')[:50]}...")
                print(f"Refresh Token: {data.get('refresh', '')[:50]}...")
                
                # 测试使用token访问受保护的API
                headers = {"Authorization": f"Bearer {data['access']}"}
                user_response = requests.get(f"{base_url}/users/me/", headers=headers)
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print(f"✅ 用户信息获取成功: {user_data}")
                else:
                    print(f"❌ 用户信息获取失败: {user_response.status_code}")
                    
            else:
                print(f"❌ 登录失败: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求错误: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
    
    print("\n" + "="*50)
    print("🔍 测试完成!")

def test_frontend_login():
    """测试前端登录页面"""
    print("\n🌐 测试前端登录页面...")
    
    try:
        # 测试前端页面
        response = requests.get("http://localhost:3000", timeout=10)
        print(f"前端页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            
            # 检查是否包含登录相关的内容
            content = response.text.lower()
            if "login" in content or "登录" in content or "react" in content:
                print("✅ 页面内容正常")
            else:
                print("⚠️ 页面内容可能有问题")
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 前端测试错误: {e}")

if __name__ == "__main__":
    test_login()
    test_frontend_login() 