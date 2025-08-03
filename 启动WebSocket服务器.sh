#!/bin/bash

echo "🚀 启动WebSocket服务器..."
echo "📡 端口: 8001"
echo "🔗 地址: ws://localhost:8001/robot/{robot_id}"
echo "=" * 50

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查websockets库是否安装
if ! python3 -c "import websockets" &> /dev/null; then
    echo "⚠️ websockets库未安装，正在安装..."
    pip3 install websockets
fi

# 启动服务器
echo "✅ 启动WebSocket服务器..."
python3 websocket_server_final.py 