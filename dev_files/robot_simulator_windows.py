#!/usr/bin/env python3
"""
🤖 机器人模拟器 - Windows版本
用于在Windows电脑上模拟机器人，与服务器进行通信测试

使用方法:
1. 安装依赖: pip install requests
2. 运行脚本: python robot_simulator_windows.py
3. 在服务器端发送控制指令，观察机器人响应
"""

import requests
import json
import time
import threading
from datetime import datetime

class RobotSimulator:
    def __init__(self, server_ip="192.168.110.148", robot_id=1):
        self.server_ip = server_ip
        self.robot_id = robot_id
        self.base_url = f"http://{server_ip}:8000/api"
        self.running = False
        self.access_token = None
        
        # 机器人状态
        self.status = "IDLE"
        self.door_status = "CLOSED"
        self.current_location = "ORIGIN"
        self.battery_level = 100
        
        print(f"🤖 机器人模拟器启动")
        print(f"📍 服务器地址: {self.base_url}")
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
    
    def get_commands(self):
        """获取待执行的指令"""
        try:
            response = requests.get(
                f"{self.base_url}/robots/{self.robot_id}/get_commands/",
                headers=self.get_headers(),
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get("pending_commands", [])
                if commands:
                    print(f"📥 收到 {len(commands)} 条新指令")
                    return commands
            elif response.status_code == 401:
                print(f"❌ 获取指令失败: HTTP 401 - 认证失败")
                print("   💡 建议: 重新登录获取新的访问令牌")
            elif response.status_code == 404:
                print(f"❌ 获取指令失败: HTTP 404 - 机器人不存在")
                print(f"   💡 建议: 检查机器人ID {self.robot_id} 是否正确")
            else:
                print(f"❌ 获取指令失败: HTTP {response.status_code}")
                print(f"   错误响应: {response.text}")
            return []
            
        except requests.exceptions.ConnectionError:
            print(f"❌ 获取指令连接错误: 无法连接到服务器")
            return []
        except requests.exceptions.Timeout:
            print(f"❌ 获取指令超时: 请求超时")
            return []
        except Exception as e:
            print(f"❌ 获取指令异常: {e}")
            return []
    
    def execute_command(self, command_id, command_type, result="执行成功"):
        """执行指令并报告结果"""
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
                print(f"✅ 指令执行完成: {command_type}")
                return True
            elif response.status_code == 401:
                print(f"❌ 指令执行失败: HTTP 401 - 认证失败")
                print("   💡 建议: 重新登录获取新的访问令牌")
            elif response.status_code == 404:
                print(f"❌ 指令执行失败: HTTP 404 - 指令或机器人不存在")
                print(f"   💡 建议: 检查指令ID {command_id} 和机器人ID {self.robot_id}")
            elif response.status_code == 400:
                print(f"❌ 指令执行失败: HTTP 400 - 请求参数错误")
                print(f"   错误响应: {response.text}")
            else:
                print(f"❌ 指令执行失败: HTTP {response.status_code}")
                print(f"   错误响应: {response.text}")
            return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 执行指令连接错误: 无法连接到服务器")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ 执行指令超时: 请求超时")
            return False
        except Exception as e:
            print(f"❌ 执行指令异常: {e}")
            return False
    
    def simulate_command_execution(self, command):
        """模拟指令执行过程"""
        command_id = command["command_id"]
        command_type = command["command"]
        command_display = command["command_display"]
        
        print(f"\n🔄 开始执行指令: {command_display}")
        
        # 模拟不同类型的指令执行
        if command_type == "open_door":
            print("🚪 正在开门...")
            time.sleep(2)
            self.door_status = "OPEN"
            result = "门已打开"
            
        elif command_type == "close_door":
            print("🚪 正在关门...")
            time.sleep(2)
            self.door_status = "CLOSED"
            result = "门已关闭"
            
        elif command_type == "start_delivery":
            print("🚀 开始配送...")
            time.sleep(3)
            self.status = "DELIVERING"
            self.current_location = "DELIVERING"
            result = "开始配送成功"
            
        elif command_type == "stop_robot":
            print("⏹️ 停止机器人...")
            time.sleep(2)
            self.status = "IDLE"
            self.current_location = "ORIGIN"
            result = "机器人已停止"
            
        elif command_type == "arrived_at_destination":
            print("📍 到达目的地...")
            time.sleep(2)
            self.status = "WAITING"
            self.current_location = "Lauridsen Barrack"
            result = "已到达目的地"
            
        elif command_type == "auto_return":
            print("🏠 自动返航...")
            time.sleep(3)
            self.status = "RETURNING"
            self.current_location = "ORIGIN"
            result = "自动返航完成"
            
        else:
            print(f"❓ 未知指令类型: {command_type}")
            result = "未知指令"
        
        # 报告执行结果
        self.execute_command(command_id, command_type, result)
        
        # 显示当前状态
        self.show_status()
    
    def show_status(self):
        """显示当前状态"""
        print(f"\n📊 当前状态:")
        print(f"   状态: {self.status}")
        print(f"   门: {self.door_status}")
        print(f"   位置: {self.current_location}")
        print(f"   电量: {self.battery_level}%")
        print("-" * 30)
    
    def start_polling(self):
        """开始轮询指令"""
        self.running = True
        print("🔄 开始轮询指令...")
        
        while self.running:
            try:
                commands = self.get_commands()
                
                for command in commands:
                    self.simulate_command_execution(command)
                
                # 每5秒轮询一次
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n⏹️ 停止轮询")
                self.running = False
                break
            except Exception as e:
                print(f"❌ 轮询异常: {e}")
                time.sleep(5)
    
    def start(self):
        """启动机器人模拟器"""
        # 登录
        if not self.login():
            print("❌ 无法登录，请检查用户名密码")
            return
        
        # 显示初始状态
        self.show_status()
        
        # 启动轮询线程
        polling_thread = threading.Thread(target=self.start_polling)
        polling_thread.daemon = True
        polling_thread.start()
        
        print("\n🎯 机器人模拟器已启动!")
        print("📝 在服务器端发送控制指令，观察机器人响应")
        print("💡 按 Ctrl+C 停止模拟器")
        print("=" * 50)
        
        try:
            # 保持主线程运行
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 机器人模拟器已停止")
            self.running = False

def main():
    """主函数"""
    print("🤖 机器人模拟器 - Windows版本")
    print("用于测试与服务器的通信")
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
    
    # 创建并启动机器人模拟器
    robot = RobotSimulator(server_ip, robot_id)
    robot.start()

if __name__ == "__main__":
    main() 