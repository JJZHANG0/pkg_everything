#!/bin/bash

# 机器人配送系统 - 日志查看器

echo "📋 机器人配送系统 - 日志查看器"
echo "================================"

# 检查logs目录是否存在
if [ ! -d "logs" ]; then
    echo "❌ logs目录不存在，正在创建..."
    mkdir -p logs
fi

# 进入logs目录
cd logs

# 检查日志文件是否存在，如果不存在则同步
if [ ! -f "robot_client.log" ] || [ ! -f "system_backend.log" ]; then
    echo "🔄 日志文件不存在，正在同步..."
    python sync_logs.py
fi

# 运行快速查看脚本
./quick_view.sh 