#!/bin/bash

# 🔍 实时WebSocket日志查看脚本
# 使用方法: ./live_logs.sh [log_type] [robot_id]

LOG_TYPE=${1:-events}
ROBOT_ID=${2:-}

echo "🔴 启动实时WebSocket日志监控..."
echo "📋 日志类型: $LOG_TYPE"
if [ ! -z "$ROBOT_ID" ]; then
    echo "🤖 机器人ID: $ROBOT_ID"
fi
echo "⏹️  按 Ctrl+C 停止监控"
echo "=" * 80

# 检查日志文件是否存在
LOG_FILE="/app/logs/websocket_${LOG_TYPE}.log"
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在: $LOG_FILE"
    echo "📁 可用的日志文件:"
    docker-compose exec backend ls -la /app/logs/websocket_*.log 2>/dev/null || echo "   无WebSocket日志文件"
    exit 1
fi

# 实时监控日志
echo "📡 开始监控日志文件: $LOG_FILE"
echo ""

# 使用docker-compose exec实时查看日志
if [ -z "$ROBOT_ID" ]; then
    # 监控所有机器人的日志
    docker-compose exec backend tail -f "$LOG_FILE"
else
    # 监控特定机器人的日志
    docker-compose exec backend tail -f "$LOG_FILE" | grep "Robot-${ROBOT_ID}:"
fi 