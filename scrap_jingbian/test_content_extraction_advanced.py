#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级文章内容提取测试脚本
专门测试p标签内容提取功能
"""

from bs4 import BeautifulSoup
import re

def test_p_tag_extraction():
    """测试p标签内容提取功能"""
    
    # 基于你提供的真实HTML结构
    sample_html = '''
    <div data-anchor-id="content" class="index_articleWrap__nPJne">
        <div>
            <div class="index_richTextPopup___6yTD">
                <div class="text-[.57rem] tracking-normal text-[#1f1f1f] bg-[#fff] leading-[.93rem] overflow-hidden index_textContent__U8ot6 index_richText__vkNnU index_richTextPc__3FDg9">
                    <div>
                        <p>牙一到晚上疼通常是因为下列几个原因：</p>
                        <p>1、<a class="health-detail-highlight" data-highlightid="ydxx_8044155665996185374" highlighttype="306" href="...">牙髓炎</a>。牙髓炎是发生于牙髓组织的炎症性疾病，主要是由细菌感染引起，当患者患有牙髓炎时，通常会出现牙齿疼痛的症状，这种症状在夜间格外明显，因为夜间人体躺卧休息时，流入到牙髓内的血流量会增加，从而加大对牙神经的刺激。患者可在医生的指导下服用抗生素或止痛药等药物缓解症状。但彻底消除疼痛症状需要找到患牙并做<a class="health-detail-highlight" data-highlightid="ydcz_5377943082221769904" highlighttype="311" href="...">根管治疗</a>。</p>
                        <p>2、<a class="health-detail-highlight" data-highlightid="ydxx_8250829123023810217" highlighttype="306" href="...">牙周炎</a>。当患者患有牙周炎时，通常也会出现牙一到晚上疼的症状，牙周炎是发生在牙周组织的慢性炎症。患者可在医生的指导下服用<a class="health-detail-highlight" data-highlightid="ydyp_11737599648565834968" highlighttype="308" href="...">替硝唑片</a>、<a class="health-detail-highlight" data-highlightid="ydyp_11683294674759464881" highlighttype="308" href="...">阿莫西林胶囊</a>等药物缓解症状。并对患牙做牙周基础治疗改善牙周状况。</p>
                        <p>3、<a class="health-detail-highlight" data-highlightid="ydxx_8207251113464819525" highlighttype="306" href="...">智齿发炎</a>。牙一到晚上疼，可能是因为智齿发炎所引起的，患者可在医生的指导下服用<a class="health-detail-highlight" data-highlightid="ydyp_11972581526977305495" highlighttype="308" href="...">头孢拉定</a>、<a class="health-detail-highlight" data-highlightid="ydyp_15743485181324276132" highlighttype="308" href="...">头孢呋辛酯</a>等药物进行治疗。</p>
                    </div>
                </div>
            </div>
        </div>
        <div style="width:100%;height:0.5px"></div>
    </div>
    '''
    
    print("=== 高级文章内容提取测试 ===\n")
    
    # 测试1: 直接提取p标签内容
    print("1. 直接提取p标签内容:")
    try:
        soup = BeautifulSoup(sample_html, 'html.parser')
        p_elements = soup.find_all('p')
        
        if p_elements:
            p_texts = []
            for p in p_elements:
                text = p.get_text(strip=True)
                if text and len(text) > 5:
                    p_texts.append(text)
            
            if p_texts:
                content = '\n\n'.join(p_texts)
                print(f"   成功提取{len(p_texts)}个段落")
                print(f"   总长度: {len(content)} 字符")
                print(f"   内容预览:\n{content[:200]}...")
            else:
                print("   未找到有效的段落内容")
        else:
            print("   未找到p标签")
    except Exception as e:
        print(f"   提取失败: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # 测试2: 使用正则表达式提取p标签
    print("2. 使用正则表达式提取p标签:")
    try:
        p_pattern = r'<p[^>]*>(.*?)</p>'
        p_matches = re.findall(p_pattern, sample_html, re.DOTALL | re.IGNORECASE)
        
        if p_matches:
            p_texts = []
            for p_html in p_matches:
                # 清理HTML标签
                soup = BeautifulSoup(p_html, 'html.parser')
                text = soup.get_text(strip=True)
                if text and len(text) > 5:
                    p_texts.append(text)
            
            if p_texts:
                content = '\n\n'.join(p_texts)
                print(f"   成功提取{len(p_texts)}个段落")
                print(f"   总长度: {len(content)} 字符")
                print(f"   内容预览:\n{content[:200]}...")
            else:
                print("   未找到有效的段落内容")
        else:
            print("   正则表达式未匹配到p标签")
    except Exception as e:
        print(f"   提取失败: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # 测试3: 测试内容清理功能
    print("3. 测试内容清理功能:")
    try:
        # 模拟提取到的内容
        raw_content = "牙一到晚上疼通常是因为下列几个原因：\n\n1、牙髓炎。牙髓炎是发生于牙髓组织的炎症性疾病...\n\n2、牙周炎。当患者患有牙周炎时...\n\n3、智齿发炎。牙一到晚上疼，可能是因为智齿发炎所引起的..."
        
        # 清理内容
        cleaned_content = clean_content(raw_content)
        
        print(f"   原始内容长度: {len(raw_content)} 字符")
        print(f"   清理后长度: {len(cleaned_content)} 字符")
        print(f"   清理后内容:\n{cleaned_content}")
        
    except Exception as e:
        print(f"   清理测试失败: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # 测试4: 测试不同长度的内容
    print("4. 测试不同长度的内容:")
    try:
        # 短内容
        short_content = "这是一个短段落。"
        print(f"   短内容: '{short_content}' (长度: {len(short_content)})")
        
        # 中等内容
        medium_content = "这是一个中等长度的段落，包含一些详细信息。" * 10
        print(f"   中等内容长度: {len(medium_content)} 字符")
        
        # 长内容
        long_content = "这是一个很长的段落。" * 1000
        print(f"   长内容长度: {len(long_content)} 字符")
        
        # 测试长度限制
        max_length = 100
        if len(long_content) > max_length:
            truncated = long_content[:max_length] + "...(内容已截断)"
            print(f"   截断后长度: {len(truncated)} 字符")
        
    except Exception as e:
        print(f"   长度测试失败: {e}")
    
    print("\n=== 测试完成 ===")

def clean_content(content_text):
    """清理和格式化内容（与爬虫程序中的方法一致）"""
    try:
        # 移除多余的空白字符
        content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
        content_text = re.sub(r' +', ' ', content_text)
        content_text = content_text.strip()
        
        # 移除可能的广告或无关内容
        content_text = re.sub(r'广告|推广|点击查看|更多信息', '', content_text)
        
        # 限制内容长度（避免过长）
        max_length = 10000
        if len(content_text) > max_length:
            content_text = content_text[:max_length] + "...(内容已截断)"
            print(f"   文章内容过长，已截断至{max_length}字符")
        
        return content_text
        
    except Exception as e:
        print(f"   清理内容失败: {e}")
        return content_text

if __name__ == "__main__":
    test_p_tag_extraction()
