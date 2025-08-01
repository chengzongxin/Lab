"""
Playwright图片下载器
支持JavaScript动态加载的网站
"""

import os
import time
import asyncio
import threading
from playwright.async_api import async_playwright
from PIL import Image
from utils import (
    validate_url, clean_filename, get_file_extension, 
    create_download_directory, is_image_url, normalize_url,
    get_file_size_str
)


class PlaywrightDownloader:
    """
    使用Playwright的图片下载器
    支持JavaScript动态加载的网站
    """
    
    def __init__(self, download_path="./downloads"):
        """
        初始化Playwright下载器
        
        Args:
            download_path (str): 默认下载路径
        """
        self.download_path = download_path
        self.browser = None
        self.page = None
        
        # 下载状态
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.download_sizes = []
        
        # 回调函数
        self.progress_callback = None
        self.status_callback = None
        
        # 浏览器配置
        self.headless = True  # 无头模式
        self.timeout = 30000  # 超时时间（毫秒）
        
    def set_callbacks(self, progress_callback=None, status_callback=None):
        """
        设置回调函数
        
        Args:
            progress_callback: 进度回调函数
            status_callback: 状态回调函数
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    async def init_browser(self):
        """
        初始化浏览器
        """
        try:
            if self.status_callback:
                self.status_callback("正在启动浏览器...")
            
            self.playwright = await async_playwright().start()
            
            # 启动浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            # 创建新页面
            self.page = await self.browser.new_page()
            
            # 设置视口大小
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 设置用户代理
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if self.status_callback:
                self.status_callback("浏览器启动成功")
                
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"浏览器启动失败: {str(e)}")
            raise
    
    async def optimize_for_redbubble(self):
        """
        Redbubble网站特殊优化
        """
        try:
            if self.status_callback:
                self.status_callback("检测到Redbubble网站，应用特殊优化...")
            
            # 等待页面完全加载
            await asyncio.sleep(5)
            
            # 等待产品图片容器加载
            try:
                await self.page.wait_for_selector('[data-testid="product-image"], .product-image, img[class*="styles__image"]', timeout=10000)
                if self.status_callback:
                    self.status_callback("Redbubble产品图片容器已加载")
            except:
                if self.status_callback:
                    self.status_callback("未找到Redbubble产品图片容器，继续正常流程")
            
            # 执行Redbubble特定的JavaScript优化
            await self.page.evaluate("""
                () => {
                    // 强制加载所有懒加载图片
                    const images = document.querySelectorAll('img[data-src], img[data-lazy-src], img[data-original]');
                    images.forEach(img => {
                        if (img.dataset.src) img.src = img.dataset.src;
                        if (img.dataset.lazySrc) img.src = img.dataset.lazySrc;
                        if (img.dataset.original) img.src = img.dataset.original;
                    });
                    
                    // 触发所有图片的load事件
                    const allImages = document.querySelectorAll('img');
                    allImages.forEach(img => {
                        if (img.complete) {
                            img.dispatchEvent(new Event('load'));
                        }
                    });
                    
                    // 滚动到所有图片位置触发懒加载
                    const imageContainers = document.querySelectorAll('[data-testid="product-image"], .product-image, [class*="styles__image"]');
                    imageContainers.forEach(container => {
                        container.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    });
                }
            """)
            
            # 等待图片加载
            await asyncio.sleep(3)
            
            if self.status_callback:
                self.status_callback("Redbubble优化完成")
                
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Redbubble优化出错: {str(e)}")
    
    async def close_browser(self):
        """
        关闭浏览器
        """
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"关闭浏览器时出错: {str(e)}")
    
    async def navigate_to_page(self, url):
        """
        导航到指定页面
        
        Args:
            url (str): 目标URL
        """
        if not validate_url(url):
            raise ValueError("无效的URL格式")
        
        try:
            if self.status_callback:
                self.status_callback(f"正在访问页面: {url}")
            
            # 导航到页面
            await self.page.goto(url, wait_until='networkidle', timeout=self.timeout)
            
            # 等待页面加载完成
            await self.page.wait_for_load_state('domcontentloaded')
            
            if self.status_callback:
                self.status_callback("页面加载完成")
                
        except Exception as e:
            raise Exception(f"页面访问失败: {str(e)}")
    
    async def scroll_and_load_content(self, scroll_count=5, scroll_delay=2):
        """
        滚动页面以加载更多内容
        
        Args:
            scroll_count (int): 滚动次数
            scroll_delay (int): 每次滚动后的等待时间（秒）
        """
        try:
            if self.status_callback:
                self.status_callback("正在滚动页面加载更多内容...")
            
            # 记录初始页面高度
            initial_height = await self.page.evaluate("document.body.scrollHeight")
            last_height = initial_height
            no_change_count = 0
            
            for i in range(scroll_count):
                # 滚动到页面底部
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # 等待内容加载
                await asyncio.sleep(scroll_delay)
                
                # 检查页面高度是否变化
                current_height = await self.page.evaluate("document.body.scrollHeight")
                if current_height == last_height:
                    no_change_count += 1
                    if no_change_count >= 2:  # 连续2次没有变化，可能已经到底
                        if self.status_callback:
                            self.status_callback("页面已滚动到底部，停止滚动")
                        break
                else:
                    no_change_count = 0
                    last_height = current_height
                
                # 尝试点击"加载更多"按钮（如果存在）
                try:
                    load_more_selectors = [
                        'button:has-text("Load More")',
                        'button:has-text("加载更多")',
                        'button:has-text("Show More")',
                        'button:has-text("显示更多")',
                        'button:has-text("Load more")',
                        'button:has-text("Show more")',
                        '[data-testid="load-more"]',
                        '[data-testid="show-more"]',
                        '.load-more',
                        '.show-more',
                        '.load-more-button',
                        '.show-more-button'
                    ]
                    
                    for selector in load_more_selectors:
                        try:
                            load_more_button = await self.page.wait_for_selector(selector, timeout=2000)
                            if load_more_button:
                                await load_more_button.click()
                                await asyncio.sleep(scroll_delay)
                                if self.status_callback:
                                    self.status_callback(f"点击了加载更多按钮")
                                break
                        except:
                            continue
                            
                except Exception:
                    pass
                
                # 尝试滚动到视口中的图片位置
                try:
                    await self.page.evaluate("""
                        () => {
                            const images = document.querySelectorAll('img');
                            images.forEach(img => {
                                const rect = img.getBoundingClientRect();
                                if (rect.top < window.innerHeight && rect.bottom > 0) {
                                    // 图片在视口中，触发懒加载
                                    img.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                }
                            });
                        }
                    """)
                    await asyncio.sleep(1)
                except Exception:
                    pass
                
                if self.status_callback:
                    self.status_callback(f"滚动进度: {i+1}/{scroll_count} (页面高度: {current_height}px)")
            
            # 最后再滚动一次，确保所有图片都加载
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            if self.status_callback:
                self.status_callback("页面滚动完成")
                
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"滚动页面时出错: {str(e)}")
    
    async def extract_images_from_page(self):
        """
        从页面中提取图片链接
        
        Returns:
            list: 图片URL列表
        """
        try:
            if self.status_callback:
                self.status_callback("正在提取图片链接...")
            
            # 等待图片加载
            await asyncio.sleep(3)
            
            # 执行JavaScript提取图片
            image_data = await self.page.evaluate("""
                () => {
                    const images = [];
                    const imgElements = document.querySelectorAll('img');
                    
                    imgElements.forEach(img => {
                        // 获取各种可能的图片源
                        const sources = [
                            img.src,
                            img.dataset.src,
                            img.dataset.lazySrc,
                            img.dataset.original,
                            img.dataset.lazySrc,
                            img.dataset.originalSrc,
                            img.getAttribute('data-original'),
                            img.getAttribute('data-src'),
                            img.getAttribute('data-lazy-src'),
                            img.getAttribute('data-original-src'),
                            img.getAttribute('data-full-src'),
                            img.getAttribute('data-high-res-src'),
                            img.getAttribute('data-zoom-src'),
                            img.getAttribute('data-large-src'),
                            img.getAttribute('data-medium-src'),
                            img.getAttribute('data-small-src')
                        ];
                        
                        sources.forEach(src => {
                            if (src && src.trim() && !src.startsWith('data:')) {
                                // 检查图片是否真正加载
                                const rect = img.getBoundingClientRect();
                                const isVisible = rect.width > 0 && rect.height > 0;
                                const hasNaturalSize = img.naturalWidth > 0 && img.naturalHeight > 0;
                                
                                // 过滤掉太小的图片（可能是图标）
                                const isLargeEnough = img.naturalWidth >= 100 && img.naturalHeight >= 100;
                                
                                if (isVisible && hasNaturalSize && isLargeEnough) {
                                    images.push({
                                        src: src.trim(),
                                        width: img.naturalWidth,
                                        height: img.naturalHeight,
                                        className: img.className,
                                        alt: img.alt || '',
                                        title: img.title || ''
                                    });
                                }
                            }
                        });
                    });
                    
                    // 去重并排序（按尺寸从大到小）
                    const uniqueImages = [];
                    const seen = new Set();
                    
                    images.forEach(img => {
                        if (!seen.has(img.src)) {
                            seen.add(img.src);
                            uniqueImages.push(img);
                        }
                    });
                    
                    // 按尺寸排序
                    uniqueImages.sort((a, b) => (b.width * b.height) - (a.width * a.height));
                    
                    return uniqueImages;
                }
            """)
            
            # 过滤有效的图片URL
            valid_images = []
            for img_data in image_data:
                url = img_data['src']
                if is_image_url(url):
                    # 转换为绝对URL
                    absolute_url = normalize_url(self.page.url, url)
                    valid_images.append(absolute_url)
            
            # 去重
            valid_images = list(set(valid_images))
            
            if self.status_callback:
                self.status_callback(f"找到 {len(valid_images)} 张图片")
                # 显示前几个图片URL用于调试
                if valid_images and len(valid_images) > 0:
                    self.status_callback(f"示例图片: {valid_images[0]}")
            
            return valid_images
            
        except Exception as e:
            raise Exception(f"提取图片失败: {str(e)}")
    
    async def download_image(self, image_url, save_path):
        """
        下载单张图片
        
        Args:
            image_url (str): 图片URL
            save_path (str): 保存路径
            
        Returns:
            bool: 下载成功返回True，失败返回False
        """
        try:
            # 使用Playwright下载图片
            response = await self.page.goto(image_url, wait_until='networkidle')
            
            if response.status != 200:
                return False
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                return False
            
            # 获取图片数据
            image_data = await response.body()
            
            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            # 验证图片
            try:
                with Image.open(save_path) as img:
                    img.verify()
                return True
            except:
                if os.path.exists(save_path):
                    os.remove(save_path)
                return False
                
        except Exception as e:
            if os.path.exists(save_path):
                os.remove(save_path)
            return False
    
    def generate_filename(self, image_url, index):
        """
        生成文件名
        
        Args:
            image_url (str): 图片URL
            index (int): 图片索引
            
        Returns:
            str: 生成的文件名
        """
        # 从URL中提取文件名
        parsed_url = image_url.split('/')[-1]
        if '?' in parsed_url:
            parsed_url = parsed_url.split('?')[0]
        
        # 清理文件名
        filename = clean_filename(parsed_url)
        
        # 如果没有有效文件名，使用索引
        if not filename or filename == 'image':
            filename = f"image_{index:03d}"
        
        # 获取文件扩展名
        extension = get_file_extension(image_url)
        
        # 确保文件名有扩展名
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg')):
            filename += extension
        
        return filename
    
    async def download_images_from_url(self, url, max_images=None, scroll_count=5):
        """
        从指定URL下载所有图片
        
        Args:
            url (str): 网页URL
            max_images (int): 最大下载图片数量
            scroll_count (int): 滚动次数
            
        Returns:
            dict: 下载结果统计
        """
        # 重置下载状态
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.download_sizes = []
        
        try:
            # 初始化浏览器
            await self.init_browser()
            
            # 导航到页面
            await self.navigate_to_page(url)
            
            # 检查是否为Redbubble网站，使用特殊优化
            if 'redbubble.com' in url.lower():
                await self.optimize_for_redbubble()
            
            # 滚动页面加载更多内容
            await self.scroll_and_load_content(scroll_count)
            
            # 提取图片链接
            image_urls = await self.extract_images_from_page()
            
            if not image_urls:
                if self.status_callback:
                    self.status_callback("未找到任何图片")
                return self.get_download_stats()
            
            # 限制下载数量
            if max_images:
                image_urls = image_urls[:max_images]
            
            self.total_images = len(image_urls)
            
            # 创建下载目录
            download_dir = create_download_directory(self.download_path, url)
            
            if self.status_callback:
                self.status_callback(f"开始下载 {self.total_images} 张图片到: {download_dir}")
            
            # 下载每张图片
            for index, image_url in enumerate(image_urls, 1):
                try:
                    # 生成文件名
                    filename = self.generate_filename(image_url, index)
                    save_path = os.path.join(download_dir, filename)
                    
                    # 如果文件已存在，添加序号
                    counter = 1
                    original_save_path = save_path
                    while os.path.exists(save_path):
                        name, ext = os.path.splitext(original_save_path)
                        save_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # 下载图片
                    if self.status_callback:
                        self.status_callback(f"正在下载 ({index}/{self.total_images}): {filename}")
                    
                    success = await self.download_image(image_url, save_path)
                    
                    if success:
                        self.downloaded_images += 1
                        # 记录文件大小
                        file_size = os.path.getsize(save_path)
                        self.download_sizes.append(file_size)
                        
                        if self.status_callback:
                            size_str = get_file_size_str(file_size)
                            self.status_callback(f"✓ 下载成功: {filename} ({size_str})")
                    else:
                        self.failed_images += 1
                        if self.status_callback:
                            self.status_callback(f"✗ 下载失败: {filename}")
                    
                    # 更新进度
                    if self.progress_callback:
                        progress = (index / self.total_images) * 100
                        self.progress_callback(progress)
                    
                    # 添加延迟，避免请求过于频繁
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.failed_images += 1
                    if self.status_callback:
                        self.status_callback(f"✗ 下载出错: {str(e)}")
            
            # 下载完成
            if self.status_callback:
                total_size = sum(self.download_sizes)
                total_size_str = get_file_size_str(total_size)
                self.status_callback(f"下载完成! 成功: {self.downloaded_images}, 失败: {self.failed_images}, 总大小: {total_size_str}")
            
            return self.get_download_stats()
            
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"下载过程出错: {str(e)}")
            raise
        finally:
            # 关闭浏览器
            await self.close_browser()
    
    def get_download_stats(self):
        """
        获取下载统计信息
        
        Returns:
            dict: 下载统计信息
        """
        total_size = sum(self.download_sizes)
        return {
            'total_images': self.total_images,
            'downloaded_images': self.downloaded_images,
            'failed_images': self.failed_images,
            'total_size': total_size,
            'total_size_str': get_file_size_str(total_size),
            'success_rate': (self.downloaded_images / self.total_images * 100) if self.total_images > 0 else 0
        }


# 同步包装器，用于在GUI中使用
class PlaywrightDownloaderSync:
    """
    Playwright下载器的同步包装器
    """
    
    def __init__(self, download_path="./downloads"):
        self.downloader = PlaywrightDownloader(download_path)
    
    def set_callbacks(self, progress_callback=None, status_callback=None):
        self.downloader.set_callbacks(progress_callback, status_callback)
    
    def download_images_from_url(self, url, max_images=None, scroll_count=5):
        """
        同步下载方法
        
        Args:
            url (str): 网页URL
            max_images (int): 最大下载图片数量
            scroll_count (int): 滚动次数
            
        Returns:
            dict: 下载结果统计
        """
        # 在新的事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.downloader.download_images_from_url(url, max_images, scroll_count)
            )
        finally:
            loop.close() 