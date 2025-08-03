#!/bin/bash

# 🤖 WebSocket测试启动脚本
# 供同事快速开始WebSocket测试使用

echo "🤖 WebSocket测试启动脚本"
echo "================================"

# 检查Python环境
echo "🔍 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到Python环境，请先安装Python"
    exit 1
fi

echo "✅ 使用Python命令: $PYTHON_CMD"

# 检查websockets库
echo "🔍 检查websockets库..."
$PYTHON_CMD -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装websockets库..."
    $PYTHON_CMD -m pip install websockets
    if [ $? -ne 0 ]; then
        echo "❌ 安装websockets库失败"
        exit 1
    fi
fi

echo "✅ websockets库已安装"

# 显示配置信息
echo ""
echo "📋 配置信息"
echo "================================"
echo "服务器地址: ws://你的服务器IP:8001/robot/1"
echo "机器人ID: 1"
echo ""

# 询问是否修改配置
read -p "是否需要修改服务器地址？(y/n): " modify_config
if [ "$modify_config" = "y" ] || [ "$modify_config" = "Y" ]; then
    echo ""
    echo "📝 请修改 robot_test_client.py 中的服务器地址"
    echo "找到这一行:"
    echo "server_url = \"ws://localhost:8001/robot/1\""
    echo "修改为你的实际服务器地址"
    echo ""
    read -p "修改完成后按回车继续..."
fi

# 启动测试客户端
echo ""
echo "🚀 启动WebSocket测试客户端..."
echo "================================"
echo "按 Ctrl+C 停止测试"
echo ""

$PYTHON_CMD robot_test_client.py

echo ""
echo "✅ 测试完成" 