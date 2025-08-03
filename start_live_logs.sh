#!/bin/bash

# 🚀 启动实时WebSocket日志监控
# 这个脚本会在新窗口中启动实时日志监控

echo "🔴 启动实时WebSocket日志监控窗口..."
echo ""

# 检查screen是否可用
if command -v screen &> /dev/null; then
    echo "✅ 使用screen创建新窗口..."
    
    # 创建新的screen会话
    screen -dmS websocket-logs bash -c "
        echo '🔴 WebSocket实时日志监控窗口'
        echo '📋 监控类型: events (重要事件)'
        echo '⏹️  按 Ctrl+A 然后按 D 来分离窗口'
        echo '🔗 使用 screen -r websocket-logs 重新连接'
        echo '=' * 80
        echo ''
        
        # 进入项目目录
        cd /Users/jjzhang/Documents/ALANG
        
        # 启动实时日志监控
        docker-compose -f docker_deploy/docker-compose.yml exec backend tail -f /app/logs/websocket_events.log
        
        # 保持窗口打开
        exec bash
    "
    
    echo "✅ 实时日志窗口已创建!"
    echo ""
    echo "📋 窗口管理命令:"
    echo "  🔗 连接到窗口: screen -r websocket-logs"
    echo "  📋 查看所有窗口: screen -ls"
    echo "  ❌ 关闭窗口: screen -S websocket-logs -X quit"
    echo ""
    echo "💡 提示: 按 Ctrl+A 然后按 D 可以分离窗口（保持运行）"
    
elif command -v tmux &> /dev/null; then
    echo "✅ 使用tmux创建新窗口..."
    
    # 创建新的tmux会话
    tmux new-session -d -s websocket-logs "
        echo '🔴 WebSocket实时日志监控窗口'
        echo '📋 监控类型: events (重要事件)'
        echo '⏹️  按 Ctrl+B 然后按 D 来分离窗口'
        echo '🔗 使用 tmux attach -t websocket-logs 重新连接'
        echo '=' * 80
        echo ''
        
        cd /Users/jjzhang/Documents/ALANG
        docker-compose -f docker_deploy/docker-compose.yml exec backend tail -f /app/logs/websocket_events.log
    "
    
    echo "✅ 实时日志窗口已创建!"
    echo ""
    echo "📋 窗口管理命令:"
    echo "  🔗 连接到窗口: tmux attach -t websocket-logs"
    echo "  📋 查看所有窗口: tmux list-sessions"
    echo "  ❌ 关闭窗口: tmux kill-session -t websocket-logs"
    
else
    echo "❌ 未找到screen或tmux，使用简单方法..."
    echo ""
    echo "🔴 在当前窗口启动实时日志监控:"
    echo "⏹️  按 Ctrl+C 停止监控"
    echo ""
    
    # 直接在当前窗口启动
    cd docker_deploy
    docker-compose exec backend tail -f /app/logs/websocket_events.log
fi 