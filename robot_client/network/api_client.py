#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from config import Config

class APIClient:
    """API客户端"""
    
    def __init__(self, logger):
        self.logger = logger
        self.server_url = Config.SERVER_URL
        self.robot_id = Config.ROBOT_ID
        self.session = requests.Session()
        self.session.timeout = 10
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'RobotClient/{Config.ROBOT_NAME}'
        })
        
        # 获取JWT token
        self.access_token = self._get_auth_token()
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
    
    def _get_auth_token(self):
        """获取JWT认证token"""
        try:
            # 使用机器人专用的认证方式
            auth_data = {
                'username': 'root',  # 使用超级用户
                'password': 'test123456'  # 使用我们设置的密码
            }
            
            response = requests.post(
                f"{self.server_url}/api/token/",
                json=auth_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.logger.info("✅ 机器人认证成功")
                return token_data['access']
            else:
                self.logger.error(f"❌ 机器人认证失败: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ 认证异常: {e}")
            return None
    
    def get_robot_status(self):
        """获取机器人详细状态"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/status/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"获取机器人状态成功: {data['status']}")
                return data
            else:
                self.logger.error(f"获取机器人状态失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def update_robot_status(self, location=None, battery=None, door_status=None, status=None):
        """更新机器人状态"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/update_status/"
            
            data = {}
            if location:
                data['location'] = location
            if battery is not None:
                data['battery'] = battery
            if door_status:
                data['door_status'] = door_status
            if status:
                data['status'] = status
            
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"状态更新成功: {result['message']}")
                return result
            else:
                self.logger.error(f"状态更新失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def qr_scanned(self, order_id, qr_data):
        """二维码扫描处理"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/qr_scanned/"
            data = {
                'order_id': order_id,
                'qr_data': qr_data
            }
            
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"二维码扫描成功: {result['message']}")
                return result
            else:
                self.logger.error(f"二维码扫描失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def start_qr_wait(self, order_id):
        """开始等待二维码扫描"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/start_qr_wait/"
            data = {'order_id': order_id}
            
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"开始等待二维码扫描: {result['message']}")
                return result
            else:
                self.logger.error(f"开始等待二维码扫描失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def auto_return(self):
        """自动返航"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/auto_return/"
            response = self.session.post(url)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"自动返航: {result['message']}")
                return result
            else:
                self.logger.error(f"自动返航失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def get_current_orders(self):
        """获取当前订单"""
        try:
            url = f"{self.server_url}{Config.API_ENDPOINTS['current_orders'](self.robot_id)}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"获取订单成功，订单数量: {len(data.get('current_orders', []))}")
                return data
            else:
                self.logger.error(f"获取订单失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def get_commands(self):
        """获取待执行的指令"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/get_commands/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get('pending_commands', [])
                self.logger.info(f"获取指令成功，待执行指令数量: {len(commands)}")
                return commands
            else:
                self.logger.error(f"获取指令失败: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return []
    
    def execute_command(self, command_id, result="执行成功"):
        """执行指令并报告结果"""
        try:
            url = f"{self.server_url}/api/robots/{self.robot_id}/execute_command/"
            response = self.session.post(url, json={
                'command_id': command_id,
                'result': result
            })
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"指令执行成功: {data.get('message', '')}")
                return True
            else:
                self.logger.error(f"指令执行失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return False
    
    def receive_orders(self):
        """接收订单分配"""
        try:
            url = f"{self.server_url}{Config.API_ENDPOINTS['receive_orders'](self.robot_id)}"
            response = self.session.post(url, json={'action': 'receive'})
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"接收订单成功: {data}")
                return data
            else:
                self.logger.error(f"接收订单失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def start_delivery(self):
        """开始配送"""
        try:
            url = f"{self.server_url}{Config.API_ENDPOINTS['start_delivery'](self.robot_id)}"
            response = self.session.post(url, json={'action': 'close_door_and_start'})
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"开始配送成功: {data}")
                return data
            else:
                self.logger.error(f"开始配送失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def update_order_status(self, order_id, new_status):
        """更新订单状态"""
        try:
            url = f"{self.server_url}{Config.API_ENDPOINTS['update_order'](order_id)}"
            response = self.session.patch(url, json={'status': new_status})
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"更新订单{order_id}状态为{new_status}成功")
                return data
            else:
                self.logger.error(f"更新订单状态失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
    
    def test_connection(self):
        """测试连接"""
        try:
            response = self.session.get(f"{self.server_url}/api/robots/{self.robot_id}/")
            if response.status_code == 200:
                self.logger.info("服务器连接正常")
                return True
            else:
                self.logger.error(f"服务器连接失败: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"服务器连接失败: {e}")
            return False 