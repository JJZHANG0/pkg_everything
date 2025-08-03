#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from datetime import datetime

def view_robot_logs(lines=20):
    """查看机器人日志"""
    print("🤖 机器人客户端日志")
    print("=" * 60)
    
    try:
        with open("robot_client.log", "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            
        print(f"📊 总日志行数: {len(all_lines)}")
        print(f"📝 最近 {lines} 条机器人日志:")
        print("-" * 60)
        
        for i, line in enumerate(all_lines[-lines:], 1):
            line = line.strip()
            if line:
                print(f"{i:2d}. {line}")
                
    except FileNotFoundError:
        print("❌ 机器人日志文件不存在，请先运行 sync_logs.py")
    except Exception as e:
        print(f"❌ 读取机器人日志异常: {e}")

def view_system_logs(lines=20):
    """查看系统日志"""
    print("\n🖥️ 后端系统日志")
    print("=" * 60)
    
    try:
        with open("system_backend.log", "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            
        print(f"📊 总日志行数: {len(all_lines)}")
        print(f"📝 最近 {lines} 条系统日志:")
        print("-" * 60)
        
        for i, line in enumerate(all_lines[-lines:], 1):
            line = line.strip()
            if line:
                print(f"{i:2d}. {line}")
                
    except FileNotFoundError:
        print("❌ 系统日志文件不存在，请先运行 sync_logs.py")
    except Exception as e:
        print(f"❌ 读取系统日志异常: {e}")

def view_frontend_logs():
    """查看前端日志说明"""
    print("\n🌐 前端操作日志")
    print("=" * 60)
    
    try:
        with open("frontend_operations.log", "r", encoding="utf-8") as f:
            content = f.read()
            
        print("📋 前端日志说明和模板:")
        print("-" * 60)
        print(content)
                
    except FileNotFoundError:
        print("❌ 前端日志文件不存在，请先运行 sync_logs.py")
    except Exception as e:
        print(f"❌ 读取前端日志异常: {e}")

def view_log_summary():
    """查看日志摘要"""
    print("\n📊 日志摘要")
    print("=" * 60)
    
    summary = {}
    
    # 统计机器人日志
    try:
        with open("robot_client.log", "r", encoding="utf-8") as f:
            robot_lines = len(f.readlines())
        summary['robot'] = robot_lines
    except:
        summary['robot'] = 0
    
    # 统计系统日志
    try:
        with open("system_backend.log", "r", encoding="utf-8") as f:
            system_lines = len(f.readlines())
        summary['system'] = system_lines
    except:
        summary['system'] = 0
    
    print(f"🤖 机器人日志: {summary['robot']} 行")
    print(f"🖥️ 系统日志: {summary['system']} 行")
    print(f"🌐 前端日志: 模板文件")
    
    total = summary['robot'] + summary['system']
    print(f"📈 总日志行数: {total} 行")

def real_time_monitor():
    """实时监控日志"""
    print("\n🔍 实时日志监控")
    print("=" * 60)
    print("按 Ctrl+C 停止监控")
    print("-" * 60)
    
    try:
        while True:
            # 检查机器人日志更新
            try:
                with open("robot_client.log", "r", encoding="utf-8") as f:
                    robot_lines = f.readlines()
                if robot_lines:
                    latest_robot = robot_lines[-1].strip()
                    if latest_robot:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 {latest_robot}")
            except:
                pass
            
            # 检查系统日志更新
            try:
                with open("system_backend.log", "r", encoding="utf-8") as f:
                    system_lines = f.readlines()
                if system_lines:
                    latest_system = system_lines[-1].strip()
                    if latest_system:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🖥️ {latest_system}")
            except:
                pass
            
            time.sleep(2)  # 每2秒检查一次
            
    except KeyboardInterrupt:
        print("\n⏹️ 监控已停止")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "robot":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            view_robot_logs(lines)
        elif command == "system":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            view_system_logs(lines)
        elif command == "frontend":
            view_frontend_logs()
        elif command == "summary":
            view_log_summary()
        elif command == "monitor":
            real_time_monitor()
        elif command == "sync":
            os.system("python sync_logs.py")
        else:
            print("❌ 未知命令")
            print_usage()
    else:
        # 默认显示所有日志
        print("📋 机器人配送系统 - 统一日志查看器")
        print("=" * 80)
        
        view_robot_logs(10)
        view_system_logs(10)
        view_log_summary()
        
        print("\n" + "=" * 80)
        print("🚀 使用说明:")
        print("   • python view_all_logs.py robot [行数] - 查看机器人日志")
        print("   • python view_all_logs.py system [行数] - 查看系统日志")
        print("   • python view_all_logs.py frontend - 查看前端日志说明")
        print("   • python view_all_logs.py summary - 查看日志摘要")
        print("   • python view_all_logs.py monitor - 实时监控日志")
        print("   • python view_all_logs.py sync - 同步日志文件")

def print_usage():
    """打印使用说明"""
    print("📋 使用说明:")
    print("   • python view_all_logs.py robot [行数] - 查看机器人日志")
    print("   • python view_all_logs.py system [行数] - 查看系统日志")
    print("   • python view_all_logs.py frontend - 查看前端日志说明")
    print("   • python view_all_logs.py summary - 查看日志摘要")
    print("   • python view_all_logs.py monitor - 实时监控日志")
    print("   • python view_all_logs.py sync - 同步日志文件")

if __name__ == "__main__":
    main() 