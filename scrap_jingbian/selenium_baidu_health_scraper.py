#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度健康爬虫程序 (基于Selenium模拟浏览器)
功能：读取Excel文件中的文章标题，使用浏览器模拟搜索百度健康相关内容，爬取医生信息
优势：完全模拟真实浏览器行为，避免反爬虫检测，稳定性高
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import os
import logging
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 设置第三方库的日志级别
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class SeleniumBaiduHealthScraper:
    """基于Selenium的百度健康爬虫类"""
    
    def __init__(self, headless=False, use_existing_browser=False, debug_port=None):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
            use_existing_browser: 是否使用现有浏览器实例
            debug_port: 现有浏览器的调试端口（如9222）
        """
        self.driver = None
        self.results = []
        self.current_search_title = ""
        self.excel_file = None
        self.headless = headless
        self.use_existing_browser = use_existing_browser
        self.debug_port = debug_port
        
        # 初始化浏览器
        self._init_browser()
        
    def _init_browser(self):
        """初始化浏览器驱动"""
        try:
            chrome_options = Options()
            
            # 如果使用现有浏览器，连接到现有实例
            if self.use_existing_browser and self.debug_port:
                logging.info(f"连接到现有浏览器，调试端口: {self.debug_port}")
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            else:
                # 配置浏览器选项，模拟真实浏览器
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化检测
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # 设置用户代理
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0')
                
                # 如果使用无头模式
                if self.headless:
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--disable-gpu')
                
                # 其他优化选项
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--lang=zh-CN')
            
            # 创建WebDriver实例
            # 使用webdriver_manager自动管理ChromeDriver
            try:
                # 获取chromedriver路径
                driver_path = ChromeDriverManager().install()
                
                # 检查路径是否正确（webdriver_manager有时会返回错误的文件）
                if not os.path.exists(driver_path) or not os.access(driver_path, os.X_OK) or 'notice' in driver_path.lower():
                    # 如果路径不对，尝试在相同目录下查找chromedriver可执行文件
                    driver_dir = os.path.dirname(driver_path)
                    if os.path.exists(driver_dir):
                        # 查找目录下的chromedriver文件
                        found_driver = False
                        for file in os.listdir(driver_dir):
                            file_path = os.path.join(driver_dir, file)
                            # 检查是否是文件且可执行，且文件名包含chromedriver但不包含notice
                            if (os.path.isfile(file_path) and 
                                os.access(file_path, os.X_OK) and
                                'chromedriver' in file.lower() and 
                                'notice' not in file.lower() and
                                not file.endswith('.txt') and
                                not file.endswith('.md')):
                                driver_path = file_path
                                logging.info(f"找到正确的chromedriver路径: {driver_path}")
                                found_driver = True
                                break
                        
                        if not found_driver:
                            # 如果还是找不到，尝试查找所有子目录
                            for root, dirs, files in os.walk(driver_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    if (os.path.isfile(file_path) and 
                                        os.access(file_path, os.X_OK) and
                                        'chromedriver' in file.lower() and 
                                        'notice' not in file.lower() and
                                        not file.endswith('.txt') and
                                        not file.endswith('.md')):
                                        driver_path = file_path
                                        logging.info(f"在子目录中找到chromedriver路径: {driver_path}")
                                        found_driver = True
                                        break
                                if found_driver:
                                    break
                
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logging.error(f"使用webdriver_manager失败: {e}")
                logging.info("尝试使用系统PATH中的chromedriver...")
                # 如果webdriver_manager失败，尝试使用系统PATH中的chromedriver
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as e2:
                    logging.error(f"使用系统chromedriver也失败: {e2}")
                    raise Exception("无法初始化Chrome浏览器驱动，请确保已安装Chrome浏览器和ChromeDriver")
            
            # 设置窗口大小
            self.driver.set_window_size(1920, 1080)
            
            # 执行JavaScript来隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logging.info("浏览器驱动初始化成功")
            
        except Exception as e:
            logging.error(f"初始化浏览器失败: {e}")
            raise
    
    def read_excel_titles(self, excel_file):
        """
        读取Excel文件中的文章标题
        优先读取第二列，如果只有一列则读取第一列
        """
        try:
            df = pd.read_excel(excel_file)
            
            # 显示Excel文件的基本信息
            logging.info(f"Excel文件共有 {len(df.columns)} 列，{len(df)} 行")
            logging.info(f"列名: {list(df.columns)}")
            
            # 确定读取哪一列
            if len(df.columns) >= 2:
                # 如果有2列或更多，读取第二列（索引1）
                column_index = 1
                logging.info(f"检测到多列，读取第二列（索引{column_index}）")
            elif len(df.columns) == 1:
                # 如果只有1列，读取第一列（索引0）
                column_index = 0
                logging.info(f"检测到只有一列，读取第一列（索引{column_index}）")
            else:
                logging.error(f"Excel文件没有数据列")
                return []
            
            # 读取指定列的数据
            titles = df.iloc[:, column_index].dropna().tolist()
            
            # 过滤空字符串
            titles = [str(title).strip() for title in titles if str(title).strip()]
            
            logging.info(f"成功读取{len(titles)}个文章标题")
            if titles:
                logging.info(f"前3个标题示例: {titles[:3]}")
            
            return titles
            
        except Exception as e:
            logging.error(f"读取Excel文件失败: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return []
    
    def smart_delay(self, min_seconds=4, max_seconds=6):
        """智能延迟，避免被反爬"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        logging.debug(f"智能延迟 {delay:.2f} 秒")
    
    def search_baidu(self, title, page=0):
        """
        在百度搜索文章标题（使用浏览器模拟）
        
        Args:
            title: 搜索标题
            page: 页码，0表示第一页，1表示第二页，2表示第三页
        """
        try:
            page_info = f"第{page + 1}页" if page > 0 else "第1页"
            logging.info(f"正在搜索: {title} ({page_info})")
            
            # 智能延迟
            self.smart_delay(4, 6)
            
            # 如果是第一页，直接访问百度首页并搜索
            if page == 0:
                # 访问百度首页
                self.driver.get("https://www.baidu.com")
                time.sleep(3)  # 等待页面加载
                
                # 查找搜索框并输入关键词
                try:
                    # 尝试多种选择器来找到搜索框（按优先级排序）
                    # 优先使用新的AI搜索界面选择器
                    search_selectors = [
                        ("textarea#chat-textarea", "AI搜索框 textarea#chat-textarea"),
                        ("#chat-textarea", "AI搜索框（简化）"),
                        ("textarea.chat-input-textarea", "AI搜索框 class选择器"),
                        ("input#kw", "传统搜索框 input#kw"),
                        ("input[name='wd']", "name属性选择器"),
                        ("#kw", "传统搜索框（简化）"),
                        ("input[type='text'][name='wd']", "组合选择器"),
                        ("input[autocomplete='off'][name='wd']", "autocomplete选择器"),
                    ]
                    
                    search_input = None
                    used_selector = None
                    
                    for selector, description in search_selectors:
                        try:
                            logging.debug(f"尝试使用选择器: {description} ({selector})")
                            # 等待元素可见且可交互
                            search_input = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            if search_input:
                                used_selector = description
                                logging.info(f"成功找到搜索框，使用选择器: {description}")
                                break
                        except TimeoutException:
                            logging.debug(f"选择器 {description} 超时，尝试下一个")
                            continue
                        except Exception as e:
                            logging.debug(f"选择器 {description} 失败: {e}")
                            continue
                    
                    if not search_input:
                        logging.error("无法找到搜索框，尝试备用方法...")
                        # 备用方法：使用JavaScript查找并设置值
                        try:
                            # 尝试通过JavaScript直接设置搜索框的值（优先AI搜索框）
                            self.driver.execute_script("""
                                var input = document.getElementById('chat-textarea') || 
                                            document.getElementById('kw') || 
                                            document.querySelector('input[name="wd"]') ||
                                            document.querySelector('textarea.chat-input-textarea');
                                if (input) {
                                    input.value = arguments[0];
                                    input.focus();
                                    // 触发input事件
                                    var event = new Event('input', { bubbles: true });
                                    input.dispatchEvent(event);
                                }
                            """, title)
                            time.sleep(1)
                            # 尝试点击搜索按钮（优先AI搜索按钮）
                            try:
                                search_button = self.driver.find_element(By.CSS_SELECTOR, "button#chat-submit-button, input#su")
                                search_button.click()
                                logging.info("使用JavaScript找到并点击搜索按钮")
                            except:
                                # 使用回车键
                                self.driver.execute_script("""
                                    var input = document.getElementById('chat-textarea') || 
                                                document.getElementById('kw') || 
                                                document.querySelector('input[name="wd"]');
                                    if (input) {
                                        var event = new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true});
                                        input.dispatchEvent(event);
                                    }
                                """)
                                logging.info("使用JavaScript发送回车键")
                        except Exception as js_error:
                            logging.error(f"JavaScript备用方法也失败: {js_error}")
                            return None
                    else:
                        # 正常方法：清空搜索框并输入关键词
                        try:
                            # 滚动到搜索框位置
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
                            time.sleep(0.5)
                            
                            # 清空搜索框
                            search_input.clear()
                            time.sleep(0.3)
                            
                            # 输入关键词（逐字符输入，模拟真实用户）
                            # 对于textarea，可能需要先点击聚焦
                            if search_input.tag_name.lower() == 'textarea':
                                # textarea需要特殊处理
                                search_input.click()
                                time.sleep(0.2)
                            
                            search_input.send_keys(title)
                            time.sleep(0.3)
                            
                            # 对于textarea，触发input和change事件以确保被识别
                            if search_input.tag_name.lower() == 'textarea':
                                self.driver.execute_script("""
                                    var elem = arguments[0];
                                    var event1 = new Event('input', { bubbles: true });
                                    var event2 = new Event('change', { bubbles: true });
                                    elem.dispatchEvent(event1);
                                    elem.dispatchEvent(event2);
                                """, search_input)
                                time.sleep(0.2)
                            
                            # 验证输入是否成功（textarea和input都使用value属性）
                            input_value = search_input.get_attribute('value')
                            # 对于textarea，也可以尝试textContent或innerText
                            if not input_value or input_value != title:
                                if search_input.tag_name.lower() == 'textarea':
                                    # 尝试获取textarea的文本内容
                                    input_value = self.driver.execute_script("return arguments[0].value || arguments[0].textContent || arguments[0].innerText;", search_input)
                                
                                if input_value != title:
                                    logging.warning(f"输入验证失败，期望: {title}, 实际: {input_value}")
                                    # 尝试重新输入
                                    search_input.clear()
                                    time.sleep(0.2)
                                    if search_input.tag_name.lower() == 'textarea':
                                        search_input.click()
                                        time.sleep(0.1)
                                    search_input.send_keys(title)
                                    time.sleep(0.3)
                                    # 再次触发事件
                                    if search_input.tag_name.lower() == 'textarea':
                                        self.driver.execute_script("""
                                            var elem = arguments[0];
                                            var event1 = new Event('input', { bubbles: true });
                                            var event2 = new Event('change', { bubbles: true });
                                            elem.dispatchEvent(event1);
                                            elem.dispatchEvent(event2);
                                        """, search_input)
                                    time.sleep(0.2)
                                    # 再次验证
                                    input_value = search_input.get_attribute('value') or self.driver.execute_script("return arguments[0].value || arguments[0].textContent;", search_input)
                                    if input_value != title:
                                        logging.warning(f"重新输入后验证仍失败，但继续执行")
                            
                            logging.info(f"成功输入搜索关键词: {title}")
                            
                        except Exception as input_error:
                            logging.error(f"输入关键词失败: {input_error}")
                            return None
                        
                        # 点击搜索按钮或按回车（优先AI搜索按钮）
                        try:
                            # 优先尝试AI搜索界面的按钮
                            search_button_selectors = [
                                "button#chat-submit-button",  # AI搜索按钮
                                "input#su",  # 传统搜索按钮
                                "button[type='submit']",  # 通用提交按钮
                            ]
                            
                            search_button = None
                            for selector in search_button_selectors:
                                try:
                                    search_button = WebDriverWait(self.driver, 2).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    if search_button:
                                        logging.info(f"找到搜索按钮: {selector}")
                                        break
                                except TimeoutException:
                                    continue
                            
                            if search_button:
                                search_button.click()
                                logging.info("点击搜索按钮成功")
                            else:
                                # 如果找不到搜索按钮，使用回车键
                                logging.info("未找到搜索按钮，使用回车键")
                                search_input.send_keys(Keys.RETURN)
                        except Exception as btn_error:
                            # 如果点击按钮失败，使用回车键
                            logging.warning(f"点击搜索按钮失败: {btn_error}，使用回车键")
                            try:
                                search_input.send_keys(Keys.RETURN)
                            except:
                                # 最后的备用方法：使用JavaScript触发点击
                                self.driver.execute_script("""
                                    var btn = document.getElementById('chat-submit-button') || document.getElementById('su');
                                    if (btn) btn.click();
                                """)
                    
                    # 等待搜索结果页面加载
                    try:
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.result, div[class*='result']"))
                        )
                        logging.info(f"搜索结果页面加载成功 ({page_info})")
                    except TimeoutException:
                        logging.warning("搜索结果页面加载超时，但继续执行...")
                        # 检查当前URL是否包含搜索结果
                        current_url = self.driver.current_url
                        if 'baidu.com/s' in current_url:
                            logging.info("当前URL显示已在搜索结果页面")
                        else:
                            logging.error("未成功跳转到搜索结果页面")
                            return None
                    
                except TimeoutException:
                    logging.error("搜索超时，可能遇到验证码")
                    # 检查是否有验证码
                    if self._check_captcha():
                        return None
                    return None
                except Exception as e:
                    logging.error(f"搜索过程出错: {e}")
                    import traceback
                    logging.error(traceback.format_exc())
                    return None
            else:
                # 翻页：通过URL参数翻页
                import urllib.parse
                encoded_title = urllib.parse.quote(title)
                pn = page * 10  # 每页pn参数递增10
                search_url = f"https://www.baidu.com/s?wd={encoded_title}&pn={pn}"
                logging.info(f"翻页URL: {search_url}")
                
                self.driver.get(search_url)
                time.sleep(2)  # 等待页面加载
                
                # 等待搜索结果加载
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.result"))
                    )
                    logging.info(f"翻页成功 ({page_info})")
                except TimeoutException:
                    logging.warning(f"翻页后页面加载超时 ({page_info})")
                    if self._check_captcha():
                        return None
            
            # 检查是否被反爬
            if self._check_captcha():
                logging.warning("检测到反爬验证，等待用户处理...")
                import threading

                def wait_for_input(event):
                    input("请手动完成验证后，按回车键继续...")
                    event.set()

                # 创建一个事件对象用于线程间通信
                input_event = threading.Event()
                # 启动等待用户输入的线程
                input_thread = threading.Thread(target=wait_for_input, args=(input_event,))
                input_thread.start()

                # 主线程等待10分钟（600秒），或者直到用户输入
                input_event.wait(timeout=600)

                if input_event.is_set():
                    logging.info("用户已手动完成验证，继续执行。")
                else:
                    print("等待10分钟后仍未完成验证，程序将自动跳过该条。")
                    logging.warning("等待10分钟后未检测到用户输入，自动跳过。")
                return None
            
            # 返回当前页面的HTML内容
            return self.driver.page_source
            
        except Exception as e:
            logging.error(f"百度搜索失败: {e}")
            return None
    
    def _check_captcha(self):
        """检查页面是否有验证码"""
        try:
            page_source = self.driver.page_source
            if "安全验证" in page_source or "验证码" in page_source or "captcha" in page_source.lower():
                return True
            return False
        except:
            return False
    
    def find_baidu_health_result(self, html_content, current_page=0, max_pages=3):
        """
        从HTML内容中查找百度健康结果
        
        Args:
            html_content: 当前页面的HTML内容（可选，如果不提供则使用driver.page_source）
            current_page: 当前页码（0表示第一页）
            max_pages: 最大翻页数（总共搜索几页）
        """
        try:
            # 如果提供了html_content，使用BeautifulSoup解析
            # 否则直接使用driver查找元素
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                results = soup.find_all('div', class_=lambda x: x and 'result' in x)
                if not results:
                    results = soup.find_all('div', {'class': re.compile(r'result')})
            else:
                # 使用Selenium查找搜索结果
                results = self.driver.find_elements(By.CSS_SELECTOR, "div.result")
            
            page_info = f"第{current_page + 1}页" if current_page > 0 else "第1页"
            logging.info(f"找到{len(results)}个搜索结果 ({page_info})")
            
            # 遍历搜索结果
            for i, result in enumerate(results):
                try:
                    # 如果使用BeautifulSoup解析
                    if isinstance(result, type(soup.find('div')) if 'soup' in locals() else None):
                        # 查找百度健康标识
                        health_indicators = result.find_all('span', class_='cosc-source-text')
                        
                        for indicator in health_indicators:
                            if "百度健康" in indicator.get_text():
                                logging.info(f"找到百度健康标识: {indicator.get_text()}")
                                
                                # 查找标题链接
                                title_link = result.find('h3').find('a') if result.find('h3') else result.find('a', target='_blank')
                                
                                if title_link and title_link.get('href'):
                                    href = title_link.get('href')
                                    title_text = title_link.get_text().strip()
                                    
                                    logging.info(f"找到百度健康结果: {title_text}")
                                    
                                    # 获取详情页内容
                                    detail_content = self.get_detail_page(href)
                                    if detail_content and self.verify_baidu_health_page(detail_content):
                                        logging.info("确认是百度健康页面，开始提取信息")
                                        
                                        # 提取详细信息
                                        info = self.extract_health_info(detail_content)
                                        info['search_title'] = self.current_search_title
                                        
                                        # 添加到结果列表
                                        self.results.append(info)
                                        logging.info(f"成功提取信息: {info}")
                                        
                                        # 实时保存到Excel文件
                                        self.append_to_excel(info)
                                        logging.info(f"数据已实时保存到Excel文件")
                                        
                                        return True
                                    else:
                                        logging.warning("不是真正的百度健康页面，继续查找")
                                        continue
                    else:
                        # 使用Selenium查找元素
                        try:
                            # 查找百度健康标识
                            health_indicators = result.find_elements(By.CSS_SELECTOR, "span.cosc-source-text")
                            
                            for indicator in health_indicators:
                                indicator_text = indicator.text
                                if "百度健康" in indicator_text:
                                    logging.info(f"找到百度健康标识: {indicator_text}")
                                    
                                    # 查找标题链接
                                    try:
                                        title_link = result.find_element(By.CSS_SELECTOR, "h3 a")
                                        href = title_link.get_attribute('href')
                                        title_text = title_link.text.strip()
                                        
                                        if href:
                                            logging.info(f"找到百度健康结果: {title_text}")
                                            
                                            # 获取详情页内容
                                            detail_content = self.get_detail_page(href)
                                            if detail_content and self.verify_baidu_health_page(detail_content):
                                                logging.info("确认是百度健康页面，开始提取信息")
                                                
                                                # 提取详细信息
                                                info = self.extract_health_info(detail_content)
                                                info['search_title'] = self.current_search_title
                                                
                                                # 添加到结果列表
                                                self.results.append(info)
                                                logging.info(f"成功提取信息: {info}")
                                                
                                                # 实时保存到Excel文件
                                                self.append_to_excel(info)
                                                logging.info(f"数据已实时保存到Excel文件")
                                                
                                                return True
                                            else:
                                                logging.warning("不是真正的百度健康页面，继续查找")
                                                continue
                                    except NoSuchElementException:
                                        logging.debug("未找到标题链接")
                                        continue
                                        
                        except Exception as e:
                            logging.debug(f"处理搜索结果时出错: {e}")
                            continue
                
                except Exception as e:
                    logging.debug(f"处理搜索结果时出错: {e}")
                    continue
            
            # 如果当前页没找到，尝试翻页
            if current_page < max_pages - 1:
                next_page_num = current_page + 1
                logging.info(f"当前页未找到百度健康结果，尝试翻到第{next_page_num + 1}页...")
                
                # 通过浏览器翻页
                next_html = self.search_baidu(self.current_search_title, page=next_page_num)
                if next_html:
                    return self.find_baidu_health_result(next_html, current_page=next_page_num, max_pages=max_pages)
                else:
                    logging.warning(f"无法获取第{next_page_num + 1}页内容")
            
            logging.warning(f"已搜索{current_page + 1}页，未找到百度健康结果")
            return False
            
        except Exception as e:
            logging.error(f"查找百度健康结果失败: {e}")
            return False
    
    def get_detail_page(self, href):
        """获取详情页内容（使用浏览器导航）"""
        try:
            # 处理相对URL
            if href.startswith('/'):
                url = f"https://www.baidu.com{href}"
            elif href.startswith('http'):
                url = href
            else:
                url = f"https://www.baidu.com/{href}"
            
            logging.info(f"获取详情页: {url}")

            # 智能延迟
            self.smart_delay(4, 6)
            
            # 使用浏览器导航到详情页
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 等待页面主要内容加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logging.warning("页面加载超时")
            
            # 检查最终URL
            final_url = self.driver.current_url
            logging.info(f"最终URL: {final_url}")
            
            # 返回页面HTML内容
            return self.driver.page_source
            
        except Exception as e:
            logging.error(f"获取详情页失败: {e}")
            return None
    
    def verify_baidu_health_page(self, html_content):
        """验证是否为真正的百度健康页面"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 检查URL是否为百度健康域名
            current_url = self.driver.current_url
            if "health.baidu.com" not in current_url:
                logging.info("页面不是百度健康域名")
                return False
            
            # 查找"百度健康内容审核团队优选"标识
            page_text = soup.get_text()
            if "百度健康内容审核团队优选" in page_text:
                logging.info("找到百度健康内容审核团队优选标识")
                return True
            
            # 检查页面标题
            title = soup.find('title')
            if title and ("百度健康" in title.get_text() or "健康" in title.get_text()):
                logging.info(f"通过页面标题确认: {title.get_text()}")
                return True
            
            logging.warning("未找到百度健康页面特征标识")
            return False
            
        except Exception as e:
            logging.error(f"验证百度健康页面失败: {e}")
            return False
    
    def extract_health_info(self, html_content):
        """提取健康页面的信息"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            info = {
                'title': '',
                'doctor': '',
                'position': '',
                'department': '',
                'content': ''
            }
            
            # 提取标题
            try:
                title_selectors = [
                    "h1", ".title", ".article-title", ".page-title",
                    "[class*='title']", "h2", "h3"
                ]
                for selector in title_selectors:
                    try:
                        title_element = soup.select_one(selector)
                        if title_element and title_element.get_text().strip():
                            info['title'] = title_element.get_text().strip()
                            break
                    except:
                        continue
            except:
                info['title'] = "未找到标题"
            
            # 提取医生信息
            try:
                # 方法1: 通过父容器查找（推荐方式）
                try:
                    name_info_container = soup.select_one("div.index_nameInfo__9H6bC")
                    if name_info_container:
                        logging.info("找到医生信息容器")
                        
                        # 从容器中提取各个信息
                        doctor_name_element = name_info_container.select_one("span.index_name__0Yl8k")
                        if doctor_name_element:
                            info['doctor'] = doctor_name_element.get_text().strip()
                            logging.info(f"从容器中找到医生姓名: {info['doctor']}")
                        
                        position_element = name_info_container.select_one("span.index_title__wNRZD")
                        if position_element:
                            info['position'] = position_element.get_text().strip()
                            logging.info(f"从容器中找到医生职位: {info['position']}")
                        
                        dept_element = name_info_container.select_one("span.index_department__y9DFE")
                        if dept_element:
                            info['department'] = dept_element.get_text().strip()
                            logging.info(f"从容器中找到科室信息: {info['department']}")
                    else:
                        logging.debug("未找到医生信息容器 div.index_nameInfo__9H6bC")
                except Exception as e:
                    logging.debug(f"通过容器提取医生信息失败: {e}")
                
                # 方法2: 直接查找各个span（备用方式）
                if not info['doctor'] or not info['position'] or not info['department']:
                    try:
                        doctor_name_element = soup.select_one("span.index_name__0Yl8k")
                        if doctor_name_element and not info['doctor']:
                            info['doctor'] = doctor_name_element.get_text().strip()
                            logging.info(f"直接找到医生姓名: {info['doctor']}")
                    except Exception as e:
                        logging.debug(f"直接查找医生姓名失败: {e}")
                    
                    try:
                        position_element = soup.select_one("span.index_title__wNRZD")
                        if position_element and not info['position']:
                            info['position'] = position_element.get_text().strip()
                            logging.info(f"直接找到医生职位: {info['position']}")
                    except Exception as e:
                        logging.debug(f"直接查找医生职位失败: {e}")
                    
                    try:
                        dept_element = soup.select_one("span.index_department__y9DFE")
                        if dept_element and not info['department']:
                            info['department'] = dept_element.get_text().strip()
                            logging.info(f"直接找到科室信息: {info['department']}")
                    except Exception as e:
                        logging.debug(f"直接查找科室信息失败: {e}")
                
                # 方法3: 通过class名称的部分匹配（更宽松的匹配）
                if not info['doctor'] or not info['position'] or not info['department']:
                    try:
                        # 查找所有包含这些class的span
                        all_spans = soup.find_all('span')
                        for span in all_spans:
                            class_attr = span.get('class', [])
                            if isinstance(class_attr, list):
                                class_str = ' '.join(class_attr)
                            else:
                                class_str = str(class_attr)
                            
                            # 匹配医生姓名
                            if 'index_name__' in class_str and not info['doctor']:
                                text = span.get_text().strip()
                                if text and len(text) < 20:  # 姓名通常不会太长
                                    info['doctor'] = text
                                    logging.info(f"通过部分匹配找到医生姓名: {info['doctor']}")
                            
                            # 匹配职位
                            if 'index_title__' in class_str and not info['position']:
                                text = span.get_text().strip()
                                if text and ('医师' in text or '医生' in text or '主任' in text or '副主任' in text):
                                    info['position'] = text
                                    logging.info(f"通过部分匹配找到医生职位: {info['position']}")
                            
                            # 匹配科室
                            if 'index_department__' in class_str and not info['department']:
                                text = span.get_text().strip()
                                if text and ('科' in text):
                                    info['department'] = text
                                    logging.info(f"通过部分匹配找到科室信息: {info['department']}")
                    except Exception as e:
                        logging.debug(f"通过部分匹配提取医生信息失败: {e}")
                
                # 方法4: 备用选择器（通用匹配）
                if not info['doctor'] or not info['position'] or not info['department']:
                    backup_selectors = [
                        ".doctor-name", ".doctor-info .name", ".expert-name",
                        ".author", ".doctor", ".expert", "[class*='doctor']",
                        "[class*='author']", "[class*='expert']"
                    ]
                    
                    for selector in backup_selectors:
                        try:
                            doctor_element = soup.select_one(selector)
                            if doctor_element and doctor_element.get_text().strip():
                                doctor_text = doctor_element.get_text().strip()
                                logging.info(f"备用选择器找到医生信息: {doctor_text}")
                                
                                # 解析医生信息
                                doctor_match = re.search(r'([^\s]+)\s+([^\s]+医师)', doctor_text)
                                if doctor_match and not info['doctor']:
                                    info['doctor'] = doctor_match.group(1)
                                if doctor_match and not info['position']:
                                    info['position'] = doctor_match.group(2)
                                
                                dept_match = re.search(r'([^\s]+科)', doctor_text)
                                if dept_match and not info['department']:
                                    info['department'] = dept_match.group(1)
                                
                                break
                        except:
                            continue
                
                # 方法5: 从页面源码中搜索（最后手段）
                if not info['doctor'] or not info['position'] or not info['department']:
                    page_text = soup.get_text()
                    
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
                content = self.extract_article_content(soup)
                info['content'] = content
                logging.info(f"成功提取文章内容，长度: {len(content)} 字符")
            except Exception as e:
                logging.warning(f"提取文章内容失败: {e}")
                info['content'] = "未找到文章内容"
            
            logging.info(f"成功提取信息: {info}")
            return info
            
        except Exception as e:
            logging.error(f"提取健康信息失败: {e}")
            return {
                'title': '提取失败',
                'doctor': '提取失败',
                'position': '提取失败',
                'department': '提取失败',
                'content': '提取失败'
            }
    
    def extract_article_content(self, soup):
        """提取文章内容"""
        try:
            content_text = ""
            
            # 方法1: 直接提取所有p标签内容
            try:
                logging.info("尝试提取所有p标签内容...")
                p_elements = soup.find_all('p')
                
                if p_elements:
                    p_texts = []
                    for p in p_elements:
                        text = p.get_text(strip=True)
                        if text and len(text) > 5:
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
                            content_element = soup.select_one(selector)
                            if content_element:
                                content_text = content_element.get_text(strip=True)
                                if content_text and len(content_text) > 50:
                                    logging.info(f"使用选择器 '{selector}' 成功提取内容")
                                    break
                        except:
                            continue
                except Exception as e:
                    logging.debug(f"CSS选择器提取失败: {e}")
            
            # 方法3: 尝试提取特定内容区域
            if not content_text:
                try:
                    logging.info("尝试提取特定内容区域...")
                    content_divs = soup.select("div[data-anchor-id='content'], div[class*='articleWrap'], div[class*='textContent']")
                    
                    for div in content_divs:
                        try:
                            text = div.get_text(strip=True)
                            if text and len(text) > 100:
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
                
        except Exception as e:
            logging.error(f"提取文章内容失败: {e}")
            return "提取文章内容失败"
    
    def clean_content(self, content_text):
        """清理和格式化内容"""
        try:
            # 移除多余的空白字符
            content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
            content_text = re.sub(r' +', ' ', content_text)
            content_text = content_text.strip()
            
            # 移除可能的广告或无关内容
            content_text = re.sub(r'广告|推广|点击查看|更多信息', '', content_text)
            
            # 限制内容长度
            max_length = 1000
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
            self.current_search_title = title
            
            # 搜索标题（从第一页开始）
            html_content = self.search_baidu(title, page=0)
            if not html_content:
                return None
            
            # 查找百度健康结果（允许翻3页）
            if not self.find_baidu_health_result(html_content, current_page=0, max_pages=3):
                return None
            
            return True
            
        except Exception as e:
            logging.error(f"爬取标题'{title}'失败: {e}")
            return None
    
    def append_to_excel(self, new_data):
        """实时追加数据到Excel文件"""
        try:
            if not self.excel_file:
                today = datetime.now().strftime("%Y%m%d")
                self.excel_file = f"Selenium百度健康爬取结果_{today}.xlsx"
                
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
                    df = pd.DataFrame([new_data])
                    df = df.reindex(columns=columns_order)
                    df.to_excel(self.excel_file, index=False, engine='openpyxl')
                    logging.info(f"创建新Excel文件并保存第一条数据: {self.excel_file}")
                
            else:
                try:
                    existing_df = pd.read_excel(self.excel_file)
                    new_df = pd.DataFrame([new_data])
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                    
                    columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                    updated_df = updated_df.reindex(columns=columns_order)
                    updated_df.to_excel(self.excel_file, index=False, engine='openpyxl')
                    logging.info(f"成功追加数据到Excel文件: {self.excel_file}")
                    
                except FileNotFoundError:
                    logging.warning("Excel文件不存在，重新创建...")
                    self.excel_file = None
                    self.append_to_excel(new_data)
                    return
                    
        except Exception as e:
            logging.error(f"追加数据到Excel失败: {e}")
            try:
                backup_file = f"备用文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df = pd.DataFrame([new_data])
                columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                df = df.reindex(columns=columns_order)
                df.to_excel(backup_file, index=False, engine='openpyxl')
                logging.info(f"数据已保存到备用文件: {backup_file}")
            except Exception as backup_error:
                logging.error(f"保存到备用文件也失败: {backup_error}")
    
    def run(self, excel_file, max_titles=10000):
        """运行爬虫主程序"""
        try:
            logging.info("开始运行Selenium百度健康爬虫程序")
            
            titles = self.read_excel_titles(excel_file)
            if not titles:
                logging.error("没有找到可用的标题")
                return
            
            # 逐个爬取标题
            for i, title in enumerate(titles, 1):
                logging.info(f"正在处理第{i}/{len(titles)}个标题: {title}")

                self.smart_delay(4, 6)
                
                success = self.scrape_single_title(title)
                if success:
                    logging.info(f"成功处理: {title}")
                else:
                    logging.warning(f"处理失败: {title}")
                
                # 智能延迟
                self.smart_delay(4, 6)
                
                # 每处理几个标题后增加额外延迟
                if i % 10 == 0:
                    logging.info("已处理10个标题，增加额外延迟...")
                    extra_delay = random.uniform(1, 2)
                    time.sleep(extra_delay)
                    logging.info(f"额外延迟 {extra_delay:.2f} 秒完成")
            
            if self.results:
                logging.info(f"爬虫程序完成，共爬取{len(self.results)}条数据")
                return self.excel_file
            else:
                logging.warning("没有成功爬取到任何数据")
                return None
                
        except Exception as e:
            logging.error(f"爬虫程序运行失败: {e}")
            return None
        finally:
            # 关闭浏览器
            self.close()
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("浏览器已关闭")
        except Exception as e:
            logging.error(f"关闭浏览器失败: {e}")


def main():
    """主函数"""
    try:
        excel_files = [
            f for f in os.listdir('.')
            if f.endswith('.xlsx')
            and not f.startswith('Selenium百度健康爬取结果_')
            and not f.startswith('快速百度健康爬取结果_')
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
        
        # 询问是否使用现有浏览器
        use_existing = input("是否使用现有浏览器实例？(y/n，默认n): ").strip().lower()
        use_existing_browser = use_existing == 'y'
        debug_port = None
        
        if use_existing_browser:
            debug_port_input = input("请输入浏览器调试端口（默认9222）: ").strip()
            debug_port = int(debug_port_input) if debug_port_input else 9222
        
        # 询问是否使用无头模式
        headless_input = input("是否使用无头模式（不显示浏览器窗口）？(y/n，默认n): ").strip().lower()
        headless = headless_input == 'y'
        
        print(f"开始处理文件: {selected_file}")
        
        scraper = SeleniumBaiduHealthScraper(
            headless=headless,
            use_existing_browser=use_existing_browser,
            debug_port=debug_port
        )
        result_file = scraper.run(selected_file)
        
        if result_file:
            print(f"Selenium爬虫程序完成！结果已保存到: {result_file}")
        else:
            print("Selenium爬虫程序运行失败，请查看日志文件")
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()
