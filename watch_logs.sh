#!/bin/bash

# 🔍 简单的实时WebSocket日志查看脚本

echo "🔴 启动实时WebSocket日志监控..."
echo "📋 监控类型: events (重要事件)"
echo "⏹️  按 Ctrl+C 停止监控"
echo "=================================================="
echo ""

# 检查Docker容器是否运行
if ! docker-compose -f docker_deploy/docker-compose.yml ps | grep -q "Up"; then
    echo "❌ Docker容器未运行，请先启动服务："
    echo "   cd docker_deploy && docker-compose up -d"
    exit 1
fi

# 检查日志文件是否存在
if ! docker-compose -f docker_deploy/docker-compose.yml exec backend test -f /app/logs/websocket_events.log; then
    echo "⚠️  WebSocket日志文件不存在，可能还没有WebSocket活动"
    echo "📡 正在监控系统后端日志..."
    echo ""
    docker-compose -f docker_deploy/docker-compose.yml exec backend tail -f /app/logs/system_backend.log | grep -i websocket
else
    echo "📡 正在监控WebSocket事件日志..."
    echo ""
    docker-compose -f docker_deploy/docker-compose.yml exec backend tail -f /app/logs/websocket_events.log
fi 