"""
图片下载核心逻辑模块
包含网页解析、图片提取和下载功能
"""

import os
import requests
import threading
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PIL import Image
import io
from utils import (
    validate_url, clean_filename, get_file_extension, 
    create_download_directory, is_image_url, normalize_url,
    get_file_size_str
)


class ImageDownloader:
    """
    图片下载器类
    负责从网页中提取图片链接并下载到本地
    """
    
    def __init__(self, download_path="./downloads"):
        """
        初始化下载器
        
        Args:
            download_path (str): 默认下载路径
        """
        self.download_path = download_path
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 下载状态
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.download_sizes = []
        
        # 回调函数
        self.progress_callback = None
        self.status_callback = None
        
    def set_callbacks(self, progress_callback=None, status_callback=None):
        """
        设置回调函数
        
        Args:
            progress_callback: 进度回调函数
            status_callback: 状态回调函数
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def extract_images_from_url(self, url):
        """
        从指定URL提取图片链接
        
        Args:
            url (str): 网页URL
            
        Returns:
            list: 图片URL列表
        """
        if not validate_url(url):
            raise ValueError("无效的URL格式")
        
        try:
            # 发送HTTP请求获取网页内容
            if self.status_callback:
                self.status_callback(f"正在获取网页内容: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            
            # 解析HTML内容
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取所有图片标签
            img_tags = soup.find_all('img')
            
            # 收集图片URL
            image_urls = []
            for img in img_tags:
                # 获取图片的src属性
                src = img.get('src')
                if src:
                    # 将相对URL转换为绝对URL
                    absolute_url = normalize_url(url, src)
                    if is_image_url(absolute_url):
                        image_urls.append(absolute_url)
                
                # 检查data-src属性（懒加载图片）
                data_src = img.get('data-src')
                if data_src:
                    absolute_url = normalize_url(url, data_src)
                    if is_image_url(absolute_url):
                        image_urls.append(absolute_url)
            
            # 去重
            image_urls = list(set(image_urls))
            
            if self.status_callback:
                self.status_callback(f"找到 {len(image_urls)} 张图片")
            
            return image_urls
            
        except requests.RequestException as e:
            raise Exception(f"获取网页失败: {str(e)}")
        except Exception as e:
            raise Exception(f"解析网页失败: {str(e)}")
    
    def download_image(self, image_url, save_path):
        """
        下载单张图片
        
        Args:
            image_url (str): 图片URL
            save_path (str): 保存路径
            
        Returns:
            bool: 下载成功返回True，失败返回False
        """
        try:
            # 发送请求下载图片
            response = self.session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 获取文件大小
            file_size = int(response.headers.get('content-length', 0))
            
            # 检查内容类型是否为图片
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                return False
            
            # 保存图片文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证下载的文件是否为有效图片
            try:
                with Image.open(save_path) as img:
                    img.verify()
                return True
            except:
                # 如果不是有效图片，删除文件
                if os.path.exists(save_path):
                    os.remove(save_path)
                return False
                
        except Exception as e:
            # 下载失败，删除可能存在的文件
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
    
    def download_images_from_url(self, url, max_images=None):
        """
        从指定URL下载所有图片
        
        Args:
            url (str): 网页URL
            max_images (int): 最大下载图片数量，None表示下载所有图片
            
        Returns:
            dict: 下载结果统计
        """
        # 重置下载状态
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.download_sizes = []
        
        try:
            # 提取图片URL
            image_urls = self.extract_images_from_url(url)
            
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
                    
                    success = self.download_image(image_url, save_path)
                    
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
                    
                    # 添加小延迟，避免请求过于频繁
                    time.sleep(0.1)
                    
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