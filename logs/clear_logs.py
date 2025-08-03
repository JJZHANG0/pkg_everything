#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime

def clear_robot_logs():
    """清理机器人日志"""
    try:
        if os.path.exists("robot_client.log"):
            # 备份旧日志
            backup_name = f"robot_client_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            shutil.copy2("robot_client.log", backup_name)
            print(f"✅ 机器人日志已备份为: {backup_name}")
            
            # 清空日志文件
            with open("robot_client.log", "w", encoding="utf-8") as f:
                f.write(f"# 机器人日志清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# 日志已清理\n\n")
            
            print("✅ 机器人日志已清理")
        else:
            print("❌ 机器人日志文件不存在")
    except Exception as e:
        print(f"❌ 清理机器人日志失败: {e}")

def clear_system_logs():
    """清理系统日志"""
    try:
        if os.path.exists("system_backend.log"):
            # 备份旧日志
            backup_name = f"system_backend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            shutil.copy2("system_backend.log", backup_name)
            print(f"✅ 系统日志已备份为: {backup_name}")
            
            # 清空日志文件
            with open("system_backend.log", "w", encoding="utf-8") as f:
                f.write(f"# 系统日志清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# 日志已清理\n\n")
            
            print("✅ 系统日志已清理")
        else:
            print("❌ 系统日志文件不存在")
    except Exception as e:
        print(f"❌ 清理系统日志失败: {e}")

def clear_all_logs():
    """清理所有日志"""
    print("🧹 开始清理所有日志文件...")
    print("=" * 50)
    
    clear_robot_logs()
    clear_system_logs()
    
    print("\n" + "=" * 50)
    print("📋 日志清理完成！")
    print("💾 旧日志已备份到当前目录")

def list_backups():
    """列出备份文件"""
    print("📦 备份文件列表")
    print("=" * 50)
    
    backup_files = []
    for file in os.listdir("."):
        if file.endswith("_backup_") and file.endswith(".log"):
            backup_files.append(file)
    
    if backup_files:
        for i, file in enumerate(sorted(backup_files), 1):
            file_size = os.path.getsize(file)
            print(f"{i:2d}. {file} ({file_size} bytes)")
    else:
        print("📭 没有找到备份文件")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "robot":
            clear_robot_logs()
        elif command == "system":
            clear_system_logs()
        elif command == "all":
            clear_all_logs()
        elif command == "backups":
            list_backups()
        else:
            print("❌ 未知命令")
            print_usage()
    else:
        print("🧹 机器人配送系统 - 日志清理工具")
        print("=" * 60)
        print("请选择要清理的日志类型:")
        print("1. 清理机器人日志")
        print("2. 清理系统日志")
        print("3. 清理所有日志")
        print("4. 查看备份文件")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            clear_robot_logs()
        elif choice == "2":
            clear_system_logs()
        elif choice == "3":
            clear_all_logs()
        elif choice == "4":
            list_backups()
        elif choice == "5":
            print("👋 退出")
        else:
            print("❌ 无效选择")

def print_usage():
    """打印使用说明"""
    print("📋 使用说明:")
    print("   • python clear_logs.py robot - 清理机器人日志")
    print("   • python clear_logs.py system - 清理系统日志")
    print("   • python clear_logs.py all - 清理所有日志")
    print("   • python clear_logs.py backups - 查看备份文件")

if __name__ == "__main__":
    main() 