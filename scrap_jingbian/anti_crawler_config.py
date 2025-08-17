#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反爬虫配置文件
包含各种反爬虫策略的参数设置
"""

# 延迟策略配置
DELAY_CONFIG = {
    'min_search_delay': 3,      # 搜索后最小延迟（秒）
    'max_search_delay': 6,      # 搜索后最大延迟（秒）
    'min_page_delay': 2,        # 翻页后最小延迟（秒）
    'max_page_delay': 4,        # 翻页后最大延迟（秒）
    'min_title_delay': 5,       # 标题间最小延迟（秒）
    'max_title_delay': 10,      # 标题间最大延迟（秒）
    'extra_delay_interval': 5,  # 每处理多少个标题后增加额外延迟
    'extra_delay_min': 10,      # 额外延迟最小值（秒）
    'extra_delay_max': 20,      # 额外延迟最大值（秒）
}

# 用户代理配置
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
]

# 验证检测关键词
VERIFICATION_KEYWORDS = [
    "验证码",
    "滑块验证", 
    "人机验证",
    "安全验证",
    "verify",
    "captcha",
    "安全检测",
    "请验证",
    "拖动滑块"
]

# 浏览器配置
BROWSER_CONFIG = {
    'window_size': '1920,1080',
    'disable_automation': True,
    'disable_blink_features': True,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
}

# 代理配置（可选）
PROXY_CONFIG = {
    'enabled': False,
    'proxy_list': [
        # 在这里添加代理服务器列表
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ],
    'rotate_interval': 10,  # 每处理多少个请求后轮换代理
}

# 会话管理配置
SESSION_CONFIG = {
    'max_requests_per_session': 50,  # 每个会话最大请求数
    'session_timeout': 3600,         # 会话超时时间（秒）
    'restart_interval': 30,          # 每处理多少个标题后重启浏览器
}
