#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医生主页爬虫脚本 V2.0
功能：爬取百度健康医生列表，获取医生个人主页URL
改进：使用配置文件、增加重试机制、更好的错误处理
作者：AI助手
"""

import requests
import json
import time
import random
import uuid
from urllib.parse import urlencode
from typing import List, Dict, Optional, Tuple
import logging
from config import *

class DoctorScraperV2:
    """医生爬虫类 V2.0"""
    
    def __init__(self, use_config: bool = True):
        """
        初始化爬虫
        
        Args:
            use_config: 是否使用配置文件
        """
        if use_config:
            self._init_from_config()
        else:
            self._init_default()
        
        # 请求会话，保持连接
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': time.time()
        }
    
    def _init_from_config(self):
        """从配置文件初始化"""
        self.headers = HEADERS.copy()
        self.base_urls = URLS.copy()
        self.request_params = REQUEST_PARAMS.copy()
        self.author_config = AUTHOR_HOME_CONFIG.copy()
        self.search_config = SEARCH_CONFIG.copy()
        self.anti_crawl_config = ANTI_CRAWL_CONFIG.copy()
        self.output_config = OUTPUT_CONFIG.copy()
        
        # 日志配置
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file_handler'], 
                                 encoding=LOGGING_CONFIG['encoding']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_default(self):
        """使用默认配置初始化"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://jiankang.baidu.com/',
        }
        self.base_urls = {
            'expert_list': 'https://jiankang.baidu.com/wzcui/uiservice/expert/expertlist',
            'doctor_home': 'https://jiankang.baidu.com/decision/pages/expert/newHome/index',
            'author_home': 'https://author.baidu.com/home'
        }
        self.request_params = {}
        self.author_config = {}
        self.search_config = {'delay_range': (1, 3)}
        self.anti_crawl_config = {'timeout': 30, 'max_retries': 3}
        self.output_config = {}
        
        # 简单日志配置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _random_delay(self):
        """随机延迟，避免被反爬"""
        delay = random.uniform(*self.search_config['delay_range'])
        self.logger.info(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
    
    def _make_request(self, url: str, params: Dict = None, method: str = 'GET', 
                     retries: int = None) -> Optional[requests.Response]:
        """
        发送HTTP请求，带重试机制
        
        Args:
            url: 请求URL
            params: 请求参数
            method: 请求方法
            retries: 重试次数
            
        Returns:
            HTTP响应对象或None
        """
        if retries is None:
            retries = self.anti_crawl_config['max_retries']
        
        for attempt in range(retries + 1):
            try:
                self.stats['total_requests'] += 1
                
                if method.upper() == 'GET':
                    response = self.session.get(
                        url, 
                        params=params, 
                        timeout=self.anti_crawl_config['timeout']
                    )
                else:
                    response = self.session.post(
                        url, 
                        params=params, 
                        timeout=self.anti_crawl_config['timeout']
                    )
                
                response.raise_for_status()
                self.stats['successful_requests'] += 1
                return response
                
            except requests.exceptions.RequestException as e:
                self.stats['failed_requests'] += 1
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/{retries + 1}): {e}")
                
                if attempt < retries:
                    wait_time = self.anti_crawl_config['retry_delay'] * (2 ** attempt)
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"请求最终失败: {url}")
                    return None
        
        return None
    
    def get_doctor_list(self, 
                        search_keyword: str = None,
                        page: int = 1, 
                        page_size: int = None,
                        **kwargs) -> List[Dict]:
        """
        获取医生列表
        
        Args:
            search_keyword: 搜索关键词（科室名称）
            page: 页码
            page_size: 每页数量
            **kwargs: 其他参数
            
        Returns:
            医生列表数据
        """
        if search_keyword is None:
            search_keyword = self.search_config['default_keyword']
        if page_size is None:
            page_size = self.search_config['page_size']
            
        self.logger.info(f"正在获取第 {page} 页医生列表，关键词：{search_keyword}")
        
        # 构建请求参数
        params = self.request_params.copy()
        params.update({
            'page': page,
            'pageSize': page_size,
            'search': search_keyword,
            'word': search_keyword,
            'applid': str(random.randint(1000000000, 9999999999)),
            'reqId': self._generate_req_id(),
        })
        
        # 更新其他参数
        params.update(kwargs)
        
        # 发送请求
        response = self._make_request(self.base_urls['expert_list'], params)
        if not response:
            return []
        
        try:
            # 解析响应
            data = response.json()
            
            if data.get('status') == 0 and 'data' in data:
                experts = data['data'].get('list', [])
                expert_data = []
                
                for expert in experts:
                    if expert.get('type') == 'expert':
                        expert_info = expert['data']
                        expert_data.append({
                            'expert_id': expert_info.get('expertId'),
                            'doc_id': expert_info.get('docId'),
                            'name': expert_info.get('expertName'),
                            'level': expert_info.get('expertLevel'),
                            'hospital': expert_info.get('expertHospital'),
                            'department': expert_info.get('expertDepartment'),
                            'good_at': expert_info.get('expertGoodAt', []),
                            'pic': expert_info.get('expertPic'),
                            'core_id': expert_info.get('coreId')
                        })
                
                self.logger.info(f"成功获取 {len(expert_data)} 位医生信息")
                return expert_data
            else:
                self.logger.error(f"获取医生列表失败：{data.get('msg', '未知错误')}")
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"解析医生列表JSON失败：{e}")
            return []
    
    def build_doctor_home_url(self, doc_id: str) -> str:
        """
        构建医生百度健康页面URL
        
        Args:
            doc_id: 医生文档ID
            
        Returns:
            完整的医生健康页面URL
        """
        params = {'doc_id': doc_id}
        url = f"{self.base_urls['doctor_home']}?{urlencode(params)}"
        self.logger.info(f"构建医生健康页面URL：{url}")
        return url
    
    def get_doctor_author_home(self, doc_id: str, expert_id: str) -> Optional[str]:
        """
        获取医生个人主页URL
        
        Args:
            doc_id: 医生文档ID
            expert_id: 医生专家ID
            
        Returns:
            医生个人主页URL
        """
        self.logger.info(f"正在获取医生 {expert_id} 的个人主页")
        
        # 构建请求参数
        context = self.author_config.get('context', {
            "from": "expert_home_share",
            "app_id": "1698259672647465"
        })
        
        params = {
            'context': json.dumps(context, ensure_ascii=False),
            'lid': str(random.randint(1000000000, 9999999999)),
            'referlid': str(random.randint(1000000000, 9999999999))
        }
        
        # 发送请求
        response = self._make_request(self.base_urls['author_home'], params)
        if not response:
            return None
        
        # 检查是否成功
        if response.status_code == 200:
            final_url = response.url
            self.logger.info(f"成功获取医生个人主页：{final_url}")
            return final_url
        else:
            self.logger.error(f"获取医生个人主页失败，状态码：{response.status_code}")
            return None
    
    def _generate_req_id(self) -> str:
        """生成请求ID"""
        return str(uuid.uuid4()).replace('-', '')
    
    def scrape_doctors(self, 
                      search_keyword: str = None,
                      max_pages: int = None,
                      page_size: int = None) -> List[Dict]:
        """
        完整的爬取流程
        
        Args:
            search_keyword: 搜索关键词
            max_pages: 最大爬取页数
            page_size: 每页数量
            
        Returns:
            包含完整信息的医生列表
        """
        if search_keyword is None:
            search_keyword = self.search_config['default_keyword']
        if max_pages is None:
            max_pages = self.search_config['max_pages']
        if page_size is None:
            page_size = self.search_config['page_size']
            
        self.logger.info(f"开始爬取，关键词：{search_keyword}，最大页数：{max_pages}")
        
        all_doctors = []
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"开始爬取第 {page} 页")
            
            # 获取医生列表
            doctors = self.get_doctor_list(
                search_keyword=search_keyword,
                page=page,
                page_size=page_size
            )
            
            if not doctors:
                self.logger.warning(f"第 {page} 页没有获取到医生数据，停止爬取")
                break
            
            # 为每个医生获取详细信息
            for doctor in doctors:
                self.logger.info(f"正在处理医生：{doctor['name']}")
                
                # 构建健康页面URL
                doctor['health_page_url'] = self.build_doctor_home_url(doctor['doc_id'])
                
                # 获取个人主页URL
                if doctor.get('expert_id'):
                    doctor['author_home_url'] = self.get_doctor_author_home(
                        doctor['doc_id'], 
                        doctor['expert_id']
                    )
                
                # 添加延迟
                self._random_delay()
                
                all_doctors.append(doctor)
            
            self.logger.info(f"第 {page} 页爬取完成，当前共 {len(all_doctors)} 位医生")
            
            # 页面间延迟
            if page < max_pages:
                delay = random.uniform(*self.search_config.get('page_delay_range', (2, 5)))
                self.logger.info(f"页面间等待 {delay:.2f} 秒...")
                time.sleep(delay)
        
        return all_doctors
    
    def save_results(self, doctors: List[Dict], filename: str = None):
        """
        保存爬取结果
        
        Args:
            doctors: 医生数据列表
            filename: 保存文件名
        """
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = self.output_config.get('default_filename', 'doctors_{timestamp}.json')
            filename = filename.format(timestamp=timestamp)
        
        try:
            with open(filename, 'w', encoding=self.output_config.get('encoding', 'utf-8')) as f:
                json.dump(doctors, f, 
                         ensure_ascii=self.output_config.get('ensure_ascii', False),
                         indent=self.output_config.get('indent', 2))
            self.logger.info(f"结果已保存到：{filename}")
        except Exception as e:
            self.logger.error(f"保存结果失败：{e}")
    
    def get_statistics(self) -> Dict:
        """获取爬取统计信息"""
        end_time = time.time()
        duration = end_time - self.stats['start_time']
        
        stats = self.stats.copy()
        stats.update({
            'duration_seconds': duration,
            'duration_minutes': duration / 60,
            'success_rate': (self.stats['successful_requests'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
        })
        
        return stats
    
    def print_statistics(self):
        """打印爬取统计信息"""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("爬取统计信息")
        print("="*50)
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"失败请求: {stats['failed_requests']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"总耗时: {stats['duration_minutes']:.2f} 分钟")
        print("="*50)


def main():
    """主函数"""
    print("医生爬虫脚本 V2.0")
    print("="*50)
    
    # 创建爬虫实例
    scraper = DoctorScraperV2(use_config=True)
    
    try:
        # 执行爬取
        doctors = scraper.scrape_doctors(
            search_keyword="妇产科",  # 可以修改为其他科室
            max_pages=2,             # 爬取页数
            page_size=10             # 每页数量
        )
        
        if doctors:
            print(f"\n爬取完成，共获取 {len(doctors)} 位医生信息")
            
            # 保存结果
            scraper.save_results(doctors)
            
            # 打印部分结果
            print("\n前3位医生信息预览：")
            for i, doctor in enumerate(doctors[:3], 1):
                print(f"\n医生 {i}:")
                print(f"  姓名: {doctor['name']}")
                print(f"  级别: {doctor['level']}")
                print(f"  医院: {doctor['hospital']}")
                print(f"  科室: {doctor['department']}")
                print(f"  健康页面: {doctor.get('health_page_url', 'N/A')}")
                print(f"  个人主页: {doctor.get('author_home_url', 'N/A')}")
        else:
            print("没有获取到医生数据")
            
    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"\n爬取过程中发生错误：{e}")
    
    # 打印统计信息
    scraper.print_statistics()
    print("\n爬虫脚本运行结束")


if __name__ == "__main__":
    main()
