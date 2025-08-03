#!/bin/bash

# 快递车客户端启动脚本 (Mac模拟版)

echo "🤖 启动 CulverBot 快递车客户端 (Mac模拟版)..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3，请先安装 pip3"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "📝 正在复制配置文件..."
    cp env.example .env
    echo "✅ 配置文件已创建，请编辑 .env 文件设置正确的参数"
    echo "   特别是 SERVER_URL 需要设置为你的Django服务器地址"
fi

# 安装依赖
echo "📦 安装Python依赖包..."
pip3 install -r requirements.txt

# 创建日志目录
mkdir -p logs

# 启动客户端
echo "🚀 启动快递车客户端..."
python3 main.py 