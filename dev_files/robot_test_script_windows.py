#!/usr/bin/env python3
"""
🧪 机器人API测试脚本 - Windows版本
用于测试机器人与服务器的各种API交互

使用方法:
1. 安装依赖: pip install requests
2. 运行脚本: python robot_test_script_windows.py
3. 选择要测试的功能
"""

import requests
import json
import time

class RobotAPITester:
    def __init__(self, server_ip="192.168.110.148", robot_id=1):
        self.server_ip = server_ip
        self.robot_id = robot_id
        self.base_url = f"http://{server_ip}:8000/api"
        self.access_token = None
        
        print(f"🧪 机器人API测试器")
        print(f"📍 服务器: {self.base_url}")
        print(f"🆔 机器人ID: {self.robot_id}")
        print("=" * 50)
    
    def login(self, username="root", password="test123456"):
        """登录获取访问令牌"""
        try:
            print(f"🔐 尝试登录用户: {username}")
            response = requests.post(
                f"{self.base_url}/token/",
                json={"username": username, "password": password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                print(f"✅ 登录成功: {username}")
                return True
            else:
                print(f"❌ 登录失败: HTTP {response.status_code}")
                print(f"   错误响应: {response.text}")
                
                # 根据错误码提供具体建议
                if response.status_code == 401:
                    print("   💡 建议: 检查用户名和密码是否正确")
                elif response.status_code == 404:
                    print("   💡 建议: 检查API端点是否正确")
                elif response.status_code == 500:
                    print("   💡 建议: 服务器内部错误，请联系管理员")
                else:
                    print("   💡 建议: 检查网络连接和服务器状态")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接错误: 无法连接到服务器 {self.base_url}")
            print("   💡 建议: 检查服务器IP地址和端口是否正确")
            print("   💡 建议: 确保服务器正在运行")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ 超时错误: 请求超时")
            print("   💡 建议: 检查网络连接")
            return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            print("   💡 建议: 检查网络连接和服务器状态")
            return False
    
    def get_headers(self):
        """获取请求头"""
        if self.access_token:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        return {"Content-Type": "application/json"}
    
    def test_get_commands(self):
        """测试获取指令"""
        print("\n📥 测试获取指令...")
        try:
            response = requests.get(
                f"{self.base_url}/robots/{self.robot_id}/get_commands/",
                headers=self.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get("pending_commands", [])
                print(f"✅ 获取指令成功，共 {len(commands)} 条待执行指令")
                for cmd in commands:
                    print(f"   - {cmd['command_display']} (ID: {cmd['command_id']})")
                return True
            else:
                print(f"❌ 获取指令失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取指令异常: {e}")
            return False
    
    def test_execute_command(self, command_id, result="测试执行成功"):
        """测试执行指令"""
        print(f"\n🔄 测试执行指令 (ID: {command_id})...")
        try:
            response = requests.post(
                f"{self.base_url}/robots/{self.robot_id}/execute_command/",
                headers=self.get_headers(),
                json={
                    "command_id": command_id,
                    "result": result
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 指令执行成功: {result}")
                return True
            else:
                print(f"❌ 指令执行失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 执行指令异常: {e}")
            return False
    
    def test_arrived_at_destination(self, order_id=1):
        """测试到达目的地"""
        print(f"\n📍 测试到达目的地 (订单ID: {order_id})...")
        try:
            response = requests.post(
                f"{self.base_url}/robots/{self.robot_id}/arrived_at_destination/",
                headers=self.get_headers(),
                json={"order_id": order_id},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 到达目的地成功")
                return True
            else:
                print(f"❌ 到达目的地失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 到达目的地异常: {e}")
            return False
    
    def test_qr_scanned(self, order_id=1):
        """测试扫描二维码"""
        print(f"\n📱 测试扫描二维码 (订单ID: {order_id})...")
        try:
            response = requests.post(
                f"{self.base_url}/robots/{self.robot_id}/qr_scanned/",
                headers=self.get_headers(),
                json={
                    "qr_data": f"order_{order_id}",
                    "order_id": order_id
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 扫描二维码成功")
                return True
            else:
                print(f"❌ 扫描二维码失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 扫描二维码异常: {e}")
            return False
    
    def test_auto_return(self):
        """测试自动返航"""
        print(f"\n🏠 测试自动返航...")
        try:
            response = requests.post(
                f"{self.base_url}/robots/{self.robot_id}/auto_return/",
                headers=self.get_headers(),
                json={},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 自动返航成功")
                return True
            else:
                print(f"❌ 自动返航失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 自动返航异常: {e}")
            return False
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("\n🚀 开始完整测试流程...")
        
        # 1. 获取指令
        if not self.test_get_commands():
            return
        
        # 2. 如果有指令，执行第一个
        response = requests.get(
            f"{self.base_url}/robots/{self.robot_id}/get_commands/",
            headers=self.get_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            commands = data.get("pending_commands", [])
            
            if commands:
                first_command = commands[0]
                self.test_execute_command(first_command["command_id"])
        
        # 3. 测试到达目的地
        self.test_arrived_at_destination()
        
        # 4. 测试扫描二维码
        self.test_qr_scanned()
        
        # 5. 测试自动返航
        self.test_auto_return()
        
        print("\n✅ 完整测试流程完成!")
    
    def show_menu(self):
        """显示菜单"""
        print("\n📋 测试菜单:")
        print("1. 获取待执行指令")
        print("2. 执行指定指令")
        print("3. 测试到达目的地")
        print("4. 测试扫描二维码")
        print("5. 测试自动返航")
        print("6. 运行完整测试流程")
        print("0. 退出")
        print("-" * 30)
    
    def start(self):
        """启动测试器"""
        # 登录
        if not self.login():
            print("❌ 无法登录，请检查用户名密码")
            return
        
        while True:
            self.show_menu()
            choice = input("请选择测试项目 (0-6): ").strip()
            
            if choice == "0":
                print("👋 退出测试器")
                break
            elif choice == "1":
                self.test_get_commands()
            elif choice == "2":
                command_id = input("请输入指令ID: ").strip()
                if command_id.isdigit():
                    self.test_execute_command(int(command_id))
                else:
                    print("❌ 请输入有效的指令ID")
            elif choice == "3":
                order_id = input("请输入订单ID (默认: 1): ").strip()
                if not order_id:
                    order_id = 1
                else:
                    order_id = int(order_id)
                self.test_arrived_at_destination(order_id)
            elif choice == "4":
                order_id = input("请输入订单ID (默认: 1): ").strip()
                if not order_id:
                    order_id = 1
                else:
                    order_id = int(order_id)
                self.test_qr_scanned(order_id)
            elif choice == "5":
                self.test_auto_return()
            elif choice == "6":
                self.run_full_test()
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    print("🧪 机器人API测试器 - Windows版本")
    print("用于测试机器人与服务器的API交互")
    print()
    
    # 配置参数
    server_ip = input("请输入服务器IP地址 (默认: 192.168.110.148): ").strip()
    if not server_ip:
        server_ip = "192.168.110.148"
    
    robot_id = input("请输入机器人ID (默认: 1): ").strip()
    if not robot_id:
        robot_id = 1
    else:
        robot_id = int(robot_id)
    
    # 创建并启动测试器
    tester = RobotAPITester(server_ip, robot_id)
    tester.start()

if __name__ == "__main__":
    main() 