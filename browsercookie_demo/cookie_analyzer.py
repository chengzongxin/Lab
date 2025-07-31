import requests
import browsercookie
from urllib.parse import urlparse
from collections import Counter

def get_browser_cookies(website_domain):
    """
    通过browsercookie库获取指定网站的cookie
    
    参数:
        website_domain (str): 网站域名，如 "tapd.cn"
    
    返回:
        dict: cookie字典
    """
    all_cookies = browsercookie.chrome()
    website_cookies = {}
    
    for cookie in all_cookies:
        if website_domain in cookie.domain:
            website_cookies[cookie.name] = cookie.value
    
    return website_cookies

def string_to_cookies(cookie_string):
    """
    将F12格式的cookie字符串转换为字典
    """
    cookies = {}
    if not cookie_string:
        return cookies
    
    cookie_pairs = cookie_string.split("; ")
    for pair in cookie_pairs:
        if "=" in pair:
            name, value = pair.split("=", 1)
            cookies[name] = value
    
    return cookies

def cookies_to_string(cookies_dict):
    """
    将cookie字典转换为F12格式的字符串
    """
    cookie_pairs = []
    for name, value in cookies_dict.items():
        cookie_pairs.append(f"{name}={value}")
    return "; ".join(cookie_pairs)

def analyze_cookie_differences(f12_cookies, browser_cookies):
    """
    分析两种方法获取的cookie差异
    
    参数:
        f12_cookies (dict): F12获取的cookie
        browser_cookies (dict): browsercookie库获取的cookie
    
    返回:
        dict: 差异分析结果
    """
    f12_names = set(f12_cookies.keys())
    browser_names = set(browser_cookies.keys())
    
    # 只在F12中存在的cookie
    only_in_f12 = f12_names - browser_names
    
    # 只在browsercookie中存在的cookie
    only_in_browser = browser_names - f12_names
    
    # 两者都存在的cookie
    common = f12_names & browser_names
    
    # 值不同的cookie
    different_values = {}
    for name in common:
        if f12_cookies[name] != browser_cookies[name]:
            different_values[name] = {
                'f12_value': f12_cookies[name],
                'browser_value': browser_cookies[name]
            }
    
    return {
        'only_in_f12': {name: f12_cookies[name] for name in only_in_f12},
        'only_in_browser': {name: browser_cookies[name] for name in only_in_browser},
        'common': {name: f12_cookies[name] for name in common},
        'different_values': different_values,
        'f12_count': len(f12_cookies),
        'browser_count': len(browser_cookies),
        'common_count': len(common)
    }

def merge_cookies(f12_cookies, browser_cookies, priority='f12'):
    """
    合并两种方法获取的cookie
    
    参数:
        f12_cookies (dict): F12获取的cookie
        browser_cookies (dict): browsercookie库获取的cookie
        priority (str): 优先级，'f12' 或 'browser'
    
    返回:
        dict: 合并后的cookie字典
    """
    merged = {}
    
    # 先添加所有browser_cookies
    merged.update(browser_cookies)
    
    # 根据优先级决定如何处理重复的cookie
    if priority == 'f12':
        # F12优先级更高，覆盖重复的cookie
        merged.update(f12_cookies)
    else:
        # browser优先级更高，只添加F12中独有的cookie
        for name, value in f12_cookies.items():
            if name not in browser_cookies:
                merged[name] = value
    
    return merged

def test_cookies_with_request(cookies_dict, url, test_name):
    """
    测试cookie是否能成功访问目标URL
    
    参数:
        cookies_dict (dict): 要测试的cookie字典
        url (str): 目标URL
        test_name (str): 测试名称
    
    返回:
        dict: 测试结果
    """
    print(f"\n=== 测试 {test_name} ===")
    
    try:
        response = requests.get(url, cookies=cookies_dict, timeout=10)
        
        result = {
            'status_code': response.status_code,
            'content_length': len(response.text),
            'success': response.status_code == 200,
            'needs_login': '登录' in response.text or 'login' in response.text.lower(),
            'error': None
        }
        
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)} 字符")
        
        if response.status_code == 200:
            print("✅ 请求成功！")
            if result['needs_login']:
                print("⚠️  可能需要登录或cookie已过期")
            else:
                print("✅ 成功获取到页面内容")
        else:
            print(f"❌ 请求失败")
            
    except Exception as e:
        result = {
            'status_code': None,
            'content_length': 0,
            'success': False,
            'needs_login': False,
            'error': str(e)
        }
        print(f"❌ 请求异常: {e}")
    
    return result

# 示例使用
if __name__ == "__main__":
    # 你从F12复制的cookie字符串
    f12_cookie_string = "__root_domain_v=.tapd.cn; _qddaz=QD.454025239501366; new_worktable=search_filter; tapdsession=17476210688f6cac83c97486ef90671b70a6dd7e31f52e4a6d83a205561b0049ba4be4ce64; t_u=77284caa2ba882b31d9a6a15091d63913abb5e8182a314437945492e8c08cd077ecee62a5398c31c7013ab10d2f65ef189ff37e37f8f3f4bdba30567a9aab57b714cb0fa6c0706f3%7C1; _t_crop=38588133; tapd_div=101_3044; _t_uid=1357329843; dsc-token=q9fhAytlrF7SK3LG; cherry-ai-guide-1357329843=1; cloud_current_workspaceId=41168903; locale=zh_CN; _wt=eyJ1aWQiOiIxMzU3MzI5ODQzIiwiY29tcGFueV9pZCI6IjM4NTg4MTMzIiwiZXhwIjoxNzUzNzc2Mzc2fQ%3D%3D.2c144c4246f25a05af882020119a8ea203ac3765a45e729684c32ea36c6001fd"
    
    # 解析F12 cookie
    f12_cookies = string_to_cookies(f12_cookie_string)
    
    # 获取browsercookie
    browser_cookies = get_browser_cookies("tapd.cn")
    
    print("=== Cookie 对比分析 ===")
    print(f"F12获取的cookie数量: {len(f12_cookies)}")
    print(f"browsercookie获取的cookie数量: {len(browser_cookies)}")
    
    # 分析差异
    differences = analyze_cookie_differences(f12_cookies, browser_cookies)
    
    print(f"\n=== 差异分析 ===")
    print(f"共同cookie数量: {differences['common_count']}")
    print(f"仅在F12中存在: {len(differences['only_in_f12'])} 个")
    print(f"仅在browsercookie中存在: {len(differences['only_in_browser'])} 个")
    print(f"值不同的cookie: {len(differences['different_values'])} 个")
    
    # 显示详细差异
    if differences['only_in_f12']:
        print(f"\n仅在F12中存在的cookie:")
        for name, value in differences['only_in_f12'].items():
            print(f"  {name}: {value}")
    
    if differences['only_in_browser']:
        print(f"\n仅在browsercookie中存在的cookie:")
        for name, value in differences['only_in_browser'].items():
            print(f"  {name}: {value}")
    
    if differences['different_values']:
        print(f"\n值不同的cookie:")
        for name, values in differences['different_values'].items():
            print(f"  {name}:")
            print(f"    F12: {values['f12_value']}")
            print(f"    Browser: {values['browser_value']}")
    
    # 合并cookie
    merged_f12_priority = merge_cookies(f12_cookies, browser_cookies, 'f12')
    merged_browser_priority = merge_cookies(f12_cookies, browser_cookies, 'browser')
    
    print(f"\n=== 合并结果 ===")
    print(f"F12优先级合并: {len(merged_f12_priority)} 个cookie")
    print(f"Browser优先级合并: {len(merged_browser_priority)} 个cookie")
    
    # 测试不同cookie组合的效果
    target_url = "https://www.tapd.cn/tapd_fe/41168903/iteration/card/1141168903001000090?q=7b8f936ecba99815da046deb8b75a458"
    
    results = {}
    results['f12_only'] = test_cookies_with_request(f12_cookies, target_url, "仅F12 Cookie")
    results['browser_only'] = test_cookies_with_request(browser_cookies, target_url, "仅Browser Cookie")
    results['merged_f12'] = test_cookies_with_request(merged_f12_priority, target_url, "F12优先级合并")
    results['merged_browser'] = test_cookies_with_request(merged_browser_priority, target_url, "Browser优先级合并")
    
    # 总结
    print(f"\n=== 测试总结 ===")
    for test_name, result in results.items():
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"{test_name}: {status} (状态码: {result['status_code']})")
    
    print(f"\n=== 建议 ===")
    print("1. 如果F12 cookie能成功访问，优先使用F12 cookie")
    print("2. 如果F12 cookie失败，尝试合并两种方法")
    print("3. 某些cookie可能是动态生成的，需要定期更新")
    print("4. 建议同时保存两种方法获取的cookie作为备份") 