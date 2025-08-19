#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理和重连配置
用于处理浏览器连接问题和自动重连
"""

# 连接错误关键词列表
CONNECTION_ERROR_KEYWORDS = [
    'invalid session id',
    'session id', 
    'connection reset',
    'remote host',
    'chrome not reachable',
    'chrome failed',
    'no such session',
    'session deleted',
    'session not created',
    'timeout',
    'connection refused',
    'connection aborted',
    'broken pipe',
    'webdriver exception'
]

# 重连配置
RECONNECT_CONFIG = {
    'max_retries': 3,           # 最大重试次数
    'retry_delay': 2,           # 重试间隔（秒）
    'health_check_interval': 5, # 健康检查间隔（秒）
    'connection_timeout': 30,   # 连接超时时间（秒）
}

# 浏览器健康检查命令
HEALTH_CHECK_COMMANDS = [
    "return navigator.userAgent;",
    "return document.readyState;",
    "return window.location.href;"
]

# 错误恢复策略
ERROR_RECOVERY_STRATEGIES = {
    'connection_lost': 'reconnect',      # 连接丢失：重连
    'session_expired': 'reconnect',      # 会话过期：重连
    'page_timeout': 'refresh',           # 页面超时：刷新
    'element_not_found': 'retry',        # 元素未找到：重试
    'verification_required': 'wait',     # 需要验证：等待
    'rate_limited': 'delay',             # 被限流：延迟
}

# 智能延迟配置
SMART_DELAY_CONFIG = {
    'base_delay': 1,            # 基础延迟（秒）
    'max_delay': 5,             # 最大延迟（秒）
    'error_multiplier': 2,      # 错误时延迟倍数
    'success_reduction': 0.8,   # 成功时延迟减少比例
}

# 日志配置
LOGGING_CONFIG = {
    'connection_errors': 'WARNING',      # 连接错误日志级别
    'reconnect_attempts': 'INFO',       # 重连尝试日志级别
    'health_checks': 'DEBUG',           # 健康检查日志级别
    'error_recovery': 'INFO',           # 错误恢复日志级别
}

# 浏览器启动参数（用于重连时）
CHROME_RESTART_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gcm',
    '--disable-background-networking',
    '--disable-default-apps',
    '--disable-extensions',
    '--disable-sync',
    '--disable-translate',
    '--metrics-recording-only',
    '--no-first-run',
    '--safebrowsing-disable-auto-update',
    '--disable-blink-features=AutomationControlled',
    '--window-size=1920,1080'
]

# 用户代理列表（用于重连时轮换）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
]

# 错误消息映射
ERROR_MESSAGE_MAP = {
    'invalid session id': '浏览器会话已失效，需要重新连接',
    'connection reset': '网络连接被重置，可能是网络不稳定',
    'chrome not reachable': 'Chrome浏览器无法访问，可能已崩溃',
    'session deleted': '浏览器会话已被删除',
    'timeout': '操作超时，网络可能较慢',
    'connection refused': '连接被拒绝，端口可能被占用',
    'element not found': '页面元素未找到，页面可能未完全加载',
    'verification required': '需要人工验证，请手动处理'
}

# 重连成功后的验证步骤
RECONNECT_VERIFICATION_STEPS = [
    'check_driver_exists',      # 检查驱动是否存在
    'check_browser_accessible', # 检查浏览器是否可访问
    'check_page_loadable',      # 检查页面是否可加载
    'check_element_findable'    # 检查元素是否可查找
]

# 错误恢复后的清理操作
ERROR_RECOVERY_CLEANUP = [
    'clear_browser_cache',      # 清理浏览器缓存
    'reset_page_state',         # 重置页面状态
    'clear_error_logs',         # 清理错误日志
    'reset_retry_counters'      # 重置重试计数器
]
