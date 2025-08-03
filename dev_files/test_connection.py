#!/usr/bin/env python3
"""
🔗 连接测试脚本
用于测试Windows电脑与服务器的连接
"""

import requests
import json

def test_connection(server_ip="192.168.110.148"):
    """测试与服务器的连接"""
    base_url = f"http://{server_ip}:8000/api"
    
    print(f"🔗 测试连接到: {base_url}")
    print("=" * 50)
    
    # 1. 测试服务器是否可达
    try:
        response = requests.get(f"http://{server_ip}:8000/", timeout=5)
        print(f"✅ 服务器可达: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务器不可达: {e}")
        return False
    
    # 2. 测试登录
    try:
        login_data = {
            "username": "root",
            "password": "test123456"
        }
        
        response = requests.post(
            f"{base_url}/token/",
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access")
            print(f"✅ 登录成功: root")
            print(f"   访问令牌: {access_token[:20]}...")
            
            # 3. 测试获取机器人信息
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{base_url}/robots/1/",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                robot_data = response.json()
                print(f"✅ 获取机器人信息成功")
                print(f"   机器人名称: {robot_data.get('name', 'N/A')}")
                print(f"   机器人状态: {robot_data.get('status', 'N/A')}")
            else:
                print(f"❌ 获取机器人信息失败: {response.status_code}")
            
            # 4. 测试获取指令
            response = requests.get(
                f"{base_url}/robots/1/get_commands/",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get("pending_commands", [])
                print(f"✅ 获取指令成功，共 {len(commands)} 条待执行指令")
            else:
                print(f"❌ 获取指令失败: {response.status_code}")
            
            return True
            
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🔗 连接测试工具")
    print("用于测试Windows电脑与服务器的连接")
    print()
    
    server_ip = input("请输入服务器IP地址 (默认: 192.168.110.148): ").strip()
    if not server_ip:
        server_ip = "192.168.110.148"
    
    success = test_connection(server_ip)
    
    if success:
        print("\n🎉 连接测试成功！")
        print("现在可以运行机器人模拟器了")
    else:
        print("\n❌ 连接测试失败！")
        print("请检查网络连接和服务器状态")

if __name__ == "__main__":
    main() 