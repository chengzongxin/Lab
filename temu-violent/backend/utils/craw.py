import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from .request import NetworkRequest

@dataclass
class ViolationProduct:
    spu_id: int
    goods_name: str
    # 可根据实际需要添加更多字段

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViolationProduct':
        return cls(
            spu_id=data.get('spu_id', 0),
            goods_name=data.get('goods_name', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ViolationListCrawler:
    def __init__(self, cookie: str = None, mallid: str = None, config_type: str = "compliance"):
        self.base_url = "https://agentseller.temu.com"
        self.api_url = f"{self.base_url}/mms/tmod_punish/agent/merchant_appeal/entrance/list"
        self.request = NetworkRequest(cookie, mallid, config_type)

    def get_page_data(self, page: int, page_size: int) -> Optional[List[Dict[str, Any]]]:
        payload = {
            "page_num": page,
            "page_size": page_size,
            "target_type": "goods"
        }
        result = self.request.post(self.api_url, data=payload)
        if not result or not result.get('success'):
            return None
        items = result.get('result', {}).get('punish_appeal_entrance_list', [])
        return [ViolationProduct.from_dict(item).to_dict() for item in items] 