"""
测试脚本
用于验证图片下载器的功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from downloader import ImageDownloader
from utils import validate_url, is_image_url


def test_url_validation():
    """
    测试URL验证功能
    """
    print("测试URL验证功能...")
    
    test_urls = [
        "https://www.python.org",
        "http://example.com",
        "invalid-url",
        "ftp://example.com",
        "https://",
        ""
    ]
    
    for url in test_urls:
        is_valid = validate_url(url)
        print(f"  {url}: {'✓' if is_valid else '✗'}")


def test_image_url_detection():
    """
    测试图片URL检测功能
    """
    print("\n测试图片URL检测功能...")
    
    test_urls = [
        "https://example.com/image.jpg",
        "https://example.com/photo.png",
        "https://example.com/picture.gif",
        "https://example.com/icon.ico",
        "https://example.com/data-src/image.webp",
        "https://example.com/page.html",
        "https://example.com/script.js"
    ]
    
    for url in test_urls:
        is_image = is_image_url(url)
        print(f"  {url}: {'图片' if is_image else '非图片'}")


def test_downloader():
    """
    测试下载器功能
    """
    print("\n测试下载器功能...")
    
    # 创建下载器实例
    downloader = ImageDownloader("./test_downloads")
    
    # 设置回调函数
    def progress_callback(progress):
        print(f"  进度: {progress:.1f}%")
    
    def status_callback(message):
        print(f"  状态: {message}")
    
    downloader.set_callbacks(progress_callback, status_callback)
    
    # 测试URL（使用一个简单的网站）
    test_url = "https://www.python.org"
    
    try:
        print(f"开始测试下载: {test_url}")
        
        # 提取图片链接
        image_urls = downloader.extract_images_from_url(test_url)
        print(f"找到 {len(image_urls)} 张图片")
        
        # 只下载前3张图片进行测试
        if image_urls:
            print("下载前3张图片进行测试...")
            stats = downloader.download_images_from_url(test_url, max_images=3)
            print(f"下载完成: {stats}")
        else:
            print("未找到图片")
            
    except Exception as e:
        print(f"测试失败: {e}")


def main():
    """
    主测试函数
    """
    print("=" * 50)
    print("图片下载器功能测试")
    print("=" * 50)
    
    # 测试各个功能模块
    test_url_validation()
    test_image_url_detection()
    test_downloader()
    
    print("\n测试完成!")


if __name__ == "__main__":
    main() 