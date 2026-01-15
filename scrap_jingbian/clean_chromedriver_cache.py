#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理ChromeDriver缓存脚本
用于解决webdriver_manager缓存问题
"""

import os
import shutil
from pathlib import Path

def clean_chromedriver_cache():
    """清理webdriver_manager的ChromeDriver缓存"""
    try:
        # webdriver_manager的默认缓存目录
        cache_dir = Path.home() / ".wdm" / "drivers" / "chromedriver"
        
        if cache_dir.exists():
            print(f"找到缓存目录: {cache_dir}")
            print("正在清理缓存...")
            
            # 删除整个chromedriver缓存目录
            shutil.rmtree(cache_dir)
            print("✓ ChromeDriver缓存已清理")
            print("下次运行程序时会自动重新下载ChromeDriver")
        else:
            print("未找到ChromeDriver缓存目录")
            
    except Exception as e:
        print(f"清理缓存时出错: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("ChromeDriver缓存清理工具")
    print("=" * 50)
    clean_chromedriver_cache()
    print("=" * 50)
