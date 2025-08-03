#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def main():
    """启动GUI选择器"""
    print("🤖 Robot Delivery System GUI Launcher")
    print("=" * 40)
    print("请选择GUI版本:")
    print("1. 🎮 现代化Pygame GUI (推荐)")
    print("2. 🖥️  简化Tkinter GUI (兼容性更好)")
    print("3. 🚫 无摄像头Tkinter GUI (最稳定)")
    print("4. ❌ 退出")
    print("=" * 40)
    
    while True:
        try:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == "1":
                print("🚀 启动Pygame GUI...")
                try:
                    import main_gui
                    main_gui.main()
                except Exception as e:
                    print(f"❌ Pygame GUI启动失败: {e}")
                    print("💡 建议尝试无摄像头版本")
                    input("按回车继续...")
                    continue
                break
                
            elif choice == "2":
                print("🚀 启动Tkinter GUI...")
                try:
                    import simple_gui
                    simple_gui.main()
                except Exception as e:
                    print(f"❌ Tkinter GUI启动失败: {e}")
                    print("💡 建议尝试无摄像头版本")
                    input("按回车继续...")
                    continue
                break
                
            elif choice == "3":
                print("🚀 启动无摄像头Tkinter GUI...")
                try:
                    import simple_gui_no_camera
                    simple_gui_no_camera.main()
                except Exception as e:
                    print(f"❌ 无摄像头GUI启动失败: {e}")
                    input("按回车继续...")
                    continue
                break
                
            elif choice == "4":
                print("👋 再见!")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请输入1-4")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main() 