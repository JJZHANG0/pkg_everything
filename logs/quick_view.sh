#!/bin/bash

# 机器人配送系统 - 快速日志查看脚本

echo "📋 机器人配送系统 - 快速日志查看"
echo "=================================="

# 检查是否在logs目录
if [ ! -f "robot_client.log" ]; then
    echo "❌ 请在logs目录中运行此脚本"
    exit 1
fi

# 显示菜单
echo ""
echo "请选择要查看的日志类型:"
echo "1. 查看机器人日志 (最近20行)"
echo "2. 查看系统日志 (最近20行)"
echo "3. 查看前端日志说明"
echo "4. 实时监控所有日志"
echo "5. 查看日志摘要"
echo "6. 同步日志文件"
echo "7. 退出"
echo ""

read -p "请输入选择 (1-7): " choice

case $choice in
    1)
        echo ""
        echo "🤖 机器人客户端日志 (最近20行):"
        echo "----------------------------------------"
        tail -n 20 robot_client.log
        ;;
    2)
        echo ""
        echo "🖥️ 后端系统日志 (最近20行):"
        echo "----------------------------------------"
        tail -n 20 system_backend.log
        ;;
    3)
        echo ""
        echo "🌐 前端操作日志说明:"
        echo "----------------------------------------"
        cat frontend_operations.log
        ;;
    4)
        echo ""
        echo "🔍 实时日志监控 (按 Ctrl+C 停止):"
        echo "----------------------------------------"
        tail -f robot_client.log system_backend.log
        ;;
    5)
        echo ""
        echo "📊 日志摘要:"
        echo "----------------------------------------"
        echo "🤖 机器人日志: $(wc -l < robot_client.log) 行"
        echo "🖥️ 系统日志: $(wc -l < system_backend.log) 行"
        echo "🌐 前端日志: 模板文件"
        total=$(( $(wc -l < robot_client.log) + $(wc -l < system_backend.log) ))
        echo "📈 总日志行数: $total 行"
        ;;
    6)
        echo ""
        echo "🔄 同步日志文件..."
        python sync_logs.py
        ;;
    7)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成" 