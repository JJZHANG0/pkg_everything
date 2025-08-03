#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import random
from datetime import datetime

class BackendSimulator:
    """模拟后端系统，用于测试快递车客户端的实时连接"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.robot_id = 1
        
        # 模拟订单数据
        self.sample_orders = [
            {
                "order_id": 1,
                "student": {"name": "张三", "email": "zhangsan@example.com"},
                "delivery_location": {"building": "宿舍楼A", "room": "101"},
                "package_type": "书籍",
                "status": "ASSIGNED"
            },
            {
                "order_id": 2,
                "student": {"name": "李四", "email": "lisi@example.com"},
                "delivery_location": {"building": "宿舍楼B", "room": "205"},
                "package_type": "电子产品",
                "status": "ASSIGNED"
            },
            {
                "order_id": 3,
                "student": {"name": "王五", "email": "wangwu@example.com"},
                "delivery_location": {"building": "图书馆", "room": "自习室"},
                "package_type": "文件",
                "status": "ASSIGNED"
            }
        ]
    
    def test_connection(self):
        """测试与后端的连接"""
        try:
            response = requests.get(f"{self.base_url}/robots/{self.robot_id}/current_orders/")
            if response.status_code == 200:
                print("✅ 成功连接到后端系统")
                return True
            else:
                print(f"❌ 连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return False
    
    def simulate_order_status_changes(self):
        """模拟订单状态变化"""
        print("🚀 开始模拟后端订单状态变化...")
        print("📋 这将模拟真实的快递系统操作")
        print("=" * 50)
        
        # 模拟1: 添加新订单
        print("\n📦 模拟1: 添加新订单到系统")
        self.simulate_add_order()
        time.sleep(3)
        
        # 模拟2: 更改订单状态为LOADING
        print("\n🔄 模拟2: 更改订单状态为LOADING")
        self.simulate_change_status("LOADING")
        time.sleep(3)
        
        # 模拟3: 更改订单状态为DELIVERING
        print("\n🚚 模拟3: 更改订单状态为DELIVERING")
        self.simulate_change_status("DELIVERING")
        time.sleep(3)
        
        # 模拟4: 完成订单
        print("\n✅ 模拟4: 完成订单")
        self.simulate_change_status("DELIVERED")
        time.sleep(3)
        
        print("\n🎯 模拟完成！检查快递车客户端界面是否显示了这些变化。")
    
    def simulate_add_order(self):
        """模拟添加新订单"""
        try:
            # 这里应该调用实际的API来创建订单
            # 由于我们没有实际的创建订单API，我们只是打印信息
            new_order = random.choice(self.sample_orders)
            print(f"   📝 创建新订单: {new_order['student']['name']} - {new_order['delivery_location']['building']}")
            print(f"   📦 包裹类型: {new_order['package_type']}")
            print(f"   🏠 配送地址: {new_order['delivery_location']['building']} {new_order['delivery_location']['room']}")
            
            # 在实际系统中，这里会调用:
            # POST /api/orders/
            # 然后快递车客户端会通过轮询检测到新订单
            
        except Exception as e:
            print(f"   ❌ 添加订单失败: {e}")
    
    def simulate_change_status(self, new_status):
        """模拟更改订单状态"""
        try:
            order_id = random.randint(1, 3)
            print(f"   🔄 更改订单 {order_id} 状态为: {new_status}")
            
            # 在实际系统中，这里会调用:
            # PATCH /api/orders/{order_id}/
            # 数据: {"status": new_status}
            
            if new_status == "DELIVERING":
                print(f"   📱 生成二维码数据: Order {order_id}")
                print(f"   🎯 快递车应该收到完整的订单信息")
            
            elif new_status == "DELIVERED":
                print(f"   ✅ 订单 {order_id} 配送完成")
                print(f"   🎉 用户已签收包裹")
            
        except Exception as e:
            print(f"   ❌ 更改状态失败: {e}")
    
    def interactive_simulation(self):
        """交互式模拟"""
        print("🎮 交互式后端模拟器")
        print("=" * 50)
        print("选择要模拟的操作:")
        print("1. 测试连接")
        print("2. 添加新订单")
        print("3. 更改订单状态")
        print("4. 运行完整模拟")
        print("5. 退出")
        
        while True:
            try:
                choice = input("\n请输入选择 (1-5): ").strip()
                
                if choice == "1":
                    self.test_connection()
                elif choice == "2":
                    self.simulate_add_order()
                elif choice == "3":
                    status = input("输入新状态 (ASSIGNED/LOADING/DELIVERING/DELIVERED): ").strip()
                    if status in ["ASSIGNED", "LOADING", "DELIVERING", "DELIVERED"]:
                        self.simulate_change_status(status)
                    else:
                        print("❌ 无效的状态")
                elif choice == "4":
                    self.simulate_order_status_changes()
                elif choice == "5":
                    print("👋 退出模拟器")
                    break
                else:
                    print("❌ 无效选择")
                    
            except KeyboardInterrupt:
                print("\n👋 退出模拟器")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    """主函数"""
    simulator = BackendSimulator()
    
    print("🤖 CulverBot 后端系统模拟器")
    print("=" * 50)
    print("这个工具用于模拟后端系统的订单状态变化")
    print("配合快递车客户端使用，可以测试实时数据更新")
    print("=" * 50)
    
    # 测试连接
    if simulator.test_connection():
        simulator.interactive_simulation()
    else:
        print("⚠️ 无法连接到后端系统，但可以运行模拟")
        simulator.interactive_simulation()

if __name__ == "__main__":
    main() 