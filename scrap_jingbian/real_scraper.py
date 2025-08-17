#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的百度健康爬虫程序
实现实际的百度搜索和页面爬取功能
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import logging
import urllib.parse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BaiduHealthScraper:
    """百度健康爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = []
        
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
    
    def search_baidu(self, title, page=1):
        """在百度搜索文章标题"""
        try:
            # 构建搜索URL
            encoded_title = urllib.parse.quote(title)
            search_url = f"https://www.baidu.com/s?wd={encoded_title}&pn={(page-1)*10}"
            
            logging.info(f"正在搜索: {title} (第{page}页)")
            
            # 发送请求
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logging.error(f"百度搜索失败: {e}")
            return None
    
    def find_baidu_health_links(self, html_content):
        """从搜索结果中查找百度健康链接"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            health_links = []
            
            # 查找搜索结果
            results = soup.find_all('div', class_='result')
            
            for result in results:
                try:
                    # 查找标题链接
                    title_link = result.find('h3', class_='t').find('a')
                    if not title_link:
                        continue
                    
                    title_text = title_link.get_text(strip=True)
                    link_url = title_link.get('href', '')
                    
                    # 查找摘要信息
                    abstract = result.find('div', class_='c-abstract')
                    if abstract and '百度健康' in abstract.get_text():
                        health_links.append({
                            'title': title_text,
                            'url': link_url,
                            'abstract': abstract.get_text(strip=True)
                        })
                        logging.info(f"找到百度健康链接: {title_text}")
                
                except Exception as e:
                    continue
            
            return health_links
            
        except Exception as e:
            logging.error(f"解析搜索结果失败: {e}")
            return []
    
    def get_baidu_health_page(self, url):
        """获取百度健康页面内容"""
        try:
            # 处理相对URL
            if url.startswith('/'):
                url = 'https://www.baidu.com' + url
            
            logging.info(f"正在获取页面: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logging.error(f"获取页面失败: {e}")
            return None
    
    def extract_health_info(self, html_content):
        """提取健康页面的信息"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            info = {
                'title': '',
                'doctor': '',
                'position': '',
                'department': ''
            }
            
            # 提取标题
            title_selectors = ['h1', '.title', '.article-title', '.page-title']
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    info['title'] = title_element.get_text(strip=True)
                    break
            
            if not info['title']:
                info['title'] = "未找到标题"
            
            # 提取医生信息
            doctor_selectors = ['.doctor-name', '.doctor-info .name', '.expert-name', '.author']
            for selector in doctor_selectors:
                doctor_element = soup.select_one(selector)
                if doctor_element:
                    info['doctor'] = doctor_element.get_text(strip=True)
                    break
            
            if not info['doctor']:
                info['doctor'] = "未找到医生信息"
            
            # 提取医生职位
            position_selectors = ['.doctor-title', '.doctor-info .title', '.expert-title', '.position']
            for selector in position_selectors:
                position_element = soup.select_one(selector)
                if position_element:
                    info['position'] = position_element.get_text(strip=True)
                    break
            
            if not info['position']:
                info['position'] = "未找到职位信息"
            
            # 提取科室信息
            dept_selectors = ['.department', '.dept', '.clinic', '.section']
            for selector in dept_selectors:
                dept_element = soup.select_one(selector)
                if dept_element:
                    info['department'] = dept_element.get_text(strip=True)
                    break
            
            if not info['department']:
                info['department'] = "未找到科室信息"
            
            logging.info(f"成功提取信息: {info}")
            return info
            
        except Exception as e:
            logging.error(f"提取健康信息失败: {e}")
            return {
                'title': '提取失败',
                'doctor': '提取失败',
                'position': '提取失败',
                'department': '提取失败'
            }
    
    def scrape_single_title(self, title, max_pages=3):
        """爬取单个标题的信息"""
        try:
            for page in range(1, max_pages + 1):
                # 搜索标题
                html_content = self.search_baidu(title, page)
                if not html_content:
                    continue
                
                # 查找百度健康链接
                health_links = self.find_baidu_health_links(html_content)
                
                if health_links:
                    # 使用第一个找到的链接
                    health_link = health_links[0]
                    
                    # 获取健康页面
                    health_page = self.get_baidu_health_page(health_link['url'])
                    if health_page:
                        # 提取信息
                        info = self.extract_health_info(health_page)
                        info['search_title'] = title
                        info['source_url'] = health_link['url']
                        
                        logging.info(f"成功爬取: {title}")
                        return info
                
                # 如果当前页没找到，继续下一页
                if page < max_pages:
                    time.sleep(2)  # 延迟避免被反爬
            
            logging.warning(f"在{max_pages}页内未找到百度健康结果: {title}")
            return None
            
        except Exception as e:
            logging.error(f"爬取标题'{title}'失败: {e}")
            return None
    
    def save_to_excel(self, data, filename=None):
        """保存结果到Excel文件"""
        try:
            if not filename:
                today = datetime.now().strftime("%Y%m%d")
                filename = f"百度健康爬取结果_{today}.xlsx"
            
            df = pd.DataFrame(data)
            columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'source_url']
            df = df.reindex(columns=columns_order)
            
            df.to_excel(filename, index=False, engine='openpyxl')
            logging.info(f"结果已保存到: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"保存Excel文件失败: {e}")
            return None
    
    def run(self, excel_file, max_titles=10):
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
                
                info = self.scrape_single_title(title)
                if info:
                    self.results.append(info)
                    logging.info(f"成功爬取: {title}")
                else:
                    logging.warning(f"爬取失败: {title}")
                
                # 添加延迟，避免被反爬
                time.sleep(3)
            
            # 保存结果
            if self.results:
                filename = self.save_to_excel(self.results)
                logging.info(f"爬虫程序完成，共爬取{len(self.results)}条数据")
                return filename
            else:
                logging.warning("没有成功爬取到任何数据")
                return None
                
        except Exception as e:
            logging.error(f"爬虫程序运行失败: {e}")
            return None

def main():
    """主函数"""
    try:
        # 查找Excel文件
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
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
        
        # 询问处理数量
        try:
            max_count = int(input("请输入要处理的标题数量（建议不超过10个进行测试）: "))
        except ValueError:
            max_count = 5
            print(f"输入无效，使用默认值: {max_count}")
        
        # 创建爬虫实例并运行
        scraper = BaiduHealthScraper()
        result_file = scraper.run(selected_file, max_titles=max_count)
        
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
