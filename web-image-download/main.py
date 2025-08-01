"""
网页图片下载工具 - 主程序入口
启动GUI应用程序
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# 添加当前目录到Python路径，确保能导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import ImageDownloaderGUI


def check_dependencies():
    """
    检查必要的依赖包是否已安装
    
    Returns:
        bool: 所有依赖都已安装返回True，否则返回False
    """
    required_packages = [
        'requests',
        'beautifulsoup4',
        'Pillow',
        'lxml',
        'playwright'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'Pillow':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"缺少必要的依赖包: {', '.join(missing_packages)}\n\n"
        error_msg += "请运行以下命令安装依赖:\n"
        error_msg += "pip install -r requirements.txt"
        
        # 如果缺少playwright，提供额外说明
        if 'playwright' in missing_packages:
            error_msg += "\n\n安装完成后，还需要运行:\n"
            error_msg += "playwright install"
        
        messagebox.showerror("依赖错误", error_msg)
        return False
    
    return True


def check_playwright_browsers():
    """
    检查Playwright浏览器是否已安装
    
    Returns:
        bool: 浏览器已安装返回True，否则返回False
    """
    try:
        import subprocess
        import sys
        import os
        
        # 检查是否为exe环境
        if getattr(sys, 'frozen', False):
            # exe环境，使用相对路径
            playwright_path = os.path.join(os.path.dirname(sys.executable), 'playwright')
        else:
            # 开发环境，使用Python模块
            playwright_path = sys.executable
        
        # 检查playwright是否可用
        try:
            result = subprocess.run([playwright_path, '-m', 'playwright', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
        except:
            return False
        
        # 检查浏览器是否已安装
        try:
            result = subprocess.run([playwright_path, '-m', 'playwright', 'install', '--dry-run'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
        
    except Exception:
        return False


def install_playwright_browsers():
    """
    安装Playwright浏览器
    
    Returns:
        bool: 安装成功返回True，否则返回False
    """
    try:
        import subprocess
        import sys
        import os
        
        # 检查是否为exe环境
        if getattr(sys, 'frozen', False):
            # exe环境，使用相对路径
            playwright_path = os.path.join(os.path.dirname(sys.executable), 'playwright')
        else:
            # 开发环境，使用Python模块
            playwright_path = sys.executable
        
        # 显示安装进度
        print("正在安装Playwright浏览器...")
        print("这可能需要几分钟时间，请耐心等待...")
        
        # 安装浏览器
        try:
            result = subprocess.run([playwright_path, '-m', 'playwright', 'install', 'chromium'], 
                                  capture_output=True, text=True, timeout=300)  # 5分钟超时
            
            if result.returncode == 0:
                print("Playwright浏览器安装成功!")
                return True
            else:
                print(f"安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("安装超时，请检查网络连接")
            return False
            
    except Exception as e:
        print(f"安装过程出错: {e}")
        return False


def main():
    """
    主函数
    """
    try:
        # 检查依赖
        if not check_dependencies():
            return
        
        # 检查Playwright浏览器
        if not check_playwright_browsers():
            print("检测到Playwright浏览器未安装")
            response = messagebox.askyesno(
                "浏览器安装", 
                "检测到Playwright浏览器未安装。\n\n"
                "高级模式需要安装浏览器才能正常工作。\n"
                "是否现在安装浏览器？\n\n"
                "注意：安装过程可能需要几分钟时间。"
            )
            
            if response:
                if install_playwright_browsers():
                    messagebox.showinfo("安装成功", "Playwright浏览器安装成功！")
                else:
                    messagebox.showwarning(
                        "安装失败", 
                        "浏览器安装失败。\n"
                        "您仍可以使用简单模式，但高级模式可能无法正常工作。\n\n"
                        "您可以稍后手动运行: playwright install"
                    )
        
        # 创建主窗口
        root = tk.Tk()
        
        # 设置应用程序图标（如果有的话）
        try:
            # 尝试设置应用程序图标
            if os.path.exists("icon.ico"):
                root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建GUI应用
        app = ImageDownloaderGUI(root)
        
        # 设置窗口关闭事件
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # 显示欢迎信息
        print("=" * 50)
        print("网页图片下载工具")
        print("=" * 50)
        print("功能特性:")
        print("- 支持从任意网站下载图片")
        print("- 自动提取网页中的图片链接")
        print("- 批量下载，支持进度显示")
        print("- 智能文件名处理")
        print("- 支持多种图片格式")
        print("=" * 50)
        
        # 启动GUI事件循环
        root.mainloop()
        
    except Exception as e:
        # 捕获未处理的异常
        error_msg = f"程序运行出错:\n{str(e)}"
        print(error_msg)
        messagebox.showerror("程序错误", error_msg)


if __name__ == "__main__":
    main() 