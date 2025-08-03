#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime
from config import Config

class RobotLogger:
    """机器人日志类"""
    
    def __init__(self):
        # 创建日志目录
        log_dir = os.path.dirname(Config.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置日志
        self.logger = logging.getLogger('RobotClient')
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 文件处理器
            file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化器
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message, data=None):
        """信息日志"""
        if data:
            self.logger.info(f"{message} - {data}")
        else:
            self.logger.info(message)
    
    def error(self, message, data=None):
        """错误日志"""
        if data:
            self.logger.error(f"{message} - {data}")
        else:
            self.logger.error(message)
    
    def warning(self, message, data=None):
        """警告日志"""
        if data:
            self.logger.warning(f"{message} - {data}")
        else:
            self.logger.warning(message)
    
    def debug(self, message, data=None):
        """调试日志"""
        if data:
            self.logger.debug(f"{message} - {data}")
        else:
            self.logger.debug(message)
    
    def critical(self, message, data=None):
        """严重错误日志"""
        if data:
            self.logger.critical(f"{message} - {data}")
        else:
            self.logger.critical(message) 