import browsercookie
import requests

def get_website_cookies_simple(website_domain):
    """
    简单方法获取特定网站的cookie
    
    参数:
        website_domain (str): 网站域名，如 "tapd.cn"
    
    返回:
        dict: cookie名称和值的字典
    """
    # 获取所有cookie
    all_cookies = browsercookie.chrome()
    
    # 过滤特定网站的cookie
    website_cookies = {}
    
    for cookie in all_cookies:
        if website_domain in cookie.domain:
            website_cookies[cookie.name] = cookie.value
    
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
    for name, value in cookies_dict.items():
        cookie_pairs.append(f"{name}={value}")
    
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

# 使用示例
if __name__ == "__main__":
    # 获取TAPD网站的cookie
    tapd_cookies = get_website_cookies_simple("tapd.cn")
    
    print("=== TAPD网站的Cookie ===")
    for name, value in tapd_cookies.items():
        print(f"{name}: {value}")
    
    print(f"\n总共找到 {len(tapd_cookies)} 个cookie")
    
    # 转换为F12格式的字符串
    cookie_string = cookies_to_string(tapd_cookies)
    print("\n=== F12格式的Cookie字符串 ===")
    print(cookie_string)
    
    # 演示从字符串解析回字典
    parsed_cookies = string_to_cookies(cookie_string)
    print("\n=== 从字符串解析的Cookie字典 ===")
    print(parsed_cookies)
    
    # 如果找到了cookie，可以用它们发送请求
    if tapd_cookies:
        print("\n使用cookie发送请求...")
        url = "https://www.tapd.cn/tapd_fe/41168903/iteration/card/1141168903001000090?q=7b8f936ecba99815da046deb8b75a458"
        
        try:
            response = requests.get(url, cookies=tapd_cookies)
            print(f"请求状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.text)} 字符")
        except Exception as e:
            print(f"请求失败: {e}")
    else:
        print("未找到TAPD网站的cookie") 