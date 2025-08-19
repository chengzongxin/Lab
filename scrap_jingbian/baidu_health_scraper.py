#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度健康爬虫程序
功能：读取Excel文件中的文章标题，搜索百度健康相关内容，爬取医生信息
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 设置第三方库的日志级别，减少噪音
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('webdriver_manager').setLevel(logging.WARNING)

class BaiduHealthScraper:
    """百度健康爬虫类"""
    
    def __init__(self, use_proxy=False, proxy_list=None, use_existing_browser=False, debugger_address=None):
        """初始化爬虫"""
        self.driver = None
        self.results = []
        self.current_search_title = ""
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.excel_file = None  # 保存Excel文件路径
        self.use_existing_browser = use_existing_browser
        self.debugger_address = debugger_address or "localhost:9222"
        self.setup_driver()
        
    def setup_driver(self, max_retries=3):
        """设置Chrome浏览器驱动"""
        for attempt in range(max_retries):
            try:
                service = Service(ChromeDriverManager().install())
                options = webdriver.ChromeOptions()
                
                # 基础配置
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                # 禁用GCM服务和相关错误
                options.add_argument('--disable-gcm')
                options.add_argument('--disable-background-networking')
                options.add_argument('--disable-default-apps')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-sync')
                options.add_argument('--disable-translate')
                options.add_argument('--metrics-recording-only')
                options.add_argument('--no-first-run')
                options.add_argument('--safebrowsing-disable-auto-update')
                
                # 反爬虫配置
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # 设置用户代理
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
                ]
                options.add_argument(f'--user-agent={random.choice(user_agents)}')
                
                # 设置窗口大小
                options.add_argument('--window-size=1920,1080')
                
                # 设置代理（如果启用）
                if self.use_proxy and self.proxy_list:
                    proxy = random.choice(self.proxy_list)
                    options.add_argument(f'--proxy-server={proxy}')
                    logging.info(f"使用代理: {proxy}")
                
                self.driver = webdriver.Chrome(service=service, options=options)
                
                # 执行反检测脚本
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                logging.info("Chrome浏览器驱动设置成功")
                return  # 成功则退出循环
                
            except Exception as e:
                logging.warning(f"第{attempt + 1}次设置Chrome驱动失败: {e}")
                if attempt < max_retries - 1:
                    logging.info("等待3秒后重试...")
                    time.sleep(3)
                    # 清理可能的残留进程
                    try:
                        if hasattr(self, 'driver') and self.driver:
                            self.driver.quit()
                    except:
                        pass
                else:
                    logging.error(f"设置Chrome驱动失败，已重试{max_retries}次")
                    raise
    
    def read_excel_titles(self, excel_file):
        """读取Excel文件第二列的文章标题"""
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_file)
            
            # 检查列数
            if len(df.columns) < 2:
                logging.error(f"Excel文件列数不足，当前只有{len(df.columns)}列")
                return []
            
            # 获取第二列（索引为1）
            titles = df.iloc[:, 1].dropna().tolist()
            
            logging.info(f"成功读取{len(titles)}个文章标题")
            return titles
            
        except Exception as e:
            logging.error(f"读取Excel文件失败: {e}")
            return []
    
    def check_driver_health(self):
        """检查浏览器驱动是否健康"""
        try:
            if not self.driver:
                return False
            
            # 尝试执行一个简单的JavaScript命令来测试连接
            self.driver.execute_script("return navigator.userAgent;")
            return True
            
        except Exception as e:
            logging.warning(f"浏览器驱动健康检查失败: {e}")
            return False
    
    def reconnect_driver(self):
        """重新连接浏览器驱动"""
        try:
            logging.info("尝试重新连接浏览器驱动...")
            
            # 关闭旧的驱动
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            # 重新设置驱动
            self.setup_driver()
            
            if self.driver:
                logging.info("浏览器驱动重新连接成功")
                return True
            else:
                logging.error("浏览器驱动重新连接失败")
                return False
                
        except Exception as e:
            logging.error(f"重新连接浏览器驱动时出错: {e}")
            return False
    
    def safe_driver_operation(self, operation, *args, **kwargs):
        """安全的浏览器操作，包含自动重连机制"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 检查驱动健康状态
                if not self.check_driver_health():
                    logging.warning(f"浏览器驱动不健康，尝试重连 (第{attempt + 1}次)")
                    if not self.reconnect_driver():
                        if attempt == max_retries - 1:
                            raise Exception("无法重新连接浏览器驱动")
                        continue
                
                # 执行操作
                return operation(*args, **kwargs)
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # 检查是否是连接相关错误
                if any(keyword in error_msg for keyword in [
                    'invalid session id', 'session id', 'connection reset', 
                    'remote host', 'chrome not reachable', 'chrome failed'
                ]):
                    logging.warning(f"检测到连接错误，尝试重连 (第{attempt + 1}次): {e}")
                    
                    if attempt < max_retries - 1:
                        if not self.reconnect_driver():
                            time.sleep(2)  # 等待一下再重试
                            continue
                    else:
                        raise Exception(f"重连失败，已重试{max_retries}次: {e}")
                else:
                    # 非连接错误，直接抛出
                    raise e
        
        raise Exception(f"操作失败，已重试{max_retries}次")
    
    def search_baidu(self, title):
        """在百度搜索文章标题"""
        try:
            # 构建搜索URL
            search_url = f"https://www.baidu.com/s?wd={title}"
            
            # 使用安全操作包装器
            def _search():
                self.driver.get(search_url)
                logging.info(f"正在搜索: {title}")
                
                # 智能等待页面加载
                self.smart_wait(1, 2)
                
                # 模拟真实用户行为
                self.simulate_human_behavior()
                return True
            
            return self.safe_driver_operation(_search)
            
        except Exception as e:
            logging.error(f"百度搜索失败: {e}")
            return False
    
    def smart_wait(self, min_seconds=2, max_seconds=5):
        """智能等待，随机延迟"""
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)
        logging.debug(f"智能等待 {wait_time:.2f} 秒")
    
    def simulate_human_behavior(self):
        """模拟真实用户行为"""
        try:
            # 随机滚动页面
            scroll_times = random.randint(0, 1)
            for _ in range(scroll_times):
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # 随机移动鼠标
            actions = ActionChains(self.driver)
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y).perform()
            
            logging.debug("模拟用户行为完成")
        except Exception as e:
            logging.debug(f"模拟用户行为时出错: {e}")
    
    def check_verification_required(self):
        """检查是否需要验证"""
        try:
            # 检查常见的验证页面元素
            verification_indicators = [
                "安全验证",
            ]
            
            page_text = self.driver.page_source.lower()
            for indicator in verification_indicators:
                if indicator in page_text:
                    logging.warning(f"检测到验证要求: {indicator}")
                    return True
            
            return False
        except Exception as e:
            logging.debug(f"检查验证要求时出错: {e}")
            return False
    
    def handle_verification(self):
        """处理验证要求"""
        try:
            logging.info("检测到验证要求，等待用户手动处理...")
            
            # 等待用户手动处理验证
            input("请手动完成验证后，按回车键继续...")
            
            # 验证完成后等待页面加载
            time.sleep(3)
            
            logging.info("验证处理完成，继续执行...")
            return True
            
        except Exception as e:
            logging.error(f"处理验证时出错: {e}")
            return False
    
    def find_baidu_health_result(self, max_pages=3):
        """查找带有"百度健康"标志的搜索结果"""
        try:
            for page in range(1, max_pages + 1):
                logging.info(f"正在搜索第{page}页")
                
                # 使用安全操作包装器
                def _search_page():
                    # 等待页面加载
                    self.smart_wait(1, 2)
                    
                    # 检查是否需要验证
                    if self.check_verification_required():
                        if not self.handle_verification():
                            logging.error("验证处理失败，跳过当前页面")
                            return False
                    
                    # 查找搜索结果 - 使用新的选择器
                    results = self.driver.find_elements(By.CSS_SELECTOR, "div.result, div[class*='result']")
                    
                    logging.info(f"找到{len(results)}个搜索结果")
                    
                    for result in results:
                        try:
                            # 查找百度健康标识
                            health_indicators = result.find_elements(By.CSS_SELECTOR, "span.cosc-source-text")
                            
                            for indicator in health_indicators:
                                if "百度健康" in indicator.text:
                                    logging.info(f"找到百度健康标识: {indicator.text}")
                                    
                                    # 查找标题链接
                                    title_element = result.find_element(By.CSS_SELECTOR, "h3 a, a[target='_blank']")
                                    title_text = title_element.text
                                    
                                    logging.info(f"找到百度健康结果: {title_text}")
                                    
                                    # 点击进入详情页进行进一步验证
                                    logging.info(f"点击进入详情页: {title_text}")
                                    title_element.click()
                                    
                                    # 等待新页面加载
                                    time.sleep(3)
                                    
                                    # 切换到新窗口
                                    self.driver.switch_to.window(self.driver.window_handles[-1])
                                    
                                    # 验证是否为真正的百度健康页面
                                    if self.verify_baidu_health_page():
                                        logging.info("确认是百度健康页面，开始提取信息")
                                        
                                        # 提取详细信息
                                        info = self.extract_health_info()
                                        info['search_title'] = self.current_search_title
                                        
                                        # 添加到结果列表
                                        self.results.append(info)
                                        logging.info(f"成功提取信息: {info}")
                                        
                                        # 实时保存到Excel文件
                                        self.append_to_excel(info)
                                        logging.info(f"数据已实时保存到Excel文件")
                                        
                                        # 关闭当前标签页，回到搜索页
                                        self.driver.close()
                                        self.driver.switch_to.window(self.driver.window_handles[0])
                                        
                                        return True
                                    else:
                                        logging.warning("不是真正的百度健康页面，关闭标签页")
                                        self.driver.close()
                                        self.driver.switch_to.window(self.driver.window_handles[0])
                                        continue
                        
                        except Exception as e:
                            logging.debug(f"处理搜索结果时出错: {e}")
                            continue
                    
                    # 如果当前页没找到，尝试翻到下一页
                    if page < max_pages:
                        try:
                            # 尝试多种翻页按钮选择器
                            next_selectors = [
                                "a.n", 
                                "a[class*='next']", 
                                "a[aria-label*='下一页']"
                            ]
                            
                            next_found = False
                            for selector in next_selectors:
                                try:
                                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    if "下一页" in next_button.text or "next" in next_button.text.lower():
                                        next_button.click()
                                        time.sleep(2)
                                        next_found = True
                                        break
                                except:
                                    continue
                            
                            if not next_found:
                                logging.info("未找到下一页按钮，停止翻页")
                        except Exception as e:
                            logging.warning(f"翻页失败: {e}")
                    
                    return False  # 当前页没找到结果
                
                # 执行安全搜索
                result = self.safe_driver_operation(_search_page)
                if result:  # 找到了结果
                    return True
                
                # 如果当前页没找到，继续下一页
                if page < max_pages:
                    logging.info(f"第{page}页未找到结果，继续下一页")
            
            logging.warning("在指定页数内未找到百度健康结果")
            return False
            
        except Exception as e:
            logging.error(f"查找百度健康结果失败: {e}")
            return False
    
    def verify_baidu_health_page(self):
        """验证是否为真正的百度健康页面"""
        try:
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查URL是否为百度健康域名
            current_url = self.driver.current_url
            if "health.baidu.com" not in current_url:
                logging.info(f"URL不是百度健康域名: {current_url}")
                return False
            
            # 查找"百度健康内容审核团队优选"标识
            try:
                # 首先尝试使用具体的CSS选择器
                preferred_selectors = [
                    "span.index_preferredSwapperText__VL_Jr",
                    "[class*='preferredSwapperText']"
                ]
                
                for selector in preferred_selectors:
                    try:
                        preferred_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if "百度健康内容审核团队优选" in preferred_element.text:
                            logging.info("找到百度健康内容审核团队优选标识")
                            return True
                    except:
                        continue
                
                # 如果没有找到，尝试在整个页面中搜索文本
                page_text = self.driver.page_source
                if "百度健康内容审核团队优选" in page_text:
                    logging.info("在页面源码中找到百度健康内容审核团队优选标识")
                    return True
                
                # 如果没有找到特定标识，检查页面标题或其他特征
                page_title = self.driver.title
                if "百度健康" in page_title or "健康" in page_title:
                    logging.info(f"通过页面标题确认: {page_title}")
                    return True
                
                logging.warning("未找到百度健康页面特征标识")
                return False
                
            except Exception as e:
                logging.warning(f"验证页面标识时出错: {e}")
                return False
                
        except Exception as e:
            logging.error(f"验证百度健康页面失败: {e}")
            return False
    
    def extract_health_info(self):
        """提取健康页面的信息"""
        try:
            info = {
                'title': '',
                'doctor': '',
                'position': '',
                'department': '',
                'content': ''
            }
            
            # 使用安全操作包装器
            def _extract():
                # 等待页面加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 提取标题
                try:
                    title_selectors = [
                        "h1", ".title", ".article-title", ".page-title",
                        "[class*='title']", "h2", "h3"
                    ]
                    for selector in title_selectors:
                        try:
                            title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if title_element.text.strip():
                                info['title'] = title_element.text.strip()
                                break
                        except:
                            continue
                except:
                    info['title'] = "未找到标题"
            
                # 从详情页提取医生信息
                try:
                    # 根据百度健康页面的标准HTML结构提取医生信息
                    # 医生姓名
                    try:
                        doctor_name_element = self.driver.find_element(By.CSS_SELECTOR, "span.index_name__0Yl8k")
                        info['doctor'] = doctor_name_element.text.strip()
                        logging.info(f"找到医生姓名: {info['doctor']}")
                    except:
                        logging.debug("未找到医生姓名元素")
                    
                    # 医生职位
                    try:
                        position_element = self.driver.find_element(By.CSS_SELECTOR, "span.index_title__wNRZD")
                        info['position'] = position_element.text.strip()
                        logging.info(f"找到医生职位: {info['position']}")
                    except:
                        logging.debug("未找到医生职位元素")
                    
                    # 科室信息
                    try:
                        dept_element = self.driver.find_element(By.CSS_SELECTOR, "span.index_department__y9DFE")
                        info['department'] = dept_element.text.strip()
                        logging.info(f"找到科室信息: {info['department']}")
                    except:
                        logging.debug("未找到科室信息元素")
                    
                    # 如果没有找到标准结构，尝试备用选择器
                    if not info['doctor'] or not info['position'] or not info['department']:
                        logging.info("使用备用选择器提取医生信息")
                        
                        # 备用医生信息选择器
                        backup_selectors = [
                            ".doctor-name", ".doctor-info .name", ".expert-name",
                            ".author", ".doctor", ".expert", "[class*='doctor']",
                            "[class*='author']", "[class*='expert']"
                        ]
                        
                        for selector in backup_selectors:
                            try:
                                doctor_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if doctor_element.text.strip():
                                    doctor_text = doctor_element.text.strip()
                                    logging.info(f"备用选择器找到医生信息: {doctor_text}")
                                    
                                    # 解析医生信息（格式：王俊生 主任医师 泌尿外科）
                                    import re
                                    # 匹配医生姓名和职位
                                    doctor_match = re.search(r'([^\s]+)\s+([^\s]+医师)', doctor_text)
                                    if doctor_match and not info['doctor']:
                                        info['doctor'] = doctor_match.group(1)
                                    if doctor_match and not info['position']:
                                        info['position'] = doctor_match.group(2)
                                    
                                    # 匹配科室信息
                                    dept_match = re.search(r'([^\s]+科)', doctor_text)
                                    if dept_match and not info['department']:
                                        info['department'] = dept_match.group(1)
                                    
                                    break
                            except:
                                continue
                        
                        # 如果还是没有找到，尝试从页面源码中搜索
                        if not info['doctor'] or not info['position'] or not info['department']:
                            logging.info("从页面源码中搜索医生信息")
                            page_text = self.driver.page_source
                            
                            # 搜索医生姓名和职位
                            if not info['doctor'] or not info['position']:
                                doctor_patterns = [
                                    r'([^\s]+)\s+主任医师',
                                    r'([^\s]+)\s+副主任医师',
                                    r'([^\s]+)\s+主治医师'
                                ]
                                
                                for pattern in doctor_patterns:
                                    match = re.search(pattern, page_text)
                                    if match:
                                        if not info['doctor']:
                                            info['doctor'] = match.group(1)
                                        if not info['position']:
                                            info['position'] = match.group(1) + "医师"
                                        break
                            
                            # 搜索科室信息
                            if not info['department']:
                                dept_patterns = [
                                    r'([^\s]+科)',
                                    r'([^\s]+外科)',
                                    r'([^\s]+内科)'
                                ]
                                
                                for pattern in dept_patterns:
                                    match = re.search(pattern, page_text)
                                    if match:
                                        info['department'] = match.group(1)
                                        break
                    
                except Exception as e:
                    logging.debug(f"提取医生信息时出错: {e}")
                
                # 设置默认值
                if not info['doctor']:
                    info['doctor'] = "未找到医生信息"
                
                if not info['position']:
                    info['position'] = "未找到职位信息"
                
                if not info['department']:
                    info['department'] = "未找到科室信息"
                
                # 提取文章内容
                try:
                    content = self.extract_article_content()
                    info['content'] = content
                    logging.info(f"成功提取文章内容，长度: {len(content)} 字符")
                except Exception as e:
                    logging.warning(f"提取文章内容失败: {e}")
                    info['content'] = "未找到文章内容"
                
                logging.info(f"成功提取信息: {info}")
                return info
            
            # 执行安全提取
            return self.safe_driver_operation(_extract)
            
        except Exception as e:
            logging.error(f"提取健康信息失败: {e}")
            return {
                'title': '提取失败',
                'doctor': '提取失败',
                'position': '提取失败',
                'department': '提取失败',
                'content': '提取失败'
            }
    
    def extract_article_content(self):
        """提取文章内容"""
        try:
            # 使用安全操作包装器
            def _extract_content():
                # 等待页面加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                content_text = ""
                
                # 方法1: 直接提取所有p标签内容
                try:
                    logging.info("尝试提取所有p标签内容...")
                    p_elements = self.driver.find_elements(By.TAG_NAME, "p")
                    
                    if p_elements:
                        # 收集所有p标签的文本
                        p_texts = []
                        for p in p_elements:
                            text = p.text.strip()
                            if text and len(text) > 5:  # 过滤掉太短的文本
                                p_texts.append(text)
                        
                        if p_texts:
                            content_text = '\n\n'.join(p_texts)
                            logging.info(f"成功提取{len(p_texts)}个段落，总长度: {len(content_text)} 字符")
                            return self.clean_content(content_text)
                except Exception as e:
                    logging.debug(f"提取p标签内容失败: {e}")
                
                # 方法2: 使用CSS选择器定位内容区域
                if not content_text:
                    try:
                        logging.info("尝试使用CSS选择器提取内容...")
                        content_selectors = [
                            "div[data-anchor-id='content']",
                            "div.index_articleWrap__nPJne",
                            "div.index_textContent__U8ot6",
                            "div.index_richText__vkNnU",
                            "div.index_richTextPc__3FDg9"
                        ]
                        
                        for selector in content_selectors:
                            try:
                                content_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if content_element:
                                    # 获取所有文本内容
                                    content_text = content_element.text.strip()
                                    if content_text and len(content_text) > 50:  # 确保内容足够长
                                        logging.info(f"使用选择器 '{selector}' 成功提取内容")
                                        break
                            except:
                                continue
                    except Exception as e:
                        logging.debug(f"CSS选择器提取失败: {e}")
                
                # 方法3: 从页面源码中搜索并提取p标签内容
                if not content_text:
                    try:
                        logging.info("从页面源码中搜索p标签内容...")
                        page_source = self.driver.page_source
                        
                        # 使用正则表达式提取所有p标签内容
                        import re
                        p_pattern = r'<p[^>]*>(.*?)</p>'
                        p_matches = re.findall(p_pattern, page_source, re.DOTALL | re.IGNORECASE)
                        
                        if p_matches:
                            # 清理HTML标签，只保留文本
                            from bs4 import BeautifulSoup
                            p_texts = []
                            for p_html in p_matches:
                                # 清理HTML标签
                                soup = BeautifulSoup(p_html, 'html.parser')
                                text = soup.get_text(strip=True)
                                if text and len(text) > 5:  # 过滤掉太短的文本
                                    p_texts.append(text)
                            
                            if p_texts:
                                content_text = '\n\n'.join(p_texts)
                                logging.info(f"从页面源码成功提取{len(p_texts)}个段落")
                    except Exception as e:
                        logging.debug(f"页面源码提取失败: {e}")
                
                # 方法4: 尝试提取特定内容区域的所有文本
                if not content_text:
                    try:
                        logging.info("尝试提取特定内容区域...")
                        # 查找包含"content"的div
                        content_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[data-anchor-id='content'], div[class*='articleWrap'], div[class*='textContent']")
                        
                        for div in content_divs:
                            try:
                                text = div.text.strip()
                                if text and len(text) > 100:  # 确保内容足够长
                                    content_text = text
                                    logging.info("成功提取特定内容区域")
                                    break
                            except:
                                continue
                    except Exception as e:
                        logging.debug(f"特定内容区域提取失败: {e}")
                
                # 清理和格式化内容
                if content_text:
                    return self.clean_content(content_text)
                else:
                    logging.warning("未找到文章内容")
                    return "未找到文章内容"
            
            # 执行安全提取
            return self.safe_driver_operation(_extract_content)
                
        except Exception as e:
            logging.error(f"提取文章内容失败: {e}")
            return "提取文章内容失败"
    
    def clean_content(self, content_text):
        """清理和格式化内容"""
        try:
            import re
            
            # 移除多余的空白字符
            content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
            content_text = re.sub(r' +', ' ', content_text)
            content_text = content_text.strip()
            
            # 移除可能的广告或无关内容
            content_text = re.sub(r'广告|推广|点击查看|更多信息', '', content_text)
            
            # 限制内容长度（避免过长）
            max_length = 10000
            if len(content_text) > max_length:
                content_text = content_text[:max_length] + "...(内容已截断)"
                logging.info(f"文章内容过长，已截断至{max_length}字符")
            
            logging.info(f"成功提取文章内容，长度: {len(content_text)} 字符")
            return content_text
            
        except Exception as e:
            logging.error(f"清理内容失败: {e}")
            return content_text
    
    def scrape_single_title(self, title):
        """爬取单个标题的信息"""
        try:
            # 设置当前搜索标题
            self.current_search_title = title
            
            # 搜索标题
            if not self.search_baidu(title):
                return None
            
            # 查找百度健康结果
            if not self.find_baidu_health_result():
                return None
            
            # 信息已经在find_baidu_health_result中提取并添加到results中
            return True
            
        except Exception as e:
            logging.error(f"爬取标题'{title}'失败: {e}")
            return None
    
    def save_to_excel(self, data, filename=None):
        """保存结果到Excel文件"""
        try:
            if not filename:
                # 生成当日文件名
                today = datetime.now().strftime("%Y%m%d")
                filename = f"百度健康爬取结果_{today}.xlsx"
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 重新排列列顺序
            columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
            df = df.reindex(columns=columns_order)
            
            # 保存到Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            logging.info(f"结果已保存到: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"保存Excel文件失败: {e}")
            return None
    
    def append_to_excel(self, new_data):
        """实时追加数据到Excel文件"""
        try:
            if not self.excel_file:
                # 第一次写入，创建新文件
                today = datetime.now().strftime("%Y%m%d")
                self.excel_file = f"百度健康爬取结果_{today}.xlsx"
                
                # 如果当天文件已存在，读取后追加；否则创建新文件
                columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                if os.path.exists(self.excel_file):
                    logging.info(f"当天结果文件已存在，读取并追加: {self.excel_file}")
                    existing_df = pd.read_excel(self.excel_file)
                    new_df = pd.DataFrame([new_data])
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                    updated_df = updated_df.reindex(columns=columns_order)
                    updated_df.to_excel(self.excel_file, index=False, engine='openpyxl')
                    logging.info(f"已在现有文件中追加第一条数据")
                else:
                    # 创建包含新数据的DataFrame并保存
                    df = pd.DataFrame([new_data])
                    df = df.reindex(columns=columns_order)
                    df.to_excel(self.excel_file, index=False, engine='openpyxl')
                    logging.info(f"创建新Excel文件并保存第一条数据: {self.excel_file}")
                
            else:
                # 追加到现有文件
                try:
                    # 读取现有数据
                    existing_df = pd.read_excel(self.excel_file)
                    
                    # 添加新数据
                    new_df = pd.DataFrame([new_data])
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                    
                    # 重新排列列顺序
                    columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                    updated_df = updated_df.reindex(columns=columns_order)
                    
                    # 保存更新后的数据
                    updated_df.to_excel(self.excel_file, index=False, engine='openpyxl')
                    logging.info(f"成功追加数据到Excel文件: {self.excel_file}")
                    
                except FileNotFoundError:
                    # 如果文件不存在，重新创建
                    logging.warning("Excel文件不存在，重新创建...")
                    self.excel_file = None
                    self.append_to_excel(new_data)
                    return
                    
        except Exception as e:
            logging.error(f"追加数据到Excel失败: {e}")
            # 如果追加失败，尝试保存到备用文件
            try:
                backup_file = f"备用文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df = pd.DataFrame([new_data])
                columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                df = df.reindex(columns=columns_order)
                df.to_excel(backup_file, index=False, engine='openpyxl')
                logging.info(f"数据已保存到备用文件: {backup_file}")
            except Exception as backup_error:
                logging.error(f"保存到备用文件也失败: {backup_error}")
    
    def save_final_excel(self):
        """保存最终的Excel文件（包含所有数据）"""
        try:
            if self.results and self.excel_file:
                # 读取现有文件
                existing_df = pd.read_excel(self.excel_file)
                
                # 确保所有数据都在文件中
                if len(existing_df) != len(self.results):
                    logging.warning(f"Excel文件中的数据数量({len(existing_df)})与内存中的数据数量({len(self.results)})不匹配")
                    
                    # 重新保存所有数据
                    df = pd.DataFrame(self.results)
                    columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                    df = df.reindex(columns=columns_order)
                    df.to_excel(self.excel_file, index=False, engine='openpyxl')
                    logging.info(f"重新保存所有数据到Excel文件: {self.excel_file}")
                
                return self.excel_file
            else:
                logging.warning("没有数据需要保存")
                return None
                
        except Exception as e:
            logging.error(f"保存最终Excel文件失败: {e}")
            return None
    
    def run(self, excel_file, max_titles=10000):
        """运行爬虫主程序"""
        try:
            logging.info("开始运行百度健康爬虫程序")
            
            # 读取Excel标题
            titles = self.read_excel_titles(excel_file)
            if not titles:
                logging.error("没有找到可用的标题")
                return
            
            # 限制处理数量（避免运行时间过长）
            if len(titles) > max_titles:
                titles = titles[:max_titles]
                logging.info(f"限制处理前{max_titles}个标题")
            
            # 逐个爬取标题
            for i, title in enumerate(titles, 1):
                logging.info(f"正在处理第{i}/{len(titles)}个标题: {title}")
                
                success = self.scrape_single_title(title)
                if success:
                    logging.info(f"成功处理: {title}")
                else:
                    logging.warning(f"处理失败: {title}")
                
                # 智能延迟，避免被反爬
                self.smart_wait(1, 2)
                
                # 每处理几个标题后增加额外延迟
                if i % 5 == 0:
                    logging.info("已处理5个标题，增加额外延迟...")
                    extra_delay = random.uniform(2, 4)
                    time.sleep(extra_delay)
                    logging.info(f"额外延迟 {extra_delay:.2f} 秒完成")
            
            # 保存最终结果（确保数据完整性）
            if self.results:
                filename = self.save_final_excel()
                logging.info(f"爬虫程序完成，共爬取{len(self.results)}条数据")
                return filename
            else:
                logging.warning("没有成功爬取到任何数据")
                return None
                
        except Exception as e:
            logging.error(f"爬虫程序运行失败: {e}")
            return None
        
        finally:
            # 关闭浏览器
            if self.driver:
                self.driver.quit()
                logging.info("浏览器已关闭")

def main():
    """主函数"""
    try:
        # 查找Excel文件（排除结果类Excel，避免把当天结果文件当作输入）
        excel_files = [
            f for f in os.listdir('.')
            if f.endswith('.xlsx')
            and not f.startswith('百度健康爬取结果_')
            and not f.startswith('测试实时保存_')
            and not f.startswith('备用文件_')
        ]
        
        if not excel_files:
            print("当前目录下没有找到Excel文件")
            return
        
        print(f"找到以下Excel文件:")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        
        # 选择文件
        if len(excel_files) == 1:
            selected_file = excel_files[0]
            print(f"自动选择: {selected_file}")
        else:
            while True:
                try:
                    choice = int(input(f"请选择要处理的文件 (1-{len(excel_files)}): ")) - 1
                    if 0 <= choice < len(excel_files):
                        selected_file = excel_files[choice]
                        break
                    else:
                        print("选择无效，请重新输入")
                except ValueError:
                    print("请输入有效的数字")
        
        print(f"开始处理文件: {selected_file}")
        
        # 创建爬虫实例并运行
        scraper = BaiduHealthScraper()
        result_file = scraper.run(selected_file)
        
        if result_file:
            print(f"爬虫程序完成！结果已保存到: {result_file}")
        else:
            print("爬虫程序运行失败，请查看日志文件")
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
