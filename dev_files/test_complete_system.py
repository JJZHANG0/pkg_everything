#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime

class CompleteSystemTester:
    """完整系统测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.robot_id = 1
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {details}")
    
    def authenticate(self):
        """认证"""
        try:
            auth_data = {
                'username': 'root',
                'password': 'test123456'
            }
            
            response = requests.post(
                f"{self.base_url}/api/token/",
                json=auth_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data['access']
                self.log_test("认证", "PASS", "JWT token获取成功")
                return True
            else:
                self.log_test("认证", "FAIL", f"认证失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("认证", "FAIL", f"认证异常: {e}")
            return False
    
    def test_robot_status_api(self):
        """测试机器人状态API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.base_url}/api/robots/{self.robot_id}/status/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("机器人状态API", "PASS", f"状态: {data.get('status')}, 位置: {data.get('current_location')}")
                return data
            else:
                self.log_test("机器人状态API", "FAIL", f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("机器人状态API", "FAIL", f"异常: {e}")
            return None
    
    def test_robot_control_api(self):
        """测试机器人控制API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # 测试开门
            response = requests.post(
                f"{self.base_url}/api/robots/{self.robot_id}/control/",
                json={'action': 'open_door'},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("机器人控制API-开门", "PASS", data.get('message'))
            else:
                self.log_test("机器人控制API-开门", "FAIL", f"HTTP {response.status_code}")
            
            time.sleep(1)
            
            # 测试关门
            response = requests.post(
                f"{self.base_url}/api/robots/{self.robot_id}/control/",
                json={'action': 'close_door'},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("机器人控制API-关门", "PASS", data.get('message'))
            else:
                self.log_test("机器人控制API-关门", "FAIL", f"HTTP {response.status_code}")
            
            return True
                
        except Exception as e:
            self.log_test("机器人控制API", "FAIL", f"异常: {e}")
            return False
    
    def test_robot_status_update_api(self):
        """测试机器人状态更新API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            update_data = {
                'location': 'Test Location',
                'battery': 85,
                'door_status': 'CLOSED',
                'status': 'LOADING'
            }
            
            response = requests.post(
                f"{self.base_url}/api/robots/{self.robot_id}/update_status/",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("机器人状态更新API", "PASS", data.get('message'))
                return True
            else:
                self.log_test("机器人状态更新API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("机器人状态更新API", "FAIL", f"异常: {e}")
            return False
    
    def test_qr_scan_api(self):
        """测试二维码扫描API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # 模拟二维码数据
            qr_data = {
                'order_id': 1,
                'student_id': 2,
                'student_name': 'Test Student',
                'delivery_building': 'Test Building',
                'delivery_room': '101'
            }
            
            scan_data = {
                'order_id': 1,
                'qr_data': json.dumps(qr_data)
            }
            
            response = requests.post(
                f"{self.base_url}/api/robots/{self.robot_id}/qr_scanned/",
                json=scan_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("二维码扫描API", "PASS", data.get('message'))
                return True
            else:
                self.log_test("二维码扫描API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("二维码扫描API", "FAIL", f"异常: {e}")
            return False
    
    def test_qr_wait_api(self):
        """测试二维码等待API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = requests.post(
                f"{self.base_url}/api/robots/{self.robot_id}/start_qr_wait/",
                json={'order_id': 1},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("二维码等待API", "PASS", data.get('message'))
                return True
            else:
                self.log_test("二维码等待API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("二维码等待API", "FAIL", f"异常: {e}")
            return False
    
    def test_auto_return_api(self):
        """测试自动返航API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = requests.post(
                f"{self.base_url}/api/robots/{self.robot_id}/auto_return/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("自动返航API", "PASS", data.get('message'))
                return True
            else:
                self.log_test("自动返航API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("自动返航API", "FAIL", f"异常: {e}")
            return False
    
    def test_system_logs_api(self):
        """测试系统日志API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # 获取日志列表
            response = requests.get(f"{self.base_url}/api/logs/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                log_count = len(data.get('results', []))
                self.log_test("系统日志API", "PASS", f"获取到 {log_count} 条日志")
                return True
            else:
                self.log_test("系统日志API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("系统日志API", "FAIL", f"异常: {e}")
            return False
    
    def test_logs_summary_api(self):
        """测试日志统计API"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = requests.get(f"{self.base_url}/api/logs/summary/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("日志统计API", "PASS", f"总日志数: {data.get('total_logs')}")
                return True
            else:
                self.log_test("日志统计API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("日志统计API", "FAIL", f"异常: {e}")
            return False
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        print("\n🧪 开始完整工作流程测试...")
        print("=" * 60)
        
        # 1. 认证
        if not self.authenticate():
            return
        
        time.sleep(1)
        
        # 2. 获取机器人状态
        robot_status = self.test_robot_status_api()
        time.sleep(1)
        
        # 3. 测试机器人控制
        self.test_robot_control_api()
        time.sleep(1)
        
        # 4. 测试状态更新
        self.test_robot_status_update_api()
        time.sleep(1)
        
        # 5. 测试二维码等待
        self.test_qr_wait_api()
        time.sleep(1)
        
        # 6. 测试二维码扫描
        self.test_qr_scan_api()
        time.sleep(1)
        
        # 7. 测试自动返航
        self.test_auto_return_api()
        time.sleep(1)
        
        # 8. 测试系统日志
        self.test_system_logs_api()
        time.sleep(1)
        
        # 9. 测试日志统计
        self.test_logs_summary_api()
        
        # 输出测试结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 所有测试通过！系统功能完整")
        else:
            print(f"\n⚠️ 有{failed}个测试失败，请检查系统")
        
        return self.test_results


def main():
    """主函数"""
    print("🤖 机器人配送系统完整功能测试")
    print("=" * 60)
    
    tester = CompleteSystemTester()
    results = tester.test_complete_workflow()
    
    # 保存测试结果
    with open("complete_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试结果已保存到 complete_test_results.json")


if __name__ == "__main__":
    main() 