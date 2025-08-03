#!/usr/bin/env python3
import requests
import json

def test_deduplication():
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
    
    # 获取网络监控数据
    response = requests.get('http://localhost:8000/api/network-monitor/?limit=20', headers=headers)
    if response.status_code == 200:
        data = response.json()
        logs = data['logs']
        
        print(f"总日志数量: {len(logs)}")
        
        # 统计唯一IP和路径
        ips = set()
        paths = set()
        unique_combinations = set()
        
        for log in logs:
            client_ip = log['data']['client_ip']
            path = log['data']['path']
            method = log['data']['method']
            
            ips.add(client_ip)
            paths.add(path)
            unique_combinations.add(f"{client_ip}-{path}-{method}")
        
        print(f"唯一IP数量: {len(ips)}")
        print(f"唯一路径数量: {len(paths)}")
        print(f"唯一组合数量: {len(unique_combinations)}")
        
        if len(unique_combinations) < len(logs):
            print("✅ 去重功能正常工作！")
            print(f"去重前: {len(logs)} 条记录")
            print(f"去重后: {len(unique_combinations)} 条记录")
        else:
            print("❌ 去重功能可能有问题")
        
        # 显示IP列表
        print(f"IP列表: {list(ips)}")
        
    else:
        print(f"❌ 获取数据失败: {response.status_code}")

if __name__ == "__main__":
    test_deduplication() 