import requests
import os
import json
from typing import Dict, Optional, Any

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

class NetworkRequest:
    """
    TEMU 网络请求工具类，支持每次请求动态传入 cookie 和 mallid，并可从 config.json 读取。
    config_type: seller | compliance | blue | None
    """
    def __init__(self, cookie: Optional[str] = None, mallid: Optional[str] = None, config_type: Optional[str] = None):
        self.session = requests.Session()
        config = load_config()
        # 根据 config_type 选择不同的 cookie
        if config_type == "seller":
            self.default_cookie = config.get("seller_cookie", "")
        elif config_type == "compliance":
            self.default_cookie = config.get("compliance_cookie", "")
        elif config_type == "blue":
            self.default_cookie = config.get("blue_cookie", "")
        else:
            self.default_cookie = cookie or config.get("seller_cookie", "") or os.getenv("TEMU_COOKIE", "")
        self.default_mallid = mallid or config.get("mallid", "") or os.getenv("TEMU_MALLID", "")

    def _get_headers(self, cookie=None, mallid=None) -> Dict[str, str]:
        return {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "anti-content": "",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "cookie": cookie if cookie is not None else self.default_cookie,
            "mallid": mallid if mallid is not None else self.default_mallid,
            "origin": "https://seller.kuajingmaihuo.com",
            "referer": "https://seller.kuajingmaihuo.com/goods/product/list",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
        }

    def get(self, url: str, params: Optional[Dict] = None, cookie: Optional[str] = None, mallid: Optional[str] = None) -> Optional[Dict]:
        try:
            headers = self._get_headers(cookie, mallid)
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"GET请求失败: {e}")
            return None

    def post(self, url: str, data: Dict[str, Any], cookie: Optional[str] = None, mallid: Optional[str] = None) -> Optional[Dict]:
        try:
            headers = self._get_headers(cookie, mallid)
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"POST请求失败: {e}")
            return None 