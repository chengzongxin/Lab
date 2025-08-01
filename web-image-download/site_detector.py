"""
网站检测工具
用于识别需要JavaScript渲染的网站
"""

import re
from urllib.parse import urlparse


class SiteDetector:
    """
    网站检测器
    用于识别不同类型的网站和推荐合适的下载方式
    """
    
    # 需要JavaScript渲染的网站模式
    JS_SITES = [
        # 电商网站
        r'redbubble\.com',
        r'etsy\.com',
        r'amazon\.com',
        r'ebay\.com',
        r'pinterest\.com',
        r'instagram\.com',
        r'facebook\.com',
        r'twitter\.com',
        r'linkedin\.com',
        r'youtube\.com',
        r'tiktok\.com',
        r'snapchat\.com',
        
        # 社交媒体
        r'reddit\.com',
        r'discord\.com',
        r'telegram\.org',
        r'whatsapp\.com',
        
        # 现代Web应用
        r'notion\.so',
        r'figma\.com',
        r'slack\.com',
        r'trello\.com',
        r'asana\.com',
        r'airtable\.com',
        
        # 新闻和内容网站
        r'medium\.com',
        r'substack\.com',
        r'dev\.to',
        r'hashnode\.dev',
        
        # 设计网站
        r'dribbble\.com',
        r'behance\.net',
        r'artstation\.com',
        r'deviantart\.com',
        
        # 其他现代网站
        r'github\.com',
        r'gitlab\.com',
        r'bitbucket\.org',
        r'stackoverflow\.com',
        r'quora\.com',
        r'producthunt\.com',
        r'kickstarter\.com',
        r'indiegogo\.com',
    ]
    
    # 简单静态网站模式（可以使用requests）
    SIMPLE_SITES = [
        r'wikipedia\.org',
        r'stackoverflow\.com',
        r'python\.org',
        r'github\.com',
        r'gitlab\.com',
        r'bitbucket\.org',
        r'readthedocs\.io',
        r'pypi\.org',
        r'npmjs\.com',
        r'wordpress\.com',
        r'blogspot\.com',
        r'tumblr\.com',
    ]
    
    @classmethod
    def detect_site_type(cls, url):
        """
        检测网站类型
        
        Args:
            url (str): 网站URL
            
        Returns:
            dict: 检测结果
        """
        domain = urlparse(url).netloc.lower()
        
        # 检查是否为需要JavaScript的网站
        for pattern in cls.JS_SITES:
            if re.search(pattern, domain):
                return {
                    'type': 'javascript',
                    'recommended_method': 'playwright',
                    'reason': f'检测到现代网站模式: {pattern}',
                    'features': [
                        'JavaScript动态加载',
                        '懒加载图片',
                        '无限滚动',
                        'SPA应用'
                    ]
                }
        
        # 检查是否为简单静态网站
        for pattern in cls.SIMPLE_SITES:
            if re.search(pattern, domain):
                return {
                    'type': 'static',
                    'recommended_method': 'requests',
                    'reason': f'检测到静态网站模式: {pattern}',
                    'features': [
                        '静态HTML',
                        '传统图片加载',
                        'SEO友好'
                    ]
                }
        
        # 默认推荐使用Playwright（更安全）
        return {
            'type': 'unknown',
            'recommended_method': 'playwright',
            'reason': '未知网站类型，推荐使用高级模式确保兼容性',
            'features': [
                'JavaScript支持',
                '动态内容处理',
                '更好的兼容性'
            ]
        }
    
    @classmethod
    def get_download_recommendation(cls, url):
        """
        获取下载方式推荐
        
        Args:
            url (str): 网站URL
            
        Returns:
            dict: 推荐信息
        """
        detection = cls.detect_site_type(url)
        
        if detection['recommended_method'] == 'playwright':
            return {
                'method': 'playwright',
                'priority': 'high',
                'message': f"推荐使用高级模式 (Playwright)\n原因: {detection['reason']}",
                'features': detection['features'],
                'scroll_count': 8,  # 需要更多滚动
                'timeout': 45  # 更长超时时间
            }
        else:
            return {
                'method': 'requests',
                'priority': 'low',
                'message': f"可以使用简单模式 (Requests)\n原因: {detection['reason']}",
                'features': detection['features'],
                'scroll_count': 3,
                'timeout': 30
            }
    
    @classmethod
    def is_modern_site(cls, url):
        """
        判断是否为现代网站（需要JavaScript）
        
        Args:
            url (str): 网站URL
            
        Returns:
            bool: 是否为现代网站
        """
        detection = cls.detect_site_type(url)
        return detection['type'] == 'javascript'
    
    @classmethod
    def get_site_specific_settings(cls, url):
        """
        获取网站特定的下载设置
        
        Args:
            url (str): 网站URL
            
        Returns:
            dict: 网站特定设置
        """
        domain = urlparse(url).netloc.lower()
        
        # Redbubble特定设置
        if 'redbubble.com' in domain:
            return {
                'scroll_count': 15,
                'scroll_delay': 4,
                'wait_for_images': True,
                'custom_selectors': [
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    '.product-image img',
                    '.artwork-image img',
                    'img[class*="styles__image"]',
                    'img[class*="styles__fluid"]',
                    'img[class*="styles__rounded"]',
                    '[data-testid="product-image"] img',
                    '.product-image-container img',
                    '.artwork-image-container img'
                ],
                'special_optimization': True
            }
        
        # Pinterest特定设置
        elif 'pinterest.com' in domain:
            return {
                'scroll_count': 15,
                'scroll_delay': 2,
                'wait_for_images': True,
                'custom_selectors': [
                    'img[data-testid="pin-image"]',
                    '.pin-image img',
                    '[data-testid="pin"] img'
                ]
            }
        
        # Instagram特定设置
        elif 'instagram.com' in domain:
            return {
                'scroll_count': 12,
                'scroll_delay': 2,
                'wait_for_images': True,
                'custom_selectors': [
                    'img[data-testid="post-image"]',
                    '.post-image img',
                    '[data-testid="post"] img'
                ]
            }
        
        # 默认设置
        else:
            return {
                'scroll_count': 5,
                'scroll_delay': 2,
                'wait_for_images': False,
                'custom_selectors': []
            } 