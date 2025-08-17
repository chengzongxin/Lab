#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome错误处理配置文件
解决常见的Chrome浏览器错误和警告
"""

# Chrome启动参数配置
CHROME_OPTIONS = {
    # 基础配置
    'basic': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-software-rasterizer'
    ],
    
    # 禁用GCM和相关服务
    'disable_services': [
        '--disable-gcm',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-extensions',
        '--disable-sync',
        '--disable-translate',
        '--metrics-recording-only',
        '--no-first-run',
        '--safebrowsing-disable-auto-update',
        '--disable-component-update',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding'
    ],
    
    # 性能优化
    'performance': [
        '--memory-pressure-off',
        '--max_old_space_size=4096',
        '--disable-features=VizDisplayCompositor',
        '--disable-ipc-flooding-protection'
    ],
    
    # 网络配置
    'network': [
        '--disable-web-security',
        '--allow-running-insecure-content',
        '--disable-features=VizDisplayCompositor'
    ],
    
    # 日志控制
    'logging': [
        '--log-level=3',
        '--silent',
        '--disable-logging',
        '--disable-in-process-stack-traces'
    ]
}

# 错误处理策略
ERROR_HANDLING = {
    'max_retries': 3,
    'retry_delay': 3,
    'cleanup_on_failure': True,
    'log_errors': True
}

# 常见错误模式
ERROR_PATTERNS = {
    'gcm_error': 'google_apis\\gcm\\engine\\connection_factory_impl.cc',
    'network_error': 'net error: -2',
    'chrome_crash': 'chrome_crashpad_handler',
    'gpu_error': 'GPU process crashed'
}

# 错误修复建议
ERROR_FIXES = {
    'gcm_error': [
        '添加 --disable-gcm 参数',
        '添加 --disable-background-networking 参数',
        '检查网络连接',
        '更新Chrome版本'
    ],
    'network_error': [
        '检查防火墙设置',
        '检查代理配置',
        '增加重试次数',
        '使用备用网络'
    ],
    'chrome_crash': [
        '更新ChromeDriver',
        '检查Chrome版本兼容性',
        '增加内存限制',
        '禁用GPU加速'
    ]
}

def get_chrome_options(category='all'):
    """获取Chrome启动参数"""
    if category == 'all':
        all_options = []
        for options_list in CHROME_OPTIONS.values():
            all_options.extend(options_list)
        return all_options
    elif category in CHROME_OPTIONS:
        return CHROME_OPTIONS[category]
    else:
        return []

def get_error_fix_suggestions(error_type):
    """获取错误修复建议"""
    return ERROR_FIXES.get(error_type, ['未知错误类型'])

def is_known_error(error_message):
    """判断是否为已知错误"""
    for pattern in ERROR_PATTERNS.values():
        if pattern in error_message:
            return True
    return False
