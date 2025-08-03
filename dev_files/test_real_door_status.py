#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 测试真实门状态接收功能
验证ROS端返回的真实门状态是否能正确接收和处理
"""

import requests
import json
import time

class DoorStatusTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.robot_id = 1
        self.token = None
        
    def login(self):
        """登录获取token"""
        try:
            response = requests.post(
                f"{self.base_url}/token/",
                json={"username": "root", "password": "test123456"},
                timeout=5
            )
            if response.status_code == 200:
                self.token = response.json()["access"]
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def get_robot_status(self):
        """获取机器人状态"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/robots/{self.robot_id}/status/",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 获取状态失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取状态异常: {e}")
            return None
    
    def send_door_command(self, command_type):
        """发送门控制指令"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/robots/{self.robot_id}/control/",
                headers=headers,
                json={"action": command_type},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 发送指令失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 发送指令异常: {e}")
            return None
    
    def report_command_result(self, command_id, result):
        """报告指令执行结果"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/robots/{self.robot_id}/execute_command/",
                headers=headers,
                json={"command_id": command_id, "result": result},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 报告结果失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 报告结果异常: {e}")
            return None
    
    def test_door_status_flow(self):
        """测试门状态流程"""
        print("🚪 开始测试真实门状态接收功能")
        print("=" * 50)
        
        # 1. 获取初始状态
        print("\n1. 获取初始机器人状态...")
        initial_status = self.get_robot_status()
        if initial_status:
            print(f"   初始门状态: {initial_status.get('door_status', 'Unknown')}")
        else:
            print("   ❌ 无法获取初始状态")
            return
        
        # 2. 发送开门指令
        print("\n2. 发送开门指令...")
        open_command = self.send_door_command("open_door")
        if open_command:
            command_id = open_command.get("command_id")
            print(f"   指令ID: {command_id}")
        else:
            print("   ❌ 发送开门指令失败")
            return
        
        # 3. 模拟ROS返回真实门状态 - 门实际打开了
        print("\n3. 模拟ROS返回真实门状态 (door_open)...")
        result = self.report_command_result(command_id, "door_open")
        if result:
            print(f"   执行结果: {result.get('message', 'Unknown')}")
        else:
            print("   ❌ 报告开门结果失败")
            return
        
        # 4. 检查门状态
        print("\n4. 检查门状态更新...")
        time.sleep(1)  # 等待状态更新
        status_after_open = self.get_robot_status()
        if status_after_open:
            door_status = status_after_open.get('door_status', 'Unknown')
            print(f"   当前门状态: {door_status}")
            if door_status == 'OPEN':
                print("   ✅ 门状态正确更新为OPEN")
            else:
                print(f"   ❌ 门状态错误: 期望OPEN，实际{door_status}")
        else:
            print("   ❌ 无法获取开门后状态")
        
        # 5. 发送关门指令
        print("\n5. 发送关门指令...")
        close_command = self.send_door_command("close_door")
        if close_command:
            command_id = close_command.get("command_id")
            print(f"   指令ID: {command_id}")
        else:
            print("   ❌ 发送关门指令失败")
            return
        
        # 6. 模拟ROS返回真实门状态 - 门实际关闭了
        print("\n6. 模拟ROS返回真实门状态 (door_closed)...")
        result = self.report_command_result(command_id, "door_closed")
        if result:
            print(f"   执行结果: {result.get('message', 'Unknown')}")
        else:
            print("   ❌ 报告关门结果失败")
            return
        
        # 7. 检查门状态
        print("\n7. 检查门状态更新...")
        time.sleep(1)  # 等待状态更新
        status_after_close = self.get_robot_status()
        if status_after_close:
            door_status = status_after_close.get('door_status', 'Unknown')
            print(f"   当前门状态: {door_status}")
            if door_status == 'CLOSED':
                print("   ✅ 门状态正确更新为CLOSED")
            else:
                print(f"   ❌ 门状态错误: 期望CLOSED，实际{door_status}")
        else:
            print("   ❌ 无法获取关门后状态")
        
        # 8. 测试异常情况 - 门卡住了
        print("\n8. 测试异常情况 - 门卡住了...")
        stuck_command = self.send_door_command("open_door")
        if stuck_command:
            command_id = stuck_command.get("command_id")
            print(f"   指令ID: {command_id}")
            
            # 模拟门卡住的情况
            result = self.report_command_result(command_id, "door_stuck")
            if result:
                print(f"   执行结果: {result.get('message', 'Unknown')}")
            
            # 检查状态
            time.sleep(1)
            stuck_status = self.get_robot_status()
            if stuck_status:
                door_status = stuck_status.get('door_status', 'Unknown')
                print(f"   当前门状态: {door_status}")
                print("   ⚠️ 门卡住时状态处理")
        
        print("\n" + "=" * 50)
        print("🏁 真实门状态测试完成")

def main():
    tester = DoorStatusTester()
    
    if tester.login():
        tester.test_door_status_flow()
    else:
        print("❌ 无法登录，测试终止")

if __name__ == "__main__":
    main() 