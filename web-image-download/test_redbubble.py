"""
Redbubble网站下载测试脚本
专门用于测试Redbubble网站的图片下载功能
"""

import sys
import os
import asyncio

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright_downloader import PlaywrightDownloader


async def test_redbubble_download():
    """
    测试Redbubble网站下载
    """
    print("=" * 60)
    print("Redbubble网站下载测试")
    print("=" * 60)
    
    # 测试URL
    test_url = "https://www.redbubble.com/people/paisleydrawrns/explore?page=6&sortOrder=recent"
    
    # 创建下载器
    downloader = PlaywrightDownloader("./test_redbubble_downloads")
    
    # 设置回调函数
    def progress_callback(progress):
        print(f"进度: {progress:.1f}%")
    
    def status_callback(message):
        print(f"状态: {message}")
    
    downloader.set_callbacks(progress_callback, status_callback)
    
    try:
        print(f"开始测试Redbubble网站: {test_url}")
        print("使用高级模式（Playwright）进行下载...")
        
        # 执行下载（只下载前5张图片进行测试）
        stats = await downloader.download_images_from_url(
            url=test_url,
            max_images=5,
            scroll_count=8
        )
        
        print("\n" + "=" * 60)
        print("下载完成！统计信息:")
        print("=" * 60)
        print(f"总图片数: {stats['total_images']}")
        print(f"成功下载: {stats['downloaded_images']}")
        print(f"下载失败: {stats['failed_images']}")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print(f"总大小: {stats['total_size_str']}")
        
        if stats['downloaded_images'] > 0:
            print("\n✅ 测试成功！Redbubble图片下载功能正常工作")
        else:
            print("\n❌ 测试失败！没有下载到任何图片")
            
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


async def test_image_extraction():
    """
    测试图片提取功能
    """
    print("\n" + "=" * 60)
    print("图片提取功能测试")
    print("=" * 60)
    
    test_url = "https://www.redbubble.com/people/paisleydrawrns/explore?page=6&sortOrder=recent"
    
    downloader = PlaywrightDownloader("./test_extraction")
    
    def status_callback(message):
        print(f"状态: {message}")
    
    downloader.set_callbacks(status_callback=status_callback)
    
    try:
        # 初始化浏览器
        await downloader.init_browser()
        
        # 导航到页面
        await downloader.navigate_to_page(test_url)
        
        # Redbubble优化
        await downloader.optimize_for_redbubble()
        
        # 滚动页面
        await downloader.scroll_and_load_content(5)
        
        # 提取图片
        image_urls = await downloader.extract_images_from_page()
        
        print(f"\n找到 {len(image_urls)} 张图片")
        
        if image_urls:
            print("\n前5张图片URL:")
            for i, url in enumerate(image_urls[:5], 1):
                print(f"{i}. {url}")
        
        # 关闭浏览器
        await downloader.close_browser()
        
    except Exception as e:
        print(f"提取测试出错: {e}")
        await downloader.close_browser()


def main():
    """
    主测试函数
    """
    print("Redbubble网站下载功能测试")
    print("请选择测试类型:")
    print("1. 完整下载测试（下载5张图片）")
    print("2. 图片提取测试（只提取不下载）")
    print("3. 两个测试都运行")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(test_redbubble_download())
    elif choice == "2":
        asyncio.run(test_image_extraction())
    elif choice == "3":
        asyncio.run(test_image_extraction())
        asyncio.run(test_redbubble_download())
    else:
        print("无效选择，运行完整测试...")
        asyncio.run(test_redbubble_download())


if __name__ == "__main__":
    main() 