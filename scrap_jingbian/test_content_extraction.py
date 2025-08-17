#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文章内容提取功能
"""

from bs4 import BeautifulSoup
import re

def test_content_extraction():
    """测试内容提取功能"""
    
    # 模拟HTML内容（基于你提供的结构）
    sample_html = '''
    <div data-anchor-id="content" class="index_articleWrap__nPJne">
        <div>
            <div class="index_richTextPopup___6yTD">
                <div class="text-[.57rem] tracking-normal text-[#1f1f1f] bg-[#fff] leading-[.93rem] overflow-hidden index_textContent__U8ot6 index_richText__vkNnU index_richTextPc__3FDg9">
                    <div>
                        <p><span style="color: rgb(0, 0, 0);">夜里尿频尿急，可能是生理性原因所造成的，也有可能是因为病理性原因所引起的，比如<a class="health-detail-highlight" data-highlightid="ydxx_8127048328650495874" highlighttype="306" href="...">肾结石</a>、尿道炎等。</span></p>
                        <p><span style="color: rgb(0, 0, 0);">如果在睡觉之前喝过多的水，经过一段时间的代谢以后，可能会使膀胱处于充盈的状态，从而出现夜里尿频尿急的症状。这属于一种生理性原因，不必过分担心。</span></p>
                        <p><span style="color: rgb(0, 0, 0);">如果是肾结石患者，可出现腰部疼痛、尿血、尿频、尿急、排尿疼痛等不适症状，而且夜间会加剧，也会导致夜里尿频尿急。这属于一种病理性原因，可以通过<a class="health-detail-highlight" data-highlightid="ydcz_5359440285864887923" highlighttype="311" href="...">体外碎石</a>的方式进行治疗，也可以通过手术取石的方式进行改善。</span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    print("=== 测试文章内容提取功能 ===\n")
    
    # 测试1: 使用CSS选择器
    print("1. 测试CSS选择器提取:")
    try:
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        # 尝试多种选择器
        selectors = [
            "div[data-anchor-id='content']",
            "div.index_articleWrap__nPJne",
            "div.index_textContent__U8ot6",
            "div.index_richText__vkNnU",
            "div.index_richTextPc__3FDg9"
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(separator='\n', strip=True)
                    if text:
                        print(f"   选择器 '{selector}' 成功")
                        print(f"   提取内容长度: {len(text)} 字符")
                        print(f"   内容预览: {text[:100]}...")
                        break
            except Exception as e:
                print(f"   选择器 '{selector}' 失败: {e}")
    except Exception as e:
        print(f"   CSS选择器测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试2: 使用正则表达式
    print("2. 测试正则表达式提取:")
    try:
        patterns = [
            r'<div[^>]*data-anchor-id="content"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*index_articleWrap[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*index_textContent[^"]*"[^>]*>(.*?)</div>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sample_html, re.DOTALL | re.IGNORECASE)
            if match:
                html_content = match.group(1)
                # 清理HTML标签
                soup = BeautifulSoup(html_content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                if text:
                    print(f"   正则表达式 '{pattern}' 成功")
                    print(f"   提取内容长度: {len(text)} 字符")
                    print(f"   内容预览: {text[:100]}...")
                    break
        else:
            print("   所有正则表达式都未匹配到内容")
    except Exception as e:
        print(f"   正则表达式测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试3: 内容清理和格式化
    print("3. 测试内容清理和格式化:")
    try:
        soup = BeautifulSoup(sample_html, 'html.parser')
        content_element = soup.select_one("div[data-anchor-id='content']")
        if content_element:
            raw_text = content_element.get_text(separator='\n', strip=True)
            
            # 清理空白字符
            cleaned_text = re.sub(r'\n\s*\n', '\n\n', raw_text)
            cleaned_text = re.sub(r' +', ' ', cleaned_text)
            cleaned_text = cleaned_text.strip()
            
            print(f"   原始内容长度: {len(raw_text)} 字符")
            print(f"   清理后长度: {len(cleaned_text)} 字符")
            print(f"   清理后内容预览:\n{cleaned_text[:200]}...")
            
            # 测试长度限制
            max_length = 100
            if len(cleaned_text) > max_length:
                truncated_text = cleaned_text[:max_length] + "...(内容已截断)"
                print(f"   截断后内容:\n{truncated_text}")
        else:
            print("   未找到内容元素")
    except Exception as e:
        print(f"   内容清理测试失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_content_extraction()
