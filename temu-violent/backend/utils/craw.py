import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from .request import NetworkRequest

@dataclass
class PunishDetail:
    punish_id: int
    target_id: Optional[int]
    target_type: Optional[str]
    violation_type: int
    punish_infect_desc: str
    site_id: int
    remarks: Optional[str]
    status: int
    now_appeal_time: int
    max_appeal_time: int
    start_time: int
    plan_end_time: int
    real_end_time: Optional[int]
    appeal_id: Optional[int]
    appeal_status: int
    appeal_create_time: Optional[int]
    appeal_end_time: Optional[int]
    appeal_over_due: bool
    punish_appeal_type: Optional[str]
    illegal_detail: Optional[List[Dict[str, Any]]]
    rectification_suggestion: str
    create_from_upgrade: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PunishDetail':
        return cls(
            punish_id=data.get('punish_id', 0),
            target_id=data.get('target_id'),
            target_type=data.get('target_type'),
            violation_type=data.get('violation_type', 0),
            punish_infect_desc=data.get('punish_infect_desc', ''),
            site_id=data.get('site_id', 0),
            remarks=data.get('remarks'),
            status=data.get('status', 0),
            now_appeal_time=data.get('now_appeal_time', 0),
            max_appeal_time=data.get('max_appeal_time', 0),
            start_time=data.get('start_time', 0),
            plan_end_time=data.get('plan_end_time', 0),
            real_end_time=data.get('real_end_time'),
            appeal_id=data.get('appeal_id'),
            appeal_status=data.get('appeal_status', 0),
            appeal_create_time=data.get('appeal_create_time'),
            appeal_end_time=data.get('appeal_end_time'),
            appeal_over_due=data.get('appeal_over_due', False),
            punish_appeal_type=data.get('punish_appeal_type'),
            illegal_detail=data.get('illegal_detail', []),
            rectification_suggestion=data.get('rectification_suggestion', ''),
            create_from_upgrade=data.get('create_from_upgrade', False)
        )

@dataclass
class ViolationProduct:
    target_type: str
    target_id: int
    product_mapping_id: int
    goods_id: int
    spu_id: int
    goods_name: str
    goods_img_url: str
    mall_id: int
    mall_name: Optional[str]
    source_punish_name: str
    punish_type: int
    leaf_reason_id: int
    leaf_reason_name: str
    violation_desc: str
    violation_type: int
    site_num: int
    punish_num: int
    punish_detail_list: List[PunishDetail]
    can_appeal_punish_detail_list: List[PunishDetail]
    can_not_appeal: Optional[bool]
    reject_desc: Optional[str]
    appeal_status: int
    misuse_ban_appeal: bool
    appeal_over_due: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViolationProduct':
        punish_detail_list = [PunishDetail.from_dict(d) for d in data.get('punish_detail_list', [])]
        can_appeal_list = [PunishDetail.from_dict(d) for d in data.get('can_appeal_punish_detail_list', [])]
        return cls(
            target_type=data.get('target_type', ''),
            target_id=data.get('target_id', 0),
            product_mapping_id=data.get('product_mapping_id', 0),
            goods_id=data.get('goods_id', 0),
            spu_id=data.get('spu_id', 0),
            goods_name=data.get('goods_name', ''),
            goods_img_url=data.get('goods_img_url', ''),
            mall_id=data.get('mall_id', 0),
            mall_name=data.get('mall_name'),
            source_punish_name=data.get('source_punish_name', ''),
            punish_type=data.get('punish_type', 0),
            leaf_reason_id=data.get('leaf_reason_id', 0),
            leaf_reason_name=data.get('leaf_reason_name', ''),
            violation_desc=data.get('violation_desc', ''),
            violation_type=data.get('violation_type', 0),
            site_num=data.get('site_num', 0),
            punish_num=data.get('punish_num', 0),
            punish_detail_list=punish_detail_list,
            can_appeal_punish_detail_list=can_appeal_list,
            can_not_appeal=data.get('can_not_appeal'),
            reject_desc=data.get('reject_desc'),
            appeal_status=data.get('appeal_status', 0),
            misuse_ban_appeal=data.get('misuse_ban_appeal', False),
            appeal_over_due=data.get('appeal_over_due', False)
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

    def get_total_data(self, page: int, page_size: int) -> Optional[int]:
        payload = {
            "page_num": page,
            "page_size": page_size,
            "target_type": "goods"
        }
        result = self.request.post(self.api_url, data=payload)
        if not result or not result.get('success'):
            return None
        return result.get('result', {}).get('total', 0)