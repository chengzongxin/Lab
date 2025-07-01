import requests
import json
import time
from typing import List, Dict
import logging
import re

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 级别以获取更多信息
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchOfflineTool:
    def __init__(self):
        # 基础URL
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.api_url = f"{self.base_url}/marvel-supplier/api/ultraman/chat/reception/queryPreInterceptForToolSubmit"
        
        # 请求头
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "origin": "https://seller.kuajingmaihuo.com",
            "referer": "https://seller.kuajingmaihuo.com/goods/product/list",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
            "mallid": "634418223796259",
            "anti-content": "0aqWfxUeMwVEfaZWP6-sQQM3NbXf8gXww2Uf39xOyvShEv5wF-fTDBvoS3xkF3lk1sWuM-5vMeWWM35eFe1o-3qCIbRVN35Kd_62obf623qZIkz2ZkBeFDBfZeB-5eM-HIB3F4zMeB-FkBsV7s9V8QgjSvCSquze-EzX-DFRRe7eWDFflIDLZFKkPwS3I7F-xmHRPdKB2HKBvVH997XptavtOxXn2dm4a1qdOnpFraY_AwnUmJjUXydnGaiTSxiu2wqXHnpsuxpFrQYnwzmXbHqmjQj0Eyci9x9d4gbX_8xt2lI1dgUK59JXOC9OUt5X491KU4-P5NFJc_x14G4G_5U14H4o_HwXUGCfmy5oalOXONya5G4nGTaK59-QNN3oOYflqJ_XDgaQOOiyLPa14pmhiGskEPZaC91p5y1qdSvGNbO_uds4hmcF69BdFM3LwBeKzb2bWvl9mrlJoIlLDk8IxVSDzlmYcnMuQE49a902EImjeJu7aA",
            "cache-control": "max-age=0",
            "x-b-user-info": "DB000-0c2ef116-29eb-45ee-a37e-7a3b2caa41f1",
            "x-gateway-request-id": "1748262191308-289617571f57b1d573a639eb1abf1ad6-20",
            "x-temu-request-id": "MTIxMDEzMTMwMDAwMDAwMDAwMDAwIzE3NDgyNjIxOTEzMjkjMTAuMTAwLjIxNy4yMDQ=",
            # 注意：这里需要填入你的实际cookie
            "cookie": "api_uid=CmaibmgXiUFPWwBPCCK/Ag==; _bee=tfHT7LYhzCfWucOkWxZ5icxiBsAQXamH; rckk=tfHT7LYhzCfWucOkWxZ5icxiBsAQXamH; SUB_PASS_ID=eyJ0IjoiRjRraDJDQmNLbE5GRlRIOXZyQ05GaElLZmlBcFp3VGZvM0x4WFo4Nm9mY3Q5SDM0YjJDOWt3Sk9McHpJQi9aaSIsInYiOjEsInMiOjEwMDAwLCJ1IjoyNDE1MTU0NjgxNzcwMX0=; fingerprint=None; lingfeng_backend=backend-pro-0; api_uid=CmNNDWgx20yyaQBRbBZEAg==; _nano_fp=XpmYl09bnqC8X0XonT_MYnfCP5pFlK76TsS7G5bD; _bee=tfHT7LYhzCfWucOkWxZ5icxiBsAQXamH; _f77=fe503ea0-51c9-41ad-aa57-a17e3b9ed899; rckk=tfHT7LYhzCfWucOkWxZ5icxiBsAQXamH; ru1k=fe503ea0-51c9-41ad-aa57-a17e3b9ed899; _a42=55668fc2-6221-4e03-92ce-da00c700b90d; ru2k=55668fc2-6221-4e03-92ce-da00c700b90d; _f77=fe503ea0-51c9-41ad-aa57-a17e3b9ed899; _a42=55668fc2-6221-4e03-92ce-da00c700b90d; ru1k=fe503ea0-51c9-41ad-aa57-a17e3b9ed899; ru2k=55668fc2-6221-4e03-92ce-da00c700b90d; user_id=DB000-0c2ef116-29eb-45ee-a37e-7a3b2caa41f1; user_session=gC9oynQvJvie6hh9unl0ed74tNcEnkp4U1GGd125YpR4vn552fzjv7pZaR2selNKX6q0lYBCEBUy60slz0J3V3k127IAkWSarM3Y"
        }
        
        # 工具ID
        self.tool_id = 2406230000031
        
        # 最大重试次数
        self.max_retries = 1
        # 重试延迟（秒）
        self.retry_delay = 1

    def validate_cookie(self) -> bool:
        """
        验证cookie是否有效
        
        Returns:
            bool: cookie是否有效
        """
        if not self.headers.get("cookie"):
            logger.error("Cookie未设置")
            return False
            
        required_cookies = ["api_uid", "user_id", "user_session", "SUB_PASS_ID"]
        cookie_dict = dict(item.split("=", 1) for item in self.headers["cookie"].split("; "))
        
        missing_cookies = [cookie for cookie in required_cookies if cookie not in cookie_dict]
        if missing_cookies:
            logger.error(f"缺少必要的Cookie: {', '.join(missing_cookies)}")
            return False
            
        return True

    def offline_single_product(self, data_id: str, retry_count: int = 0) -> Dict:
        """
        下架单个商品
        
        Args:
            data_id: 商品ID
            retry_count: 当前重试次数
            
        Returns:
            Dict: 响应结果
        """
        if not self.validate_cookie():
            return {"success": False, "error": "Cookie验证失败", "error_code": 40001}
            
        payload = {
            "toolId": self.tool_id,
            "dataId": data_id
        }
        
        try:
            logger.info(f"正在发送请求，商品ID: {data_id}")
            logger.debug(f"请求头: {json.dumps(self.headers, ensure_ascii=False)}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            # 记录响应信息
            logger.info(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 403:
                logger.error("访问被拒绝，请检查认证信息")
                return {"success": False, "error": "访问被拒绝", "error_code": 403}
                
            result = response.json()
            logger.debug(f"响应内容: {json.dumps(result, ensure_ascii=False)}")
            
            # 检查错误码
            if result.get("error_code") == 40001:
                logger.error("认证失败，请检查cookie是否有效")
                return {"success": False, "error": "认证失败", "error_code": 40001}
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            if retry_count < self.max_retries:
                logger.info(f"将在 {self.retry_delay} 秒后重试...")
                time.sleep(self.retry_delay)
                return self.offline_single_product(data_id, retry_count + 1)
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"下架商品 {data_id} 时发生错误: {str(e)}")
            return {"success": False, "error": str(e)}

    def batch_offline_products(self, data_ids: List[str], delay: float = 1.0) -> List[Dict]:
        """
        批量下架商品
        
        Args:
            data_ids: 商品ID列表
            delay: 每次请求之间的延迟时间（秒）
            
        Returns:
            List[Dict]: 所有商品的下架结果
        """
        if not self.validate_cookie():
            logger.error("Cookie验证失败，无法继续执行")
            return []
            
        results = []
        total = len(data_ids)
        
        for index, data_id in enumerate(data_ids, 1):
            logger.info(f"正在处理第 {index}/{total} 个商品 (ID: {data_id})")
            result = self.offline_single_product(data_id)
            results.append(result)
            
            if index < total:
                logger.info(f"等待 {delay} 秒后处理下一个商品...")
                time.sleep(delay)
                
        return results

def main():
    # 使用示例
    tool = BatchOfflineTool()
    
    # 这里填入需要下架的商品ID列表
    product_ids = [
        "99630087532",
        # 添加更多商品ID...
    ]
    
    # 执行批量下架
    results = tool.batch_offline_products(product_ids)
    
    # 打印结果
    success_count = 0
    fail_count = 0
    
    for i, result in enumerate(results):
        print(f"\n商品 {product_ids[i]} 下架结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get("success", False):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个，失败: {fail_count} 个")

if __name__ == "__main__":
    main() 