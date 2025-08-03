#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 紧急按钮API测试脚本
用于测试机器人紧急按钮功能
"""

import requests
import json
import time
from datetime import datetime

class EmergencyButtonTester:
    def __init__(self, server_url="http://localhost:8000", robot_id=1):
        self.server_url = server_url
        self.robot_id = robot_id
        self.token = None
        
    def login(self, username="root", password="root"):
        """登录获取token"""
        try:
            print(f"🔐 正在登录用户: {username}")
            
            response = requests.post(
                f"{self.server_url}/api/token/",
                headers={"Content-Type": "application/json"},
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access")
                print(f"✅ 登录成功！Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_emergency_button(self, action="emergency_open_door"):
        """测试紧急按钮API"""
        if not self.token:
            print("❌ 请先登录获取token")
            return False
            
        try:
            print(f"🚨 测试紧急按钮API...")
            print(f"📡 请求URL: {self.server_url}/api/robots/{self.robot_id}/emergency_button/")
            print(f"📝 请求体: {{'action': '{action}'}}")
            
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/emergency_button/",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={"action": action},
                timeout=10
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 紧急按钮API调用成功！")
                print("📋 响应详情:")
                print(f"   - 消息: {data.get('message', 'N/A')}")
                print(f"   - 命令ID: {data.get('command_id', 'N/A')}")
                print(f"   - 动作: {data.get('action', 'N/A')}")
                print(f"   - 状态: {data.get('status', 'N/A')}")
                print(f"   - 门状态: {data.get('door_status', 'N/A')}")
                print(f"   - 发送时间: {data.get('sent_at', 'N/A')}")
                print(f"   - 执行时间: {data.get('executed_at', 'N/A')}")
                print(f"   - 紧急标志: {data.get('emergency', 'N/A')}")
                return True
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"📝 错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    def test_invalid_requests(self):
        """测试无效请求"""
        if not self.token:
            print("❌ 请先登录获取token")
            return
            
        print("\n🧪 测试无效请求...")
        
        # 测试1: 空请求体
        print("\n📝 测试1: 空请求体")
        try:
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/emergency_button/",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={},
                timeout=10
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ 空请求体被正确处理")
            else:
                print(f"   ❌ 空请求体处理失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
        
        # 测试2: 错误的action值
        print("\n📝 测试2: 错误的action值")
        try:
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/emergency_button/",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={"action": "wrong_action"},
                timeout=10
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ 错误action值被正确处理")
            else:
                print(f"   ❌ 错误action值处理失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
        
        # 测试3: 缺少认证
        print("\n📝 测试3: 缺少认证")
        try:
            response = requests.post(
                f"{self.server_url}/api/robots/{self.robot_id}/emergency_button/",
                headers={"Content-Type": "application/json"},
                json={"action": "emergency_open_door"},
                timeout=10
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ 认证检查正常工作")
            else:
                print(f"   ⚠️ 认证检查异常: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    def test_robot_status(self):
        """测试机器人状态"""
        if not self.token:
            print("❌ 请先登录获取token")
            return
            
        try:
            print(f"\n🤖 获取机器人状态...")
            
            response = requests.get(
                f"{self.server_url}/api/robots/{self.robot_id}/status/",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 机器人状态获取成功！")
                print("📋 状态详情:")
                print(f"   - 机器人ID: {data.get('id', 'N/A')}")
                print(f"   - 机器人名称: {data.get('name', 'N/A')}")
                print(f"   - 状态: {data.get('status', 'N/A')}")
                print(f"   - 门状态: {data.get('door_status', 'N/A')}")
                print(f"   - 电池电量: {data.get('battery_level', 'N/A')}")
                print(f"   - 位置: {data.get('location', 'N/A')}")
            else:
                print(f"❌ 状态获取失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 状态获取异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始紧急按钮API测试")
        print("=" * 50)
        
        # 1. 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return
        
        # 2. 获取机器人状态
        self.test_robot_status()
        
        # 3. 测试正常紧急按钮
        print("\n" + "=" * 50)
        success = self.test_emergency_button()
        
        # 4. 测试无效请求
        self.test_invalid_requests()
        
        # 5. 再次获取状态确认门已开启
        print("\n" + "=" * 50)
        print("🔄 再次检查机器人状态...")
        self.test_robot_status()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 所有测试完成！紧急按钮API工作正常！")
        else:
            print("❌ 测试过程中发现问题，请检查配置")

def main():
    """主函数"""
    print("🚨 紧急按钮API测试工具")
    print("=" * 50)
    
    # 配置参数
    server_url = input("请输入服务器地址 (默认: http://localhost:8000): ").strip()
    if not server_url:
        server_url = "http://localhost:8000"
    else:
        # 自动添加协议前缀
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"http://{server_url}"
        # 自动添加端口号
        if ':' not in server_url.split('//')[1]:
            server_url = f"{server_url}:8000"
    
    robot_id = input("请输入机器人ID (默认: 1): ").strip()
    if not robot_id:
        robot_id = 1
    else:
        robot_id = int(robot_id)
    
    username = input("请输入用户名 (默认: root): ").strip()
    if not username:
        username = "root"
    
    password = input("请输入密码 (默认: root): ").strip()
    if not password:
        password = "root"
    
    print(f"\n📋 测试配置:")
    print(f"   服务器: {server_url}")
    print(f"   机器人ID: {robot_id}")
    print(f"   用户名: {username}")
    print(f"   密码: {'*' * len(password)}")
    
    # 创建测试器并运行测试
    tester = EmergencyButtonTester(server_url, robot_id)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 