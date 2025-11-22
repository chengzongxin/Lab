
import os
import sys
import logging
from dotenv import load_dotenv
import httpx

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_final():
    print("Running final verification for FALLBACK mechanism...")
    
    # 测试 ai_title_cleaner
    try:
        from ai_title_cleaner import clean_title_with_fallback
        print("Calling clean_title_with_fallback...")
        
        # 这应该会触发API调用 -> 失败(429) -> 捕获异常 -> 降级到规则清洗 -> 返回成功
        result = clean_title_with_fallback("Test Title with 1pc and Marketing Words")
        print(f"Result: {result}")
        
        if result.get('success'):
            print(f"SUCCESS: Fallback worked! Model used: {result.get('model_used')}")
            if result.get('model_used') == 'rule-based-fallback':
                print("Confirmed: System correctly fell back to rule-based cleaning.")
        else:
            print("FAILURE: Fallback did not work.")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final()
