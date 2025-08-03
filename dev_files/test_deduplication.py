#!/usr/bin/env python3
"""
测试网络监控去重功能
"""

import requests
import time
import json

def test_deduplication():
    """测试去重功能"""
    
    # 获取认证token
    token_response = requests.post('http://localhost:8000/api/token/', {
        'username': 'root',
        'password': 'test123456'
    })
    
    if token_response.status_code != 200:
        print("❌ 认证失败")
        return
    
    token = token_response.json()['access']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔍 测试网络监控去重功能...")
    
    # 1. 获取初始数据
    print("\n1️⃣ 获取初始网络监控数据...")
    initial_response = requests.get('http://localhost:8000/api/network-monitor/?limit=10', headers=headers)
    if initial_response.status_code == 200:
        initial_data = initial_response.json()
        initial_count = len(initial_data['logs'])
        print(f"   初始日志数量: {initial_count}")
    else:
        print(f"   ❌ 获取初始数据失败: {initial_response.status_code}")
        return
    
    # 2. 模拟多次相同请求
    print("\n2️⃣ 模拟多次相同请求...")
    for i in range(5):
        print(f"   发送第 {i+1} 次请求...")
        requests.get('http://localhost:8000/api/robots/1/status/', headers=headers)
        time.sleep(1)
    
    # 3. 获取更新后的数据
    print("\n3️⃣ 获取更新后的数据...")
    time.sleep(2)  # 等待数据更新
    updated_response = requests.get('http://localhost:8000/api/network-monitor/?limit=10', headers=headers)
    if updated_response.status_code == 200:
        updated_data = updated_response.json()
        updated_count = len(updated_data['logs'])
        print(f"   更新后日志数量: {updated_count}")
        
        # 4. 检查去重效果
        print("\n4️⃣ 检查去重效果...")
        if updated_count <= initial_count + 1:  # 应该只增加1个新记录（去重后）
            print("   ✅ 去重功能正常工作！")
            print(f"   日志数量增长: {updated_count - initial_count}")
        else:
            print("   ❌ 去重功能可能有问题")
            print(f"   日志数量增长过多: {updated_count - initial_count}")
        
        # 5. 显示最新的几条日志
        print("\n5️⃣ 最新日志示例:")
        for i, log in enumerate(updated_data['logs'][:3]):
            print(f"   {i+1}. {log['data']['client_ip']} - {log['data']['method']} {log['data']['path']}")
    
    # 6. 测试活跃连接去重
    print("\n6️⃣ 测试活跃连接去重...")
    connections_response = requests.get('http://localhost:8000/api/network-monitor/connections/', headers=headers)
    if connections_response.status_code == 200:
        connections_data = connections_response.json()
        unique_ips = len(connections_data['active_connections'])
        print(f"   活跃连接数量: {connections_data['total_connections']}")
        print(f"   唯一IP数量: {unique_ips}")
        
        if unique_ips <= 2:  # 应该只有很少的唯一IP
            print("   ✅ 活跃连接去重功能正常工作！")
        else:
            print("   ❌ 活跃连接去重可能有问题")
    else:
        print(f"   ❌ 获取活跃连接失败: {connections_response.status_code}")

if __name__ == "__main__":
    test_deduplication() 