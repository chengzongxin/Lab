"""
AI标题清洗工具
使用OpenAI API对TEMU商品标题进行清洗，提取核心关键词
"""

import os
import json
import logging
from typing import List, Dict, Optional
import httpx
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

# 从环境变量获取API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
# 获取代理配置
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

def clean_title_with_ai(title: str) -> Dict[str, any]:
    """
    使用AI清洗商品标题，提取核心关键词
    
    :param title: 原始商品标题
    :return: 包含cleaned_keywords（字符串）和keywords_list（列表）的字典
    """

    model = OPENAI_MODEL

    if not model:
        logger.error("未设置OPENAI_MODEL环境变量")
        raise ValueError("未配置OpenAI模型")

    if not OPENAI_API_KEY:
        logger.error("未设置OPENAI_API_KEY环境变量")
        raise ValueError("未配置OpenAI API密钥")
    
    try:
        # 配置代理
        # httpx 0.28.0+ 使用 proxy 参数而不是 proxies
        proxy_url = None
        if HTTPS_PROXY:
            proxy_url = HTTPS_PROXY
        elif HTTP_PROXY:
            proxy_url = HTTP_PROXY
            
        # 显式创建 httpx client
        # 1. 避免 openai 内部初始化错误
        # 2. 确保代理配置生效
        if proxy_url:
            logger.info(f"使用代理连接OpenAI: {proxy_url}")
            http_client = httpx.Client(proxy=proxy_url)
        else:
            http_client = httpx.Client()
        
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            http_client=http_client
        )
        
        # 构建提示词
        system_prompt = """你是一个专业的商品标题清洗专家。你的任务是：
1. 从商品标题中提取核心关键词
2. 去除所有通用的营销形容词（如：hot, best, new, premium, quality, perfect, amazing等）
3. 去除数量词和规格词（如：1pc, 2pcs, set of, pack）
4. 保留最重要的商品类型、风格、特征等核心描述词
5. 必须去除以下类目词：cap, scarf, beanie, hat, sock, socks
6. 返回最多不超过5个关键词，用空格分隔

示例：
输入：1pc Retro Brimless Hat With Deep Sea Dive Diving Design - Casual Stylish Accessory For Men & Women
输出：retro brimless hat deep sea dive design

输入：Men's Winter Warm Knit Beanie - Premium Quality Soft Comfortable Hat
输出：men winter knit beanie

请只返回清洗后的关键词，不要解释。"""

        user_prompt = f"请清洗这个商品标题：{title}"
        
        logger.info(f"正在调用AI清洗标题: {title[:50]}...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # 降低温度以获得更一致的结果
            max_tokens=100
        )
        
        cleaned_keywords = response.choices[0].message.content.strip()
        
        # 将关键词拆分成列表
        keywords_list = [kw.strip() for kw in cleaned_keywords.split() if kw.strip()]
        
        logger.info(f"AI清洗完成: {cleaned_keywords}")
        
        return {
            "cleaned_keywords": cleaned_keywords,
            "keywords_list": keywords_list,
            "model_used": model,
            "success": True
        }
    
    except RateLimitError as e:
        logger.warning(f"OpenAI API额度不足或请求过快: {e}")
        return {
            "cleaned_keywords": None,
            "keywords_list": [],
            "model_used": model,
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"AI标题清洗失败: {e}")
        return {
            "cleaned_keywords": None,
            "keywords_list": [],
            "model_used": model,
            "success": False,
            "error": str(e)
        }


def clean_title_with_fallback(title: str) -> Dict[str, any]:
    """
    带降级方案的标题清洗：优先使用AI，失败时使用规则方法
    
    :param title: 原始标题
    :return: 清洗结果
    """
    # 首先尝试AI清洗
    try:
        result = clean_title_with_ai(title)
        if result["success"]:
            return result
    except Exception as e:
        logger.warning(f"AI清洗调用失败: {e}")
    
    # AI失败，使用规则方法作为降级方案
    logger.warning(f"AI清洗失败，使用规则方法作为降级方案")
    
    # 简单的规则：
    # 1. 转小写
    # 2. 去除常见营销词
    # 3. 去除数量词
    # 4. 去除特殊字符
    
    import re
    
    # 通用营销词列表
    marketing_words = [
        'hot', 'best', 'new', 'premium', 'quality', 'perfect', 'amazing',
        'great', 'super', 'top', 'special', 'unique', 'exclusive', 'limited',
        'sale', 'discount', 'cheap', 'free', 'shipping', 'fashion', 'trendy',
        'stylish', 'casual', 'comfortable', 'soft', 'warm', 'cool',
        'cap', 'scarf', 'beanie', 'hat', 'sock', 'socks'
    ]
    
    # 数量词模式
    quantity_patterns = [
        r'\d+\s*pc[s]?',  # 1pc, 2pcs
        r'\d+\s*pack',    # 1pack
        r'set\s+of\s+\d+', # set of 2
        r'\d+\s*piece',   # 1piece
    ]
    
    cleaned = title.lower()
    
    # 去除数量词
    for pattern in quantity_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # 去除营销词
    for word in marketing_words:
        cleaned = re.sub(r'\b' + word + r'\b', '', cleaned, flags=re.IGNORECASE)
    
    # 去除特殊字符，只保留字母数字和空格
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    
    # 去除多余空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 取前5个词
    keywords_list = cleaned.split()[:5]
    cleaned_keywords = ' '.join(keywords_list)
    
    logger.info(f"规则清洗完成: {cleaned_keywords}")
    
    return {
        "cleaned_keywords": cleaned_keywords,
        "keywords_list": keywords_list,
        "model_used": "rule-based-fallback",
        "success": True
    }


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    test_titles = [
        "1pc Retro Brimless Hat With Deep Sea Dive Diving Design - Casual Stylish Accessory For Men & Women",
        "Men's Winter Warm Knit Beanie - Premium Quality Soft Comfortable Hat",
        "Colorful Pullover Hat Ski Hat For Men Women Casual Neck Hair Hoop Skull Cap Hip Hop Hat Beanie Christmas Gift"
    ]
    
    for title in test_titles:
        print(f"\n原标题: {title}")
        result = clean_title_with_fallback(title)
        print(f"清洗后: {result['cleaned_keywords']}")
        print(f"关键词列表: {result['keywords_list']}")

