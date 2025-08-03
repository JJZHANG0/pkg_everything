#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env')

class Config:
    """机器人配置类"""
    
    # 服务器配置
    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:8000')
    ROBOT_ID = int(os.getenv('ROBOT_ID', '1'))
    ROBOT_NAME = os.getenv('ROBOT_NAME', 'Robot-001')
    
    # 轮询配置
    POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '3'))  # 秒
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))  # 秒
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/robot.log')
    
    # GPIO引脚配置
    GPIO_PINS = {
        'DOOR_SENSOR': 17,      # 门传感器
        'LOADING_BUTTON': 18,   # 装货按钮
        'DELIVERY_BUTTON': 23,  # 开始配送按钮
        'EMERGENCY_STOP': 24,   # 紧急停止按钮
        'LED_STATUS': 25,       # 状态LED
        'LED_LOADING': 8,       # 装货LED
        'LED_DELIVERING': 7,    # 配送LED
        'BUZZER': 12,           # 蜂鸣器
    }
    
    # 摄像头配置
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
    QR_SCAN_INTERVAL = int(os.getenv('QR_SCAN_INTERVAL', '1'))  # 秒
    
    # API端点
    API_ENDPOINTS = {
        'current_orders': lambda robot_id: f'/api/robots/{robot_id}/current_orders/',
        'receive_orders': lambda robot_id: f'/api/robots/{robot_id}/receive_orders/',
        'start_delivery': lambda robot_id: f'/api/robots/{robot_id}/start_delivery/',
        'update_order': lambda order_id: f'/api/dispatch/orders/{order_id}/',
    }
    
    # 状态定义
    STATUS = {
        'IDLE': '空闲',
        'LOADING': '装货中',
        'DELIVERING': '配送中',
        'MAINTENANCE': '维护中'
    }
    
    # 订单状态
    ORDER_STATUS = {
        'PENDING': '待处理',
        'ASSIGNED': '已分配',
        'DELIVERING': '配送中',
        'DELIVERED': '已送达',
        'CANCELLED': '已取消'
    } 