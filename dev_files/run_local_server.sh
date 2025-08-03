#!/bin/bash

echo "🔄 [1/4] 正在重启 nginx..."
sudo nginx -s stop
sudo nginx

echo "✅ nginx 已启动 ✅"
sleep 1

echo "🚀 [2/4] 启动 Django 后端服务..."
cd ~/Documents/PACKAGE_CRUISER/campus_delivery
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 &

sleep 2

echo "🌍 [3/4] 启动 ngrok 公网代理..."
ngrok http 80
