#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医生主页爬虫脚本
功能：爬取百度健康医生列表，获取医生个人主页URL
作者：AI助手
"""

import requests
import json
import time
import random
from urllib.parse import urlencode, quote
from typing import List, Dict, Optional
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
logger = logging.getLogger(__name__)

class DoctorScraper:
    """医生爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        # 设置请求头，模拟真实浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://jiankang.baidu.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        # 基础URL配置
        self.base_urls = {
            'expert_list': 'https://jiankang.baidu.com/wzcui/uiservice/expert/expertlist',
            'doctor_home': 'https://jiankang.baidu.com/decision/pages/expert/newHome/index',
            'author_home': 'https://author.baidu.com/home'
        }
        
        # 请求会话，保持连接
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 添加随机延迟，避免被反爬
        self.delay_range = (1, 3)
    
    def _random_delay(self):
        """随机延迟，避免被反爬"""
        delay = random.uniform(*self.delay_range)
        logger.info(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
    
    def get_doctor_list(self, 
                        search_keyword: str = "妇产科",
                        page: int = 1, 
                        page_size: int = 20,
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
        logger.info(f"正在获取第 {page} 页医生列表，关键词：{search_keyword}")
        
        # 构建请求参数
        params = {
            'from_sf': 1,
            'need_tab': 1,
            'openapi': 1,
            'page': page,
            'pageSize': page_size,
            'pd': 'med',
            'ref': 'feed_bjh_yszy',
            'search': search_keyword,
            'search_channel': 'wz',
            'search_mode': 'res',
            'search_section': 'all',
            'sf_ref': 'feed_bjh_yszy',
            'tpl': 'feed_wenzhen',
            'vn': 'med',
            'word': search_keyword,
            'version': 'bannerCard',
            'clientName': 'h5',
            'applid': str(random.randint(1000000000, 9999999999)),  # 随机生成
            'reqId': self._generate_req_id(),  # 生成请求ID
        }
        
        # 更新其他参数
        params.update(kwargs)
        
        try:
            # 发送请求
            response = self.session.get(
                self.base_urls['expert_list'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
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
                            'pic': expert_info.get('expertPic')
                        })
                
                logger.info(f"成功获取 {len(expert_data)} 位医生信息")
                return expert_data
            else:
                logger.error(f"获取医生列表失败：{data.get('msg', '未知错误')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求医生列表失败：{e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"解析医生列表JSON失败：{e}")
            return []
    
    def build_doctor_home_url(self, doc_id: str) -> str:
        """
        构建医生百度健康页面URL
        
        Args:
            doc_id: 医生文档ID
            
        Returns:
            完整的医生健康页面URL
        """
        params = {
            'doc_id': doc_id
        }
        
        url = f"{self.base_urls['doctor_home']}?{urlencode(params)}"
        logger.info(f"构建医生健康页面URL：{url}")
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
        logger.info(f"正在获取医生 {expert_id} 的个人主页")
        
        # 构建请求参数
        context = {
            "from": "expert_home_share",
            "app_id": "1698259672647465"
        }
        
        params = {
            'context': json.dumps(context, ensure_ascii=False),
            'lid': str(random.randint(1000000000, 9999999999)),
            'referlid': str(random.randint(1000000000, 9999999999))
        }
        
        try:
            # 发送请求获取医生主页
            response = self.session.get(
                self.base_urls['author_home'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # 检查是否成功跳转
            if response.status_code == 200:
                # 这里可能需要进一步处理，因为可能需要跟随重定向
                final_url = response.url
                logger.info(f"成功获取医生个人主页：{final_url}")
                return final_url
            else:
                logger.error(f"获取医生个人主页失败，状态码：{response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求医生个人主页失败：{e}")
            return None
    
    def _generate_req_id(self) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4()).replace('-', '')
    
    def scrape_doctors(self, 
                      search_keyword: str = "妇产科",
                      max_pages: int = 3,
                      page_size: int = 20) -> List[Dict]:
        """
        完整的爬取流程
        
        Args:
            search_keyword: 搜索关键词
            max_pages: 最大爬取页数
            page_size: 每页数量
            
        Returns:
            包含完整信息的医生列表
        """
        all_doctors = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"开始爬取第 {page} 页")
            
            # 获取医生列表
            doctors = self.get_doctor_list(
                search_keyword=search_keyword,
                page=page,
                page_size=page_size
            )
            
            if not doctors:
                logger.warning(f"第 {page} 页没有获取到医生数据，停止爬取")
                break
            
            # 为每个医生获取详细信息
            for doctor in doctors:
                logger.info(f"正在处理医生：{doctor['name']}")
                
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
            
            logger.info(f"第 {page} 页爬取完成，当前共 {len(all_doctors)} 位医生")
            
            # 页面间延迟
            if page < max_pages:
                time.sleep(random.uniform(2, 5))
        
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
            filename = f"doctors_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(doctors, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存到：{filename}")
        except Exception as e:
            logger.error(f"保存结果失败：{e}")


def main():
    """主函数"""
    logger.info("开始运行医生爬虫脚本")
    
    # 创建爬虫实例
    scraper = DoctorScraper()
    
    try:
        # 执行爬取
        doctors = scraper.scrape_doctors(
            search_keyword="妇产科",  # 可以修改为其他科室
            max_pages=2,             # 爬取页数
            page_size=10             # 每页数量
        )
        
        if doctors:
            logger.info(f"爬取完成，共获取 {len(doctors)} 位医生信息")
            
            # 保存结果
            scraper.save_results(doctors)
            
            # 打印部分结果
            for i, doctor in enumerate(doctors[:3], 1):
                print(f"\n医生 {i}:")
                print(f"  姓名: {doctor['name']}")
                print(f"  级别: {doctor['level']}")
                print(f"  医院: {doctor['hospital']}")
                print(f"  科室: {doctor['department']}")
                print(f"  健康页面: {doctor.get('health_page_url', 'N/A')}")
                print(f"  个人主页: {doctor.get('author_home_url', 'N/A')}")
        else:
            logger.warning("没有获取到医生数据")
            
    except KeyboardInterrupt:
        logger.info("用户中断爬取")
    except Exception as e:
        logger.error(f"爬取过程中发生错误：{e}")
    
    logger.info("爬虫脚本运行结束")


if __name__ == "__main__":
    main()
