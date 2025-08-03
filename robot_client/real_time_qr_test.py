#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import qrcode
import json
import time
import random
from PIL import Image, ImageDraw, ImageFont
import pygame
import sys

class RealTimeQRTest:
    """实时二维码测试工具"""
    
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Real-time QR Code Test Tool")
        
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'blue': (0, 100, 255),
            'green': (0, 200, 0),
            'red': (255, 0, 0),
            'gray': (128, 128, 128)
        }
        
        self.current_qr_data = None
        self.qr_surface = None
        self.is_running = True
    
    def generate_sample_qr_data(self):
        """生成示例二维码数据"""
        sample_data = {
            "order_id": random.randint(1, 999),
            "student_id": random.randint(1, 999),
            "student_name": random.choice(["张三", "李四", "王五", "赵六", "钱七"]),
            "delivery_building": random.choice(["宿舍楼A", "宿舍楼B", "图书馆", "教学楼", "食堂"]),
            "delivery_room": f"{random.randint(1, 20)}{random.randint(1, 9):02d}",
            "package_type": random.choice(["书籍", "电子产品", "文件", "衣物", "食品"]),
            "signature": f"sig_{random.randint(100000, 999999)}"
        }
        return sample_data
    
    def create_qr_code(self, data):
        """创建二维码"""
        try:
            # 创建二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(data, ensure_ascii=False))
            qr.make(fit=True)
            
            # 生成图像
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为Pygame surface
            qr_surface = pygame.image.fromstring(qr_image.tobytes(), qr_image.size, qr_image.mode)
            
            return qr_surface
            
        except Exception as e:
            print(f"创建二维码失败: {e}")
            return None
    
    def draw(self):
        """绘制界面"""
        self.screen.fill(self.colors['white'])
        
        # 标题
        title = self.font.render("Real-time QR Code Test Tool", True, self.colors['black'])
        self.screen.blit(title, (50, 30))
        
        # 说明
        instructions = [
            "Press SPACE to generate new QR code",
            "Press R to generate random order data",
            "Press S to save current QR code",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.colors['gray'])
            self.screen.blit(text, (50, 80 + i * 25))
        
        # 显示当前二维码数据
        if self.current_qr_data:
            data_text = self.small_font.render("Current QR Data:", True, self.colors['black'])
            self.screen.blit(data_text, (50, 200))
            
            y_offset = 230
            for key, value in self.current_qr_data.items():
                line = f"{key}: {value}"
                text = self.small_font.render(line, True, self.colors['black'])
                self.screen.blit(text, (50, y_offset))
                y_offset += 20
        
        # 显示二维码
        if self.qr_surface:
            # 缩放二维码以适应显示
            scaled_qr = pygame.transform.scale(self.qr_surface, (300, 300))
            self.screen.blit(scaled_qr, (450, 200))
            
            # 二维码说明
            qr_info = self.small_font.render("Scan this QR code with the robot client", True, self.colors['blue'])
            self.screen.blit(qr_info, (450, 520))
        
        pygame.display.flip()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_SPACE:
                    self.generate_new_qr()
                elif event.key == pygame.K_r:
                    self.generate_random_qr()
                elif event.key == pygame.K_s:
                    self.save_qr_code()
    
    def generate_new_qr(self):
        """生成新的二维码"""
        data = {
            "order_id": 1,
            "student_id": 2,
            "student_name": "张三",
            "delivery_building": "宿舍楼A",
            "delivery_room": "101",
            "package_type": "书籍",
            "signature": "abc123def456ghi789"
        }
        self.current_qr_data = data
        self.qr_surface = self.create_qr_code(data)
        print("📱 生成新二维码")
    
    def generate_random_qr(self):
        """生成随机二维码"""
        self.current_qr_data = self.generate_sample_qr_data()
        self.qr_surface = self.create_qr_code(self.current_qr_data)
        print("🎲 生成随机二维码数据")
    
    def save_qr_code(self):
        """保存二维码"""
        if self.qr_surface:
            try:
                # 转换Pygame surface为PIL图像
                qr_string = pygame.image.tostring(self.qr_surface, 'RGB')
                qr_image = Image.frombytes('RGB', self.qr_surface.get_size(), qr_string)
                
                # 保存图像
                filename = f"qr_code_{int(time.time())}.png"
                qr_image.save(filename)
                print(f"💾 二维码已保存为: {filename}")
            except Exception as e:
                print(f"❌ 保存失败: {e}")
    
    def run(self):
        """运行测试工具"""
        print("🔍 启动实时二维码测试工具")
        print("📱 使用空格键生成新二维码")
        print("🎲 使用R键生成随机数据")
        print("💾 使用S键保存二维码")
        print("🚪 使用ESC键退出")
        
        # 生成初始二维码
        self.generate_new_qr()
        
        while self.is_running:
            self.handle_events()
            self.draw()
        
        pygame.quit()

def main():
    """主函数"""
    qr_test = RealTimeQRTest()
    qr_test.run()

if __name__ == "__main__":
    main() 