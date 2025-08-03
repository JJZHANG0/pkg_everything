#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import requests
import json
from datetime import datetime
import time

def sync_robot_logs():
    """同步机器人客户端日志"""
    source_file = "../robot_client/logs/robot.log"
    target_file = "robot_client.log"
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, target_file)
        print(f"✅ 机器人日志同步完成: {target_file}")
    else:
        print(f"❌ 机器人日志文件不存在: {source_file}")

def sync_system_logs():
    """同步后端系统日志"""
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
                
                with open("system_backend.log", "w", encoding="utf-8") as f:
                    for log in logs_data:
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
                        
                        f.write(f"[{formatted_time}] {level:8s} [{log_type:12s}] {message}\n")
                
                print(f"✅ 系统日志同步完成: system_backend.log ({len(logs_data)} 条记录)")
            else:
                print(f"❌ 获取系统日志失败: HTTP {logs_response.status_code}")
                
        else:
            print(f"❌ 认证失败: HTTP {auth_response.status_code}")
            
    except Exception as e:
        print(f"❌ 同步系统日志异常: {e}")

def create_frontend_log_template():
    """创建前端日志模板文件"""
    template_content = """# 🌐 前端操作日志模板

这个文件用于记录前端用户操作日志。由于前端日志是临时性的，这里提供一个模板格式：

## 📝 日志格式示例

[时间] ✅/❌ 操作结果: 详细信息

## 📋 常见操作日志

[4:21:19 PM] ✅ 机器人控制成功: open_door - 机器人 Robot-001 开门成功
[4:21:19 PM] ✅ 机器人控制成功: close_door - 机器人 Robot-001 关门成功
[4:21:19 PM] ✅ 机器人控制成功: start_delivery - 机器人 Robot-001 开始配送
[4:21:19 PM] ✅ 机器人控制成功: stop_robot - 机器人 Robot-001 停止运行

[4:21:19 PM] ✅ 订单状态更新成功: 订单 #1 状态更新为 ASSIGNED
[4:21:19 PM] ❌ 订单状态更新失败: 订单 #1 状态更新失败 - 权限不足

## 🔍 如何查看前端日志

1. 访问前端页面: http://localhost:3000
2. 登录Dispatcher页面
3. 查看页面底部的"System Logs"部分
4. 执行操作后观察日志更新

## 📊 日志说明

- ✅ 表示操作成功
- ❌ 表示操作失败
- 时间格式: 本地时间 (12小时制)
- 操作类型: 机器人控制、订单管理、系统操作等

---
注意: 前端日志是临时性的，刷新页面后会消失。重要操作请查看系统日志。
"""
    
    with open("frontend_operations.log", "w", encoding="utf-8") as f:
        f.write(template_content)
    
    print("✅ 前端日志模板创建完成: frontend_operations.log")

def main():
    """主函数"""
    print("🔄 开始同步日志文件...")
    print("=" * 50)
    
    # 确保在logs目录中
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # 同步各种日志
    sync_robot_logs()
    sync_system_logs()
    create_frontend_log_template()
    
    print("\n" + "=" * 50)
    print("📋 日志同步完成！")
    print("📁 日志文件位置:")
    print("   • robot_client.log - 机器人客户端日志")
    print("   • system_backend.log - 后端系统日志")
    print("   • frontend_operations.log - 前端操作日志模板")
    print("\n🚀 查看命令:")
    print("   • tail -f robot_client.log")
    print("   • tail -f system_backend.log")
    print("   • cat frontend_operations.log")

if __name__ == "__main__":
    main() 