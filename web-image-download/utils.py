"""
工具函数模块
包含URL验证、文件名处理、路径创建等通用功能
"""

import os
import re
import urllib.parse
from urllib.parse import urljoin, urlparse
from pathlib import Path


def validate_url(url):
    """
    验证URL格式是否正确
    
    Args:
        url (str): 要验证的URL
        
    Returns:
        bool: URL格式正确返回True，否则返回False
    """
    try:
        # 解析URL
        result = urlparse(url)
        # 检查是否有协议和网络位置
        return all([result.scheme, result.netloc])
    except:
        return False


def clean_filename(filename):
    """
    清理文件名，移除非法字符
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 移除或替换Windows和Unix系统中的非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '_', filename)
    
    # 移除多余的空格和点
    cleaned = cleaned.strip('. ')
    
    # 如果文件名为空，使用默认名称
    if not cleaned:
        cleaned = 'image'
    
    return cleaned


def get_file_extension(url):
    """
    从URL中提取文件扩展名
    
    Args:
        url (str): 图片URL
        
    Returns:
        str: 文件扩展名（包含点号）
    """
    # 从URL路径中提取扩展名
    parsed = urlparse(url)
    path = parsed.path
    
    # 查找常见的图片扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    
    for ext in image_extensions:
        if path.lower().endswith(ext):
            return ext
    
    # 如果没有找到扩展名，返回默认的.jpg
    return '.jpg'


def create_download_directory(base_path, url):
    """
    为下载创建目录结构
    
    Args:
        base_path (str): 基础下载路径
        url (str): 网站URL
        
    Returns:
        str: 创建的目录路径
    """
    # 从URL中提取域名作为文件夹名
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # 清理域名，移除端口号等
    domain = domain.split(':')[0]
    
    # 创建目录路径
    download_dir = os.path.join(base_path, domain)
    
    # 确保目录存在
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    
    return download_dir


def is_image_url(url):
    """
    判断URL是否为图片链接
    
    Args:
        url (str): 要检查的URL
        
    Returns:
        bool: 是图片链接返回True，否则返回False
    """
    # 图片文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico']
    
    # 检查URL是否包含图片扩展名
    url_lower = url.lower()
    for ext in image_extensions:
        if ext in url_lower:
            return True
    
    # 检查常见的图片URL模式
    image_patterns = [
        r'\.(jpg|jpeg|png|gif|bmp|webp|svg|ico)',
        r'/image/',
        r'/img/',
        r'/photo/',
        r'/picture/'
    ]
    
    for pattern in image_patterns:
        if re.search(pattern, url_lower):
            return True
    
    return False


def normalize_url(base_url, img_url):
    """
    将相对URL转换为绝对URL
    
    Args:
        base_url (str): 基础URL（网页URL）
        img_url (str): 图片URL（可能是相对路径）
        
    Returns:
        str: 完整的绝对URL
    """
    # 如果已经是绝对URL，直接返回
    if img_url.startswith(('http://', 'https://')):
        return img_url
    
    # 将相对URL转换为绝对URL
    return urljoin(base_url, img_url)


def get_file_size_str(size_bytes):
    """
    将字节数转换为人类可读的文件大小字符串
    
    Args:
        size_bytes (int): 文件大小（字节）
        
    Returns:
        str: 格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}" 