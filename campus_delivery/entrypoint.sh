#!/bin/sh

echo "🚀 等待数据库启动中..."
sleep 5

echo "🧱 执行数据库迁移..."
python manage.py migrate

echo "✅ 启动 Django 服务..."
python manage.py runserver 0.0.0.0:8000

