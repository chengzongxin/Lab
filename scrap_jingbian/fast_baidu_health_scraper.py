#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速百度健康爬虫程序 (基于requests + BeautifulSoup)
功能：读取Excel文件中的文章标题，快速搜索百度健康相关内容，爬取医生信息
优势：速度快，资源占用少，稳定性高
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import os
import logging
import re
import urllib.parse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fast_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 设置第三方库的日志级别
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

headers = {
    'Host': 'www.baidu.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cookie': 'BIDUPSID=0BA67C76418CBE48FFD22A9BE212E1B6; PSTM=1763283537; BAIDUID=0BA67C76418CBE480B37002D25A89551:FG=1; BDUSS=JFakRxWGd0QURncE1WeDNhLXRsMXFNVG13dWdKaTBHMUtYWjBzM3pRdHJQV1pwRVFBQUFBJCQAAAAAAAAAAAEAAAA45jc3QW5nZWxfwLbPqwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGuwPmlrsD5pdj; BDUSS_BFESS=JFakRxWGd0QURncE1WeDNhLXRsMXFNVG13dWdKaTBHMUtYWjBzM3pRdHJQV1pwRVFBQUFBJCQAAAAAAAAAAAEAAAA45jc3QW5nZWxfwLbPqwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGuwPmlrsD5pdj; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=60276_63145_64007_66529_66585_66583_66592_66675_66689_66684_66791_66801_66804_66849_66605_66903_66932_66958_66961; H_WISE_SIDS=60276_63145_64007_66529_66585_66583_66592_66675_66689_66684_66791_66801_66804_66849_66605_66903_66932_66958_66961; H_WISE_SIDS_BFESS=60276_63145_64007_66529_66585_66583_66592_66675_66689_66684_66791_66801_66804_66849_66605_66903_66932_66958_66961; BA_HECTOR=208g01al0g242kag0g0k212h810l0i1kkcqjq26; BAIDUID_BFESS=0BA67C76418CBE480B37002D25A89551:FG=1; delPer=0; PSINO=7; ZFY=G2W5OGv33Lp:BEpsMMDIviaZzVv1UqynVJ1IeHhWmG:B4:C; __bid_n=19ab5cb1abb45125c5254f; RT="z=1&dm=baidu.com&si=d6d1a2eb-ec16-4370-a20e-27ce613113b8&ss=mje3xe9e&sl=1&tt=v6&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=1n7&ul=3qn&hd=3rf"; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; ab_sr=1.0.1_YTk2YTA5MDA0N2VkMTdhOGYzYjBiNzYyYzZiMGFkYjMxNTA1MDZhODQ3YzI2MDZkYjI1MWQ1N2QxNjE0ODc1MWExMWFhNmZhYjVlNzJmNzYyOTAxYjI5YjZlNDg5N2U0ZDUwOGJmZTg2MjY5ZmY1NDYzN2FjZjQ2MzI0M2MxMjM0OTY5YmRmMWE4MGU1YWQwNzIwMjBhZDIyNTY5NWFhMg=='
}

class FastBaiduHealthScraper:
    """快速百度健康爬虫类"""
    
    def __init__(self, use_proxy=False, proxy_list=None):
        """初始化爬虫"""
        self.session = self._create_session()
        self.results = []
        self.current_search_title = ""
        self.excel_file = None
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        
    def _create_session(self):
        """创建优化的requests会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        
        # 设置请求头
        session.headers.update(headers)
        
        return session
    
    def read_excel_titles(self, excel_file):
        """读取Excel文件第二列的文章标题"""
        try:
            df = pd.read_excel(excel_file)
            
            if len(df.columns) < 2:
                logging.error(f"Excel文件列数不足，当前只有{len(df.columns)}列")
                return []
            
            titles = df.iloc[:, 1].dropna().tolist()
            logging.info(f"成功读取{len(titles)}个文章标题")
            return titles
            
        except Exception as e:
            logging.error(f"读取Excel文件失败: {e}")
            return []
    
    def smart_delay(self, min_seconds=4, max_seconds=6):
        """智能延迟，避免被反爬"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        logging.debug(f"智能延迟 {delay:.2f} 秒")
    
    def search_baidu(self, title, page=0):
        """在百度搜索文章标题
        
        Args:
            title: 搜索标题
            page: 页码，0表示第一页，1表示第二页，2表示第三页
        """
        try:
            # 构建搜索URL
            encoded_title = urllib.parse.quote(title)
            
            # 根据页码构建URL
            # 第一页：www.baidu.com/s?wd={encoded_title}
            # 第二页：www.baidu.com/s?wd={encoded_title}&pn=10
            # 第三页：www.baidu.com/s?wd={encoded_title}&pn=20
            if page == 0:
                search_url = f"https://www.baidu.com/s?wd={encoded_title}"
            else:
                pn = page * 10  # 每页pn参数递增10
                search_url = f"https://www.baidu.com/s?wd={encoded_title}&pn={pn}"
            
            page_info = f"第{page + 1}页" if page > 0 else "第1页"
            logging.info(f"正在搜索: {title} ({page_info})")

            self.smart_delay(4, 6)
            
            # 发送请求
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 检查是否被反爬
            if "安全验证" in response.text or "验证码" in response.text:
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
                # return self.search_baidu(title, page)  # 重新搜索
                return None
            
            logging.info(f"搜索请求成功 ({page_info})")
            return response.text
            
        except Exception as e:
            logging.error(f"百度搜索失败: {e}")
            return None
    
    def find_baidu_health_result(self, html_content, current_page=0, max_pages=3):
        """从HTML内容中查找百度健康结果
        
        Args:
            html_content: 当前页面的HTML内容
            current_page: 当前页码（0表示第一页）
            max_pages: 最大翻页数（总共搜索几页）
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找搜索结果
            results = soup.find_all('div', class_=lambda x: x and 'result' in x)
            if not results:
                # 备用选择器
                results = soup.find_all('div', {'class': re.compile(r'result')})
            
            page_info = f"第{current_page + 1}页" if current_page > 0 else "第1页"
            logging.info(f"找到{len(results)}个搜索结果 ({page_info})")
            
            for result in results:
                try:
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
                
                except Exception as e:
                    logging.debug(f"处理搜索结果时出错: {e}")
                    continue
            
            # 如果当前页没找到，尝试翻页
            if current_page < max_pages - 1:
                next_page_num = current_page + 1
                logging.info(f"当前页未找到百度健康结果，尝试翻到第{next_page_num + 1}页...")
                
                # 通过URL参数翻页
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
        """获取详情页内容"""
        try:
            # 如果是百度重定向链接，优先使用特殊处理方法
            if 'baidu.com/link' in href:
                logging.info("检测到百度重定向链接，使用特殊处理方法")
                result = self.handle_baidu_redirect(href)
                if result:
                    return result
                else:
                    logging.warning("特殊处理方法失败，尝试常规方法")
            
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
            
            # 发送请求，允许重定向
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # 检查最终URL
            final_url = response.url
            logging.info(f"最终URL: {final_url}")
            
            
            return response.text
            
        except Exception as e:
            logging.error(f"获取详情页失败: {e}")
            # 尝试使用备用方法
            return self.get_detail_page_fallback(href)
    
    def get_detail_page_fallback(self, href):
        """备用方法获取详情页"""
        try:
            # 构建备用URL
            if href.startswith('/'):
                url = f"https://www.baidu.com{href}"
            elif href.startswith('http'):
                url = href
            else:
                url = f"https://www.baidu.com/{href}"
            
            logging.info(f"使用备用方法获取详情页: {url}")

            self.smart_delay(4, 6)
            
            # 发送请求，禁用重试
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            
            if response.status_code == 200:
                logging.info("备用方法获取详情页成功")
                return response.text
            else:
                logging.warning(f"备用方法获取详情页失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"备用方法获取详情页也失败: {e}")
            return None
    
    def handle_baidu_redirect(self, href):
        """专门处理百度重定向链接"""
        try:
            # 如果是百度重定向链接，需要特殊处理
            if 'baidu.com/link' in href:
                logging.info("检测到百度重定向链接，使用特殊处理方法")
                
                # 构建完整URL
                if href.startswith('/'):
                    url = f"https://www.baidu.com{href}"
                elif href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.baidu.com/{href}"
                
                # 设置特殊的请求头，模拟真实浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://www.baidu.com/',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1'
                }
                
                # 创建新的session来处理重定向
                session = requests.Session()
                session.headers.update(headers)
                
                # 先获取重定向页面
                response = session.get(url, timeout=15, allow_redirects=False)
                
                if response.status_code in [301, 302, 303, 307, 308]:
                    # 获取重定向目标
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        logging.info(f"重定向到: {redirect_url}")
                        
                        # 如果重定向URL是相对路径，转换为绝对路径
                        if redirect_url.startswith('/'):
                            if 'baijiahao.baidu.com' in str(response.headers):
                                redirect_url = f"https://baijiahao.baidu.com{redirect_url}"
                            else:
                                redirect_url = f"https://www.baidu.com{redirect_url}"
                        
                        # 获取最终页面内容
                        final_response = session.get(redirect_url, timeout=20)
                        if final_response.status_code == 200:
                            logging.info("成功获取重定向后的页面内容")
                            return final_response.text
                        else:
                            logging.warning(f"获取重定向页面失败，状态码: {final_response.status_code}")
                            return None
                    else:
                        logging.warning("未找到重定向目标URL")
                        return None
                else:
                    # 没有重定向，直接返回内容
                    if response.status_code == 200:
                        return response.text
                    else:
                        logging.warning(f"获取页面失败，状态码: {response.status_code}")
                        return None
                        
        except Exception as e:
            logging.error(f"处理百度重定向链接失败: {e}")
            return None
    
    def verify_baidu_health_page(self, html_content):
        """验证是否为真正的百度健康页面"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 检查URL是否为百度健康域名
            if "health.baidu.com" not in str(soup):
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
                self.excel_file = f"快速百度健康爬取结果_{today}.xlsx"
                
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
            logging.info("开始运行快速百度健康爬虫程序")
            
            titles = self.read_excel_titles(excel_file)
            if not titles:
                logging.error("没有找到可用的标题")
                return
            
            # if len(titles) > max_titles:
            #     titles = titles[:max_titles]
            #     logging.info(f"限制处理前{max_titles}个标题")
            
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

def main():
    """主函数"""
    try:
        excel_files = [
            f for f in os.listdir('.')
            if f.endswith('.xlsx')
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
        
        print(f"开始处理文件: {selected_file}")
        
        scraper = FastBaiduHealthScraper()
        result_file = scraper.run(selected_file)
        
        if result_file:
            print(f"快速爬虫程序完成！结果已保存到: {result_file}")
        else:
            print("快速爬虫程序运行失败，请查看日志文件")
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
