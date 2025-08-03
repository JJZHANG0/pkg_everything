#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 WebSocket日志查看工具
提供专业的WebSocket日志查看和分析功能
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse

class WebSocketLogViewer:
    """WebSocket日志查看器"""
    
    def __init__(self, log_dir: str = "/app/logs"):
        self.log_dir = log_dir
        self.log_files = {
            'detailed': os.path.join(log_dir, 'websocket_detailed.log'),
            'events': os.path.join(log_dir, 'websocket_events.log'),
            'system': os.path.join(log_dir, 'system_backend.log')
        }
    
    def read_log_file(self, file_path: str, lines: int = 100) -> List[str]:
        """读取日志文件"""
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()[-lines:]
        except Exception as e:
            print(f"读取日志文件失败: {e}")
            return []
    
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """解析日志行"""
        try:
            # 解析时间戳
            if line.startswith('['):
                end_bracket = line.find(']', 1)
                if end_bracket != -1:
                    timestamp_str = line[1:end_bracket]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    message = line[end_bracket + 1:].strip()
                    
                    # 解析日志级别
                    level = 'INFO'
                    if 'ERROR' in message:
                        level = 'ERROR'
                    elif 'WARNING' in message:
                        level = 'WARNING'
                    elif 'DEBUG' in message:
                        level = 'DEBUG'
                    
                    return {
                        'timestamp': timestamp,
                        'level': level,
                        'message': message,
                        'raw': line.strip()
                    }
        except Exception as e:
            pass
        
        return {
            'timestamp': datetime.now(),
            'level': 'UNKNOWN',
            'message': line.strip(),
            'raw': line.strip()
        }
    
    def filter_logs(self, logs: List[Dict], 
                   level: str = None, 
                   robot_id: str = None, 
                   event_type: str = None,
                   time_range: timedelta = None) -> List[Dict]:
        """过滤日志"""
        filtered = []
        now = datetime.now()
        
        for log in logs:
            # 时间过滤
            if time_range and (now - log['timestamp']) > time_range:
                continue
            
            # 级别过滤
            if level and log['level'] != level:
                continue
            
            # 机器人ID过滤
            if robot_id and f"Robot-{robot_id}:" not in log['message']:
                continue
            
            # 事件类型过滤
            if event_type and event_type not in log['message']:
                continue
            
            filtered.append(log)
        
        return filtered
    
    def show_recent_logs(self, log_type: str = 'events', lines: int = 50, 
                        level: str = None, robot_id: str = None):
        """显示最近的日志"""
        print(f"\n📋 显示最近的 {log_type} 日志 (最后 {lines} 行)")
        print("=" * 80)
        
        if log_type not in self.log_files:
            print(f"❌ 未知的日志类型: {log_type}")
            return
        
        log_lines = self.read_log_file(self.log_files[log_type], lines)
        logs = [self.parse_log_line(line) for line in log_lines]
        
        # 过滤日志
        if level or robot_id:
            logs = self.filter_logs(logs, level=level, robot_id=robot_id)
        
        # 显示日志
        for log in logs:
            timestamp = log['timestamp'].strftime('%H:%M:%S')
            level_emoji = {
                'ERROR': '❌',
                'WARNING': '⚠️',
                'INFO': 'ℹ️',
                'DEBUG': '🔍'
            }.get(log['level'], '❓')
            
            print(f"{level_emoji} [{timestamp}] {log['level']} - {log['message']}")
    
    def show_connection_stats(self):
        """显示连接统计"""
        print("\n📊 WebSocket连接统计")
        print("=" * 50)
        
        # 读取事件日志
        log_lines = self.read_log_file(self.log_files['events'], 1000)
        logs = [self.parse_log_line(line) for line in log_lines]
        
        # 统计连接事件
        stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'total_messages': 0,
            'robots': {}
        }
        
        for log in logs:
            message = log['message']
            
            if 'CONNECTION_ESTABLISHED' in message:
                stats['total_connections'] += 1
                stats['active_connections'] += 1
                
                # 提取机器人信息
                if 'Robot-' in message:
                    robot_info = message.split('Robot-')[1].split(']')[0]
                    robot_id = robot_info.split(':')[0]
                    if robot_id not in stats['robots']:
                        stats['robots'][robot_id] = {'connections': 0, 'messages': 0}
                    stats['robots'][robot_id]['connections'] += 1
            
            elif 'CONNECTION_CLOSED' in message:
                stats['active_connections'] = max(0, stats['active_connections'] - 1)
            
            elif 'CONNECTION_FAILED' in message:
                stats['failed_connections'] += 1
            
            elif 'MESSAGE_RECEIVED' in message or 'MESSAGE_SENT' in message:
                stats['total_messages'] += 1
                
                # 统计机器人消息
                if 'Robot-' in message:
                    robot_info = message.split('Robot-')[1].split(']')[0]
                    robot_id = robot_info.split(':')[0]
                    if robot_id not in stats['robots']:
                        stats['robots'][robot_id] = {'connections': 0, 'messages': 0}
                    stats['robots'][robot_id]['messages'] += 1
        
        # 显示统计信息
        print(f"🔗 总连接数: {stats['total_connections']}")
        print(f"🟢 活跃连接: {stats['active_connections']}")
        print(f"🔴 失败连接: {stats['failed_connections']}")
        print(f"💬 总消息数: {stats['total_messages']}")
        
        if stats['robots']:
            print(f"\n🤖 机器人统计:")
            for robot_id, robot_stats in stats['robots'].items():
                print(f"  Robot-{robot_id}: {robot_stats['connections']} 连接, {robot_stats['messages']} 消息")
    
    def show_performance_metrics(self):
        """显示性能指标"""
        print("\n⚡ WebSocket性能指标")
        print("=" * 50)
        
        # 读取详细日志
        log_lines = self.read_log_file(self.log_files['detailed'], 1000)
        logs = [self.parse_log_line(line) for line in log_lines]
        
        # 统计性能指标
        performance_data = {
            'command_send_times': [],
            'execution_times': [],
            'message_counts': {}
        }
        
        for log in logs:
            message = log['message']
            
            if 'PERFORMANCE' in message:
                if 'command_send_time' in message:
                    # 提取发送时间
                    try:
                        time_str = message.split('command_send_time: ')[1].split('s')[0]
                        performance_data['command_send_times'].append(float(time_str))
                    except:
                        pass
                
                elif 'execution_time' in message:
                    # 提取执行时间
                    try:
                        time_str = message.split('execution_time: ')[1].split('s')[0]
                        performance_data['execution_times'].append(float(time_str))
                    except:
                        pass
            
            elif 'MESSAGE_RECEIVED' in message or 'MESSAGE_SENT' in message:
                # 统计消息类型
                if 'Type:' in message:
                    msg_type = message.split('Type: ')[1].split(' ')[0]
                    if msg_type not in performance_data['message_counts']:
                        performance_data['message_counts'][msg_type] = 0
                    performance_data['message_counts'][msg_type] += 1
        
        # 显示性能指标
        if performance_data['command_send_times']:
            avg_send_time = sum(performance_data['command_send_times']) / len(performance_data['command_send_times'])
            print(f"📤 平均指令发送时间: {avg_send_time:.3f}s")
        
        if performance_data['execution_times']:
            avg_exec_time = sum(performance_data['execution_times']) / len(performance_data['execution_times'])
            print(f"⚡ 平均指令执行时间: {avg_exec_time:.3f}s")
        
        if performance_data['message_counts']:
            print(f"\n💬 消息类型统计:")
            for msg_type, count in performance_data['message_counts'].items():
                print(f"  {msg_type}: {count} 条")
    
    def show_errors(self, hours: int = 24):
        """显示错误日志"""
        print(f"\n🚨 最近 {hours} 小时的错误日志")
        print("=" * 80)
        
        # 读取所有日志文件
        all_logs = []
        for log_type, file_path in self.log_files.items():
            log_lines = self.read_log_file(file_path, 1000)
            logs = [self.parse_log_line(line) for line in log_lines]
            all_logs.extend(logs)
        
        # 过滤错误日志
        time_range = timedelta(hours=hours)
        error_logs = self.filter_logs(all_logs, level='ERROR', time_range=time_range)
        
        if not error_logs:
            print("✅ 没有发现错误日志")
            return
        
        # 按时间排序
        error_logs.sort(key=lambda x: x['timestamp'])
        
        # 显示错误日志
        for log in error_logs:
            timestamp = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"❌ [{timestamp}] {log['message']}")
    
    def show_live_logs(self, log_type: str = 'events', robot_id: str = None):
        """实时显示日志"""
        print(f"\n🔴 实时监控 {log_type} 日志 (按 Ctrl+C 停止)")
        print("=" * 80)
        
        if log_type not in self.log_files:
            print(f"❌ 未知的日志类型: {log_type}")
            return
        
        file_path = self.log_files[log_type]
        if not os.path.exists(file_path):
            print(f"❌ 日志文件不存在: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 移动到文件末尾
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        log = self.parse_log_line(line)
                        
                        # 过滤机器人ID
                        if robot_id and f"Robot-{robot_id}:" not in log['message']:
                            continue
                        
                        timestamp = log['timestamp'].strftime('%H:%M:%S')
                        level_emoji = {
                            'ERROR': '❌',
                            'WARNING': '⚠️',
                            'INFO': 'ℹ️',
                            'DEBUG': '🔍'
                        }.get(log['level'], '❓')
                        
                        print(f"{level_emoji} [{timestamp}] {log['message']}")
                    else:
                        time.sleep(0.1)
                        
        except KeyboardInterrupt:
            print("\n⏹️ 停止实时监控")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WebSocket日志查看工具')
    parser.add_argument('--log-dir', default='/app/logs', help='日志目录路径')
    parser.add_argument('--type', choices=['detailed', 'events', 'system'], default='events', help='日志类型')
    parser.add_argument('--lines', type=int, default=50, help='显示行数')
    parser.add_argument('--level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='日志级别过滤')
    parser.add_argument('--robot-id', help='机器人ID过滤')
    parser.add_argument('--stats', action='store_true', help='显示连接统计')
    parser.add_argument('--performance', action='store_true', help='显示性能指标')
    parser.add_argument('--errors', type=int, default=24, help='显示最近N小时的错误')
    parser.add_argument('--live', action='store_true', help='实时监控日志')
    
    args = parser.parse_args()
    
    viewer = WebSocketLogViewer(args.log_dir)
    
    if args.stats:
        viewer.show_connection_stats()
    elif args.performance:
        viewer.show_performance_metrics()
    elif args.errors:
        viewer.show_errors(args.errors)
    elif args.live:
        viewer.show_live_logs(args.type, args.robot_id)
    else:
        viewer.show_recent_logs(args.type, args.lines, args.level, args.robot_id)

if __name__ == "__main__":
    main() 