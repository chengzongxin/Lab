"""
AI调试工具 - 通用AI对话接口
提供灵活的AI对话调试功能
"""

import os
import logging
from typing import List, Dict, Optional
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")


def chat_with_ai(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 500
) -> Dict:
    """
    通用AI对话接口
    
    :param messages: 消息列表，格式 [{"role": "system|user|assistant", "content": "..."}]
    :param model: 使用的模型
    :param temperature: 温度参数（0-2），越高越随机
    :param max_tokens: 最大token数
    :return: AI响应结果
    """
    
    if not OPENAI_API_KEY:
        logger.error("未设置OPENAI_API_KEY环境变量")
        raise ValueError("未配置OpenAI API密钥")
    
    try:
        # 配置代理
        proxy_url = HTTPS_PROXY or HTTP_PROXY
        
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
        
        logger.info(f"调用AI - 模型: {model}, 温度: {temperature}, 最大tokens: {max_tokens}")
        logger.info(f"消息数量: {len(messages)}")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        assistant_message = response.choices[0].message.content
        usage = response.usage
        
        logger.info(f"AI响应成功，使用tokens: {usage.total_tokens}")
        
        return {
            "success": True,
            "message": assistant_message,
            "model": model,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        }
    
    except Exception as e:
        logger.error(f"AI对话失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": None
        }


def get_presets() -> List[Dict]:
    """
    获取预设的提示词模板
    """
    return [
        {
            "name": "标题清洗专家",
            "description": "从ai_title_cleaner.py - 清洗商品标题，提取核心关键词",
            "system_prompt": """你是一个专业的商品标题清洗专家。你的任务是：
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

请只返回清洗后的关键词，不要解释。""",
            "user_prompt": "请清洗这个商品标题：",
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 64
        },
        {
            "name": "通用助手",
            "description": "通用AI助手，用于一般对话和问答",
            "system_prompt": "你是一个有帮助的AI助手。请简洁、准确地回答用户的问题。",
            "user_prompt": "",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 500
        },
        {
            "name": "代码助手",
            "description": "专注于编程和代码相关问题",
            "system_prompt": """你是一个专业的编程助手。你的特点是：
1. 提供清晰、可运行的代码示例
2. 解释代码的关键逻辑
3. 指出潜在的问题和最佳实践
4. 使用代码注释帮助理解

请用中文回答，代码用英文编写。""",
            "user_prompt": "",
            "model": "gpt-4o-mini",
            "temperature": 0.5,
            "max_tokens": 1000
        },
        {
            "name": "创意文案",
            "description": "生成创意文案和营销内容",
            "system_prompt": """你是一个创意文案专家。你擅长：
1. 创造吸引人的标题和口号
2. 编写生动的产品描述
3. 把握目标用户的心理
4. 使用情感化的语言

请保持专业、有趣、富有创意。""",
            "user_prompt": "",
            "model": "gpt-4o-mini",
            "temperature": 0.9,
            "max_tokens": 300
        }
    ]


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    test_messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
    
    result = chat_with_ai(test_messages)
    if result["success"]:
        print(f"AI回复: {result['message']}")
        print(f"使用tokens: {result['usage']['total_tokens']}")
    else:
        print(f"错误: {result['error']}")

