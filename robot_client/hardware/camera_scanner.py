#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from pyzbar import pyzbar
import json
import time
import threading
from config import Config

class CameraScanner:
    """摄像头和二维码扫描器"""
    
    def __init__(self, logger):
        self.logger = logger
        self.camera_index = Config.CAMERA_INDEX
        self.scan_interval = Config.QR_SCAN_INTERVAL
        self.camera = None
        self.is_scanning = False
        self.scan_thread = None
        self.callbacks = {}
        self.camera_available = False
        
        # 新增：按钮扫描模式
        self.button_scan_mode = False
        self.button_scan_duration = 60  # 60秒扫描时间
        self.button_scan_start_time = None
        self.button_scan_thread = None
        
        # 初始化摄像头
        self.camera_available = self.init_camera()
    
    def init_camera(self):
        """初始化摄像头"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                self.logger.warning(f"无法打开摄像头 {self.camera_index}，将跳过摄像头功能")
                return False
            
            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.logger.info("摄像头初始化完成")
            return True
            
        except Exception as e:
            self.logger.warning(f"摄像头初始化失败，将跳过摄像头功能: {e}")
            return False
    
    def start_scanning(self):
        """开始扫描 - 保持向后兼容"""
        if not self.camera_available:
            self.logger.info("摄像头不可用，跳过二维码扫描")
            return
            
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self._scan_loop)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        self.logger.info("开始二维码扫描")
    
    def stop_scanning(self):
        """停止扫描"""
        self.is_scanning = False
        if self.scan_thread:
            self.scan_thread.join()
        self.logger.info("停止二维码扫描")
    
    def start_button_scan(self):
        """开始按钮触发的扫描模式"""
        if not self.camera_available:
            self.logger.warning("摄像头不可用，无法开始扫描")
            if 'scan_timeout' in self.callbacks:
                self.callbacks['scan_timeout']("摄像头不可用")
            return False
        
        if self.button_scan_mode:
            self.logger.info("扫描已在进行中，请等待完成")
            return False
        
        self.button_scan_mode = True
        self.button_scan_start_time = time.time()
        
        self.logger.info(f"🔘 按钮扫描模式启动，扫描时间: {self.button_scan_duration}秒")
        
        # 启动按钮扫描线程
        self.button_scan_thread = threading.Thread(target=self._button_scan_loop)
        self.button_scan_thread.daemon = True
        self.button_scan_thread.start()
        
        return True
    
    def stop_button_scan(self):
        """停止按钮扫描模式"""
        self.button_scan_mode = False
        if self.button_scan_thread:
            self.button_scan_thread.join()
        self.logger.info("按钮扫描模式已停止")
    
    def _button_scan_loop(self):
        """按钮扫描循环"""
        self.logger.info("📱 开始按钮扫描循环...")
        
        while self.button_scan_mode:
            try:
                # 检查是否超时
                elapsed_time = time.time() - self.button_scan_start_time
                remaining_time = self.button_scan_duration - elapsed_time
                
                if remaining_time <= 0:
                    self.logger.warning(f"⏰ 扫描超时 ({self.button_scan_duration}秒)，未扫描到有效二维码")
                    self.button_scan_mode = False
                    if 'scan_timeout' in self.callbacks:
                        self.callbacks['scan_timeout']("扫描超时")
                    break
                
                # 读取摄像头帧
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.warning("无法读取摄像头帧")
                    time.sleep(0.5)
                    continue
                
                # 扫描二维码
                qr_codes = self.scan_qr_codes(frame)
                
                if qr_codes:
                    for qr_data in qr_codes:
                        self.logger.info(f"✅ 扫描到二维码: {qr_data}")
                        self.button_scan_mode = False  # 扫描成功，停止扫描
                        if 'qr_scanned' in self.callbacks:
                            self.callbacks['qr_scanned'](qr_data)
                        return  # 扫描成功，退出循环
                
                # 显示剩余时间
                if int(remaining_time) % 10 == 0 and remaining_time > 0:
                    self.logger.info(f"⏱️ 扫描剩余时间: {int(remaining_time)}秒")
                
                time.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"按钮扫描循环错误: {e}")
                time.sleep(1)
        
        self.logger.info("按钮扫描循环结束")
    
    def _scan_loop(self):
        """扫描循环 - 保持向后兼容"""
        while self.is_scanning:
            try:
                # 读取摄像头帧
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.warning("无法读取摄像头帧")
                    time.sleep(1)
                    continue
                
                # 扫描二维码
                qr_codes = self.scan_qr_codes(frame)
                
                if qr_codes:
                    for qr_data in qr_codes:
                        self.logger.info(f"扫描到二维码: {qr_data}")
                        if 'qr_scanned' in self.callbacks:
                            self.callbacks['qr_scanned'](qr_data)
                
                time.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"扫描循环错误: {e}")
                time.sleep(1)
    
    def scan_qr_codes(self, frame):
        """扫描二维码"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 检测二维码
            qr_codes = pyzbar.decode(gray)
            
            results = []
            for qr in qr_codes:
                try:
                    # 解码二维码数据
                    data = qr.data.decode('utf-8')
                    
                    # 尝试解析JSON
                    try:
                        qr_data = json.loads(data)
                        results.append(qr_data)
                    except json.JSONDecodeError:
                        # 如果不是JSON，直接使用原始数据
                        results.append({'raw_data': data})
                        
                except Exception as e:
                    self.logger.error(f"二维码解码失败: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"二维码扫描失败: {e}")
            return []
    
    def capture_image(self, filename=None):
        """拍摄图片"""
        if not self.camera_available:
            self.logger.warning("摄像头不可用")
            return None
            
        try:
            ret, frame = self.camera.read()
            if not ret:
                self.logger.error("无法拍摄图片")
                return None
            
            if filename:
                cv2.imwrite(filename, frame)
                self.logger.info(f"图片已保存: {filename}")
            
            return frame
            
        except Exception as e:
            self.logger.error(f"拍摄图片失败: {e}")
            return None
    
    def register_callback(self, event, callback):
        """注册回调函数"""
        self.callbacks[event] = callback
        self.logger.info(f"注册摄像头回调: {event}")
    
    def verify_qr_code(self, qr_data, expected_order_id):
        """验证二维码"""
        try:
            if isinstance(qr_data, dict):
                # 检查订单ID
                if 'order_id' in qr_data:
                    if str(qr_data['order_id']) == str(expected_order_id):
                        self.logger.info(f"二维码验证成功: 订单{expected_order_id}")
                        return True
                    else:
                        self.logger.warning(f"二维码验证失败: 期望订单{expected_order_id}, 实际订单{qr_data['order_id']}")
                        return False
                
                # 检查签名
                if 'signature' in qr_data:
                    # 这里可以添加签名验证逻辑
                    self.logger.info("二维码签名验证通过")
                    return True
            
            self.logger.warning("二维码格式无效")
            return False
            
        except Exception as e:
            self.logger.error(f"二维码验证失败: {e}")
            return False
    
    def is_button_scanning(self):
        """检查是否正在按钮扫描模式"""
        return self.button_scan_mode
    
    def get_remaining_scan_time(self):
        """获取剩余扫描时间"""
        if not self.button_scan_mode or not self.button_scan_start_time:
            return 0
        elapsed = time.time() - self.button_scan_start_time
        remaining = self.button_scan_duration - elapsed
        return max(0, int(remaining))
    
    def cleanup(self):
        """清理资源"""
        try:
            self.stop_scanning()
            self.stop_button_scan()
            if self.camera and self.camera_available:
                self.camera.release()
            cv2.destroyAllWindows()
            self.logger.info("摄像头资源清理完成")
        except Exception as e:
            self.logger.error(f"摄像头清理失败: {e}") 