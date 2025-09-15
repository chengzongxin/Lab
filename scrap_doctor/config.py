#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置文件
包含各种可配置的参数
"""

# 搜索配置
SEARCH_CONFIG = {
    'default_keyword': '妇产科',  # 默认搜索关键词
    'max_pages': 3,              # 最大爬取页数
    'page_size': 20,             # 每页数量
    'delay_range': (1, 3),       # 请求间隔范围（秒）
    'page_delay_range': (2, 5),  # 页面间延迟范围（秒）
}

# 请求头配置
HEADERS = {
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

# URL配置
URLS = {
    'expert_list': 'https://jiankang.baidu.com/wzcui/uiservice/expert/expertlist',
    'doctor_home': 'https://jiankang.baidu.com/decision/pages/expert/newHome/index',
    'author_home': 'https://author.baidu.com/home'
}

# 请求参数配置
REQUEST_PARAMS = {
    'from_sf': 1,
    'need_tab': 1,
    'openapi': 1,
    'pd': 'med',
    'ref': 'feed_bjh_yszy',
    'search_channel': 'wz',
    'search_mode': 'res',
    'search_section': 'all',
    'sf_ref': 'feed_bjh_yszy',
    'tpl': 'feed_wenzhen',
    'vn': 'med',
    'version': 'bannerCard',
    'clientName': 'h5',
}

# 医生主页配置
AUTHOR_HOME_CONFIG = {
    'context': {
        "from": "expert_home_share",
        "app_id": "1698259672647465"
    }
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_handler': 'scraper.log',
    'encoding': 'utf-8'
}

# 输出配置
OUTPUT_CONFIG = {
    'default_filename': 'doctors_{timestamp}.json',
    'encoding': 'utf-8',
    'indent': 2,
    'ensure_ascii': False
}

# 反爬配置
ANTI_CRAWL_CONFIG = {
    'timeout': 30,           # 请求超时时间
    'max_retries': 3,        # 最大重试次数
    'retry_delay': 5,        # 重试延迟（秒）
    'use_proxy': False,      # 是否使用代理
    'proxy_list': [],        # 代理列表
}

# 科室关键词列表（可以扩展）
DEPARTMENT_KEYWORDS = [
    '妇产科',
    '内科',
    '外科',
    '儿科',
    '骨科',
    '眼科',
    '口腔科',
    '皮肤科',
    '神经科',
    '心血管科',
    '消化科',
    '呼吸科',
    '泌尿科',
    '肿瘤科',
    '急诊科',
    '康复科',
    '中医科',
    '精神科',
    '感染科',
    '风湿免疫科'
]
