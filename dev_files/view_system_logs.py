#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

def view_system_logs():
    """查看系统日志"""
    print("📋 系统日志查看器")
    print("=" * 60)
    
    try:
        # 获取token
        auth_response = requests.post(
            "http://localhost:8000/api/token/",
            json={"username": "root", "password": "test123456"},
            timeout=5
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 获取系统日志
            logs_response = requests.get(
                "http://localhost:8000/api/logs/",
                headers=headers,
                timeout=5
            )
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                print(f"📊 总日志数: {len(logs_data)}")
                print("\n📝 最近20条系统日志:")
                print("-" * 60)
                
                for i, log in enumerate(logs_data[:20], 1):
                    timestamp = log.get('timestamp', '')
                    level = log.get('level', '')
                    message = log.get('message', '')
                    log_type = log.get('log_type', '')
                    
                    # 格式化时间
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_time = timestamp
                    else:
                        formatted_time = 'N/A'
                    
                    print(f"{i:2d}. [{formatted_time}] {level:8s} [{log_type:12s}] {message}")
                
                # 获取日志统计
                summary_response = requests.get(
                    "http://localhost:8000/api/logs/summary/",
                    headers=headers,
                    timeout=5
                )
                
                if summary_response.status_code == 200:
                    summary = summary_response.json()
                    print("\n📈 日志统计:")
                    print("-" * 30)
                    print(f"总日志数: {summary.get('total_logs', 0)}")
                    print(f"信息日志: {summary.get('info_count', 0)}")
                    print(f"成功日志: {summary.get('success_count', 0)}")
                    print(f"警告日志: {summary.get('warning_count', 0)}")
                    print(f"错误日志: {summary.get('error_count', 0)}")
                    
            else:
                print(f"❌ 获取系统日志失败: HTTP {logs_response.status_code}")
                print(f"错误信息: {logs_response.text}")
                
        else:
            print(f"❌ 认证失败: HTTP {auth_response.status_code}")
            
    except Exception as e:
        print(f"❌ 查看系统日志异常: {e}")

def view_robot_logs():
    """查看机器人客户端日志"""
    print("\n🤖 机器人客户端日志")
    print("=" * 60)
    
    try:
        with open('robot_client/logs/robot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"📊 总日志行数: {len(lines)}")
        print("\n📝 最近20条机器人日志:")
        print("-" * 60)
        
        for i, line in enumerate(lines[-20:], 1):
            line = line.strip()
            if line:
                print(f"{i:2d}. {line}")
                
    except FileNotFoundError:
        print("❌ 机器人日志文件不存在")
    except Exception as e:
        print(f"❌ 读取机器人日志异常: {e}")

def main():
    """主函数"""
    view_system_logs()
    view_robot_logs()
    
    print("\n" + "=" * 60)
    print("📋 日志说明:")
    print("• 系统日志: 存储在Django数据库中，永久保存")
    print("• 机器人日志: 存储在 robot_client/logs/robot.log 文件中")
    print("• 前端日志: 显示在页面中，刷新后消失")

if __name__ == "__main__":
    main() 