import requests
import browsercookie
from urllib.parse import urlparse

def get_specific_website_cookies(website_url):
    """
    获取特定网站的cookie
    
    参数:
        website_url (str): 要获取cookie的网站URL
    
    返回:
        dict: 包含该网站所有cookie的字典
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
            website_cookies[cookie.name] = {
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires,
                'secure': cookie.secure,
                'http_only': getattr(cookie, 'has_nonstandard_attr', lambda x: False)('HttpOnly')
            }
    
    return website_cookies

def cookies_to_string(cookies_dict):
    """
    将cookie字典转换为F12格式的字符串
    
    参数:
        cookies_dict (dict): cookie字典
    
    返回:
        str: 类似F12中显示的cookie字符串
    """
    cookie_pairs = []
    for name, info in cookies_dict.items():
        if isinstance(info, dict):
            # 如果是详细格式，取value
            cookie_pairs.append(f"{name}={info['value']}")
        else:
            # 如果是简单格式，直接使用
            cookie_pairs.append(f"{name}={info}")
    
    return "; ".join(cookie_pairs)

def string_to_cookies(cookie_string):
    """
    将F12格式的cookie字符串转换为字典
    
    参数:
        cookie_string (str): 类似F12中显示的cookie字符串
    
    返回:
        dict: cookie字典
    """
    cookies = {}
    if not cookie_string:
        return cookies
    
    # 按分号和空格分割
    cookie_pairs = cookie_string.split("; ")
    
    for pair in cookie_pairs:
        if "=" in pair:
            name, value = pair.split("=", 1)  # 最多分割一次，避免值中有=号
            cookies[name] = value
    
    return cookies

def compare_cookies(f12_cookies, browser_cookies):
    """
    比较F12和browsercookie获取的cookie差异
    
    参数:
        f12_cookies (dict): F12获取的cookie
        browser_cookies (dict): browsercookie获取的cookie
    
    返回:
        dict: 差异分析结果
    """
    f12_names = set(f12_cookies.keys())
    browser_names = set(browser_cookies.keys())
    
    only_in_f12 = f12_names - browser_names
    only_in_browser = browser_names - f12_names
    common = f12_names & browser_names
    
    return {
        'only_in_f12': list(only_in_f12),
        'only_in_browser': list(only_in_browser),
        'common': list(common),
        'f12_count': len(f12_cookies),
        'browser_count': len(browser_cookies),
        'common_count': len(common)
    }

def print_cookies_info(cookies_dict, website_name):
    """
    格式化打印cookie信息
    
    参数:
        cookies_dict (dict): cookie字典
        website_name (str): 网站名称
    """
    print(f"\n=== {website_name} 的Cookie信息 ===")
    print(f"总共找到 {len(cookies_dict)} 个cookie\n")
    
    for cookie_name, cookie_info in cookies_dict.items():
        print(f"Cookie名称: {cookie_name}")
        print(f"  值: {cookie_info['value']}")
        print(f"  域名: {cookie_info['domain']}")
        print(f"  路径: {cookie_info['path']}")
        print(f"  过期时间: {cookie_info['expires']}")
        print(f"  安全传输: {cookie_info['secure']}")
        print(f"  HttpOnly: {cookie_info['http_only']}")
        print("-" * 50)

# 示例使用
if __name__ == "__main__":
    # 获取所有Chrome cookie（原始方法）
    print("=== 所有Chrome Cookie ===")
    all_cookies = browsercookie.chrome()
    print(f"总共找到 {len(all_cookies)} 个cookie")
    
    # 获取特定网站的cookie
    target_website = "https://www.tapd.cn"
    specific_cookies = get_specific_website_cookies(target_website)
    
    # 打印特定网站的cookie信息
    print_cookies_info(specific_cookies, "TAPD")
    
    # 使用cookie进行请求的示例
    if specific_cookies:
        # 将cookie字典转换为requests可以使用的格式
        cookie_dict = {name: info['value'] for name, info in specific_cookies.items()}
        
        print("------------- 详细Cookie信息 --------------")
        print(specific_cookies)
        print("------------- 详细Cookie信息 --------------")

        print("------------- 简单Cookie字典 --------------")
        print(cookie_dict)
        print("------------- 简单Cookie字典 --------------")
        
        # 转换为F12格式的字符串
        cookie_string = cookies_to_string(specific_cookies)
        print("------------- F12格式的Cookie字符串 --------------")
        print(cookie_string)
        print("------------- F12格式的Cookie字符串 --------------")
        
        # 演示从字符串解析回字典
        parsed_cookies = string_to_cookies(cookie_string)
        print("------------- 从字符串解析的Cookie字典 --------------")
        print(parsed_cookies)
        print("------------- 从字符串解析的Cookie字典 --------------")
        
        # 比较F12和browsercookie的差异
        print("\n=== Cookie差异分析 ===")
        
        # 模拟F12获取的cookie（你可以替换为实际的F12 cookie字符串）
        f12_cookie_string = "__root_domain_v=.tapd.cn; _qddaz=QD.454025239501366; new_worktable=search_filter; tapdsession=17476210688f6cac83c97486ef90671b70a6dd7e31f52e4a6d83a205561b0049ba4be4ce64; t_u=77284caa2ba882b31d9a6a15091d63913abb5e8182a314437945492e8c08cd077ecee62a5398c31c7013ab10d2f65ef189ff37e37f8f3f4bdba30567a9aab57b714cb0fa6c0706f3%7C1; _t_crop=38588133; tapd_div=101_3044; _t_uid=1357329843; dsc-token=q9fhAytlrF7SK3LG; cherry-ai-guide-1357329843=1; cloud_current_workspaceId=41168903; locale=zh_CN; _wt=eyJ1aWQiOiIxMzU3MzI5ODQzIiwiY29tcGFueV9pZCI6IjM4NTg4MTMzIiwiZXhwIjoxNzUzNzc2Mzc2fQ%3D%3D.2c144c4246f25a05af882020119a8ea203ac3765a45e729684c32ea36c6001fd"
        
        f12_cookies = string_to_cookies(f12_cookie_string)
        browser_cookies = {name: info['value'] for name, info in specific_cookies.items()}
        
        differences = compare_cookies(f12_cookies, browser_cookies)
        
        print(f"F12获取的cookie数量: {differences['f12_count']}")
        print(f"browsercookie获取的cookie数量: {differences['browser_count']}")
        print(f"共同cookie数量: {differences['common_count']}")
        print(f"仅在F12中存在: {len(differences['only_in_f12'])} 个")
        print(f"仅在browsercookie中存在: {len(differences['only_in_browser'])} 个")
        
        if differences['only_in_f12']:
            print(f"\n仅在F12中存在的cookie: {differences['only_in_f12']}")
        
        if differences['only_in_browser']:
            print(f"\n仅在browsercookie中存在的cookie: {differences['only_in_browser']}")
        
        # 发送请求
        url = "https://www.tapd.cn/tapd_fe/41168903/iteration/card/1141168903001000090?q=7b8f936ecba99815da046deb8b75a458"
        response = requests.get(url, cookies=cookie_dict)
        print(f"\n请求状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.text)} 字符")
    else:
        print("未找到该网站的cookie")