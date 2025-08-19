#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Chrome浏览器（带调试端口）
用于连接现有浏览器进行爬虫操作
"""

import os
import sys
import subprocess
import platform
import time

def find_chrome_path():
    """查找Chrome浏览器安装路径"""
    system = platform.system()
    
    if system == "Windows":
        # Windows路径
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def kill_existing_chrome():
    """关闭现有的Chrome进程"""
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, check=False)
        elif system == "Darwin":  # macOS
            subprocess.run(["pkill", "-f", "Google Chrome"], 
                         capture_output=True, check=False)
        else:  # Linux
            subprocess.run(["pkill", "-f", "chrome"], 
                         capture_output=True, check=False)
        
        print("已关闭现有Chrome进程")
        time.sleep(2)  # 等待进程完全关闭
        
    except Exception as e:
        print(f"关闭Chrome进程时出错: {e}")

def start_chrome_debug(port=9222):
    """启动带调试端口的Chrome"""
    chrome_path = find_chrome_path()
    
    if not chrome_path:
        print("❌ 未找到Chrome浏览器")
        print("请确保已安装Google Chrome浏览器")
        return False
    
    print(f"✅ 找到Chrome: {chrome_path}")
    print(f"🚀 启动Chrome，调试端口: {port}")
    print("注意：这将关闭所有现有的Chrome窗口")
    print()
    
    # 关闭现有Chrome
    kill_existing_chrome()
    
    # 准备启动参数
    if platform.system() == "Windows":
        user_data_dir = os.path.join(os.environ.get('TEMP', ''), 'chrome_debug_profile')
    else:
        user_data_dir = os.path.join(os.path.expanduser('~'), '.chrome_debug_profile')
    
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-default-apps"
    ]
    
    try:
        # 启动Chrome
        process = subprocess.Popen(chrome_args)
        print(f"✅ Chrome已启动，进程ID: {process.pid}")
        print(f"🌐 调试地址: http://localhost:{port}")
        print()
        print("现在可以运行爬虫程序:")
        print("1. 运行: python baidu_health_scraper.py")
        print("2. 选择Excel文件")
        print("3. 选择 'y' 使用现有浏览器")
        print("4. 输入调试端口 (默认: {port})")
        print()
        print("按 Ctrl+C 退出此脚本（Chrome将继续运行）")
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\n用户中断，Chrome将继续在后台运行")
            print("如需完全关闭Chrome，请手动关闭浏览器窗口")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动Chrome失败: {e}")
        return False

def main():
    """主函数"""
    print("=== Chrome调试模式启动器 ===")
    print()
    
    # 获取调试端口
    try:
        port_input = input(f"请输入调试端口 (默认9222): ").strip()
        port = int(port_input) if port_input else 9222
    except ValueError:
        print("端口无效，使用默认端口9222")
        port = 9222
    
    print(f"使用端口: {port}")
    print()
    
    # 启动Chrome
    if start_chrome_debug(port):
        print("✅ 启动成功！")
    else:
        print("❌ 启动失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
