import requests

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

# 你从F12中复制的cookie字符串
cookie_string_from_f12 = "__root_domain_v=.tapd.cn; _qddaz=QD.454025239501366; new_worktable=search_filter; tapdsession=17476210688f6cac83c97486ef90671b70a6dd7e31f52e4a6d83a205561b0049ba4be4ce64; t_u=77284caa2ba882b31d9a6a15091d63913abb5e8182a314437945492e8c08cd077ecee62a5398c31c7013ab10d2f65ef189ff37e37f8f3f4bdba30567a9aab57b714cb0fa6c0706f3%7C1; _t_crop=38588133; tapd_div=101_3044; _t_uid=1357329843; dsc-token=q9fhAytlrF7SK3LG; cherry-ai-guide-1357329843=1; cloud_current_workspaceId=41168903; locale=zh_CN"

if __name__ == "__main__":
    print("=== 原始Cookie字符串（从F12复制） ===")
    print(cookie_string_from_f12)
    print()
    
    # 解析为字典
    cookies_dict = string_to_cookies(cookie_string_from_f12)
    
    print("=== 解析后的Cookie字典 ===")
    for name, value in cookies_dict.items():
        print(f"{name}: {value}")
    print()
    
    print(f"总共解析出 {len(cookies_dict)} 个cookie")
    print()
    
    # 转换回字符串格式（验证解析是否正确）
    reconstructed_string = cookies_to_string(cookies_dict)
    print("=== 重新构建的Cookie字符串 ===")
    print(reconstructed_string)
    print()
    
    # 使用这些cookie发送请求
    print("=== 使用Cookie发送请求 ===")
    url = "https://www.tapd.cn/tapd_fe/41168903/iteration/card/1141168903001000090?q=7b8f936ecba99815da046deb8b75a458"
    
    try:
        response = requests.get(url, cookies=cookies_dict)
        print(f"请求状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.text)} 字符")
        
        # 检查是否成功获取到内容
        if response.status_code == 200:
            print("✅ 请求成功！")
            # 可以进一步检查响应内容
            if "登录" in response.text or "login" in response.text.lower():
                print("⚠️  可能需要登录或cookie已过期")
            else:
                print("✅ 成功获取到页面内容")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n=== 重要说明 ===")
    print("1. 这个示例展示了如何手动解析F12中的cookie字符串")
    print("2. 你可以直接复制F12中的cookie字符串，替换上面的cookie_string_from_f12变量")
    print("3. 确保cookie没有过期，否则请求可能会失败")
    print("4. 某些网站可能需要额外的请求头或参数") 