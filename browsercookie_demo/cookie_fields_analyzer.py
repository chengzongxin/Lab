import requests
import browsercookie
from urllib.parse import urlparse
import inspect

def get_complete_cookie_info(website_url):
    """
    获取指定网站的完整cookie信息，包括所有字段
    
    参数:
        website_url (str): 要获取cookie的网站URL
    
    返回:
        dict: 包含该网站所有cookie的完整信息
    """
    # 获取Chrome浏览器的所有cookie
    all_cookies = browsercookie.chrome()
    
    # 解析URL以获取域名
    parsed_url = urlparse(website_url)
    domain = parsed_url.netloc
    
    # 过滤出特定网站的cookie
    website_cookies = {}
    
    for cookie in all_cookies:
        # 检查cookie是否属于目标网站
        if domain in cookie.domain or cookie.domain in domain:
            # 获取cookie的所有属性
            cookie_info = {}
            
            # 基本属性
            cookie_info['name'] = cookie.name
            cookie_info['value'] = cookie.value
            cookie_info['domain'] = cookie.domain
            cookie_info['path'] = cookie.path
            
            # 时间相关属性
            cookie_info['expires'] = cookie.expires
            cookie_info['expires_date'] = None
            if cookie.expires:
                try:
                    import datetime
                    cookie_info['expires_date'] = datetime.datetime.fromtimestamp(cookie.expires)
                except:
                    pass
            
            # 安全相关属性
            cookie_info['secure'] = cookie.secure
            cookie_info['http_only'] = getattr(cookie, 'has_nonstandard_attr', lambda x: False)('HttpOnly')
            
            # 尝试获取其他可能的属性
            possible_attrs = [
                'maxAge', 'comment', 'version', 'sameSite', 'discard',
                'comment_url', 'rfc2109', 'rest', 'port', 'port_specified',
                'domain_specified', 'domain_initial_dot', 'path_specified'
            ]
            
            for attr in possible_attrs:
                if hasattr(cookie, attr):
                    try:
                        cookie_info[attr] = getattr(cookie, attr)
                    except:
                        cookie_info[attr] = "无法获取"
            
            # 获取cookie对象的所有属性（包括私有属性）
            all_attrs = {}
            for attr_name in dir(cookie):
                if not attr_name.startswith('_') and not callable(getattr(cookie, attr_name)):
                    try:
                        all_attrs[attr_name] = getattr(cookie, attr_name)
                    except:
                        all_attrs[attr_name] = "无法获取"
            
            cookie_info['all_attributes'] = all_attrs
            
            website_cookies[cookie.name] = cookie_info
    
    return website_cookies

def print_cookie_fields_info(cookies_dict, website_name):
    """
    格式化打印cookie的完整字段信息
    
    参数:
        cookies_dict (dict): cookie字典
        website_name (str): 网站名称
    """
    print(f"\n=== {website_name} 的完整Cookie字段信息 ===")
    print(f"总共找到 {len(cookies_dict)} 个cookie\n")
    
    for cookie_name, cookie_info in cookies_dict.items():
        print(f"🍪 Cookie名称: {cookie_name}")
        print(f"   值: {cookie_info['value']}")
        print(f"   域名: {cookie_info['domain']}")
        print(f"   路径: {cookie_info['path']}")
        
        # 时间信息
        if cookie_info['expires']:
            print(f"   过期时间戳: {cookie_info['expires']}")
            if cookie_info['expires_date']:
                print(f"   过期日期: {cookie_info['expires_date']}")
        else:
            print(f"   过期时间: 会话cookie（浏览器关闭时过期）")
        
        # 安全信息
        print(f"   安全传输: {cookie_info['secure']}")
        print(f"   HttpOnly: {cookie_info['http_only']}")
        
        # 其他属性
        for attr, value in cookie_info.items():
            if attr not in ['name', 'value', 'domain', 'path', 'expires', 'expires_date', 'secure', 'http_only', 'all_attributes']:
                if value is not None and value != "无法获取":
                    print(f"   {attr}: {value}")
        
        print("-" * 60)

def explain_cookie_fields():
    """
    解释cookie各个字段的含义
    """
    print("\n=== Cookie字段详解 ===")
    
    fields_explanation = {
        'name': 'Cookie的名称，用于标识不同的cookie',
        'value': 'Cookie的值，存储的实际数据',
        'domain': 'Cookie所属的域名，决定哪些网站可以访问此cookie',
        'path': 'Cookie的路径，决定哪些页面可以访问此cookie',
        'expires': 'Cookie的过期时间戳，None表示会话cookie',
        'secure': '是否只在HTTPS连接下发送cookie',
        'http_only': '是否只能通过HTTP访问，防止JavaScript访问',
        'maxAge': 'Cookie的最大存活时间（秒）',
        'comment': 'Cookie的注释信息',
        'version': 'Cookie的版本号',
        'sameSite': '同站策略，控制跨站请求时是否发送cookie',
        'discard': '是否在会话结束时丢弃',
        'comment_url': '注释的URL',
        'rfc2109': '是否遵循RFC 2109标准',
        'rest': '其他属性',
        'port': 'Cookie的端口号',
        'port_specified': '是否指定了端口号',
        'domain_specified': '是否指定了域名',
        'domain_initial_dot': '域名是否以点开头',
        'path_specified': '是否指定了路径'
    }
    
    for field, explanation in fields_explanation.items():
        print(f"• {field}: {explanation}")

def get_http_request_cookies(cookies_dict):
    """
    获取用于HTTP请求的cookie（只包含必要的字段）
    
    参数:
        cookies_dict (dict): 完整的cookie字典
    
    返回:
        dict: 只包含name和value的cookie字典
    """
    http_cookies = {}
    for name, info in cookies_dict.items():
        http_cookies[name] = info['value']
    return http_cookies

def analyze_cookie_importance(cookies_dict):
    """
    分析cookie字段的重要性
    
    参数:
        cookies_dict (dict): cookie字典
    """
    print("\n=== Cookie字段重要性分析 ===")
    
    importance_levels = {
        'essential': ['name', 'value'],  # HTTP请求必需
        'important': ['domain', 'path', 'expires', 'secure', 'http_only'],  # 安全和控制
        'optional': ['maxAge', 'comment', 'version', 'sameSite', 'discard']  # 额外信息
    }
    
    for level, fields in importance_levels.items():
        print(f"\n{level.upper()} 字段:")
        for field in fields:
            found_count = sum(1 for cookie in cookies_dict.values() if field in cookie and cookie[field] is not None)
            print(f"  • {field}: {found_count} 个cookie包含此字段")

# 示例使用
if __name__ == "__main__":
    # 获取TAPD网站的完整cookie信息
    target_website = "https://www.tapd.cn"
    complete_cookies = get_complete_cookie_info(target_website)
    
    # 解释cookie字段
    explain_cookie_fields()
    
    # 打印完整信息
    print_cookie_fields_info(complete_cookies, "TAPD")
    
    # 分析字段重要性
    analyze_cookie_importance(complete_cookies)
    
    # 获取HTTP请求用的cookie
    http_cookies = get_http_request_cookies(complete_cookies)
    print(f"\n=== HTTP请求用的Cookie（简化版）===")
    print(f"包含 {len(http_cookies)} 个cookie，只包含name和value字段")
    
    # 测试HTTP请求
    if http_cookies:
        print("\n=== 测试HTTP请求 ===")
        url = "https://www.tapd.cn/tapd_fe/41168903/iteration/card/1141168903001000090?q=7b8f936ecba99815da046deb8b75a458"
        
        try:
            response = requests.get(url, cookies=http_cookies, timeout=10)
            print(f"请求状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.text)} 字符")
            
            if response.status_code == 200:
                print("✅ 请求成功！")
            else:
                print(f"❌ 请求失败")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print(f"\n=== 总结 ===")
    print("1. Cookie包含很多字段，但HTTP请求只需要name和value")
    print("2. 其他字段主要用于安全控制、过期时间等")
    print("3. 不同浏览器和网站可能使用不同的字段")
    print("4. 建议根据实际需要选择合适的字段") 