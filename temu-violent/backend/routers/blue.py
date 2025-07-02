from fastapi import APIRouter, Body
from utils.request import load_config
import requests

router = APIRouter()

@router.post("/search")
def blue_search(
    picture_name: str = Body(..., embed=True),
    page: int = Body(1, embed=True),
    page_size: int = Body(20, embed=True)
):
    config = load_config()
    url = "https://apigw.hihumbird.com/bird-gallery/v2/picture/search?t=5c043cf81e9a4836a7adaecdfe348ec2"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": config.get("blue_token", ""),
        "origin": "https://fzhqtc.merchant.hihumbird.com",
        "referer": "https://fzhqtc.merchant.hihumbird.com/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
        "sign": "deb440ffc9e2d96e2ae342d6e70e7cff389d63918ede01c4722ca5fd701a325d",
        "stamp": "1751417757743",
        # 如需补充 sign、stamp、cookie 等字段，可在 config.json 里配置并补充到此处
    }

    print(headers)
    payload = {
        "page_size": page_size,
        "page": page,
        "total": 0,
        "ids": [],
        "sort": [{"sort_by": "created", "sort_type": 2}],
        "picture_name": picture_name,
        "codes": [],
        "category_id": "0",
        "gallery_id": [config.get("gallery_id", "180859")],
        "return_risk_word": False,
        "search_type": 1
    }
    resp = requests.post(url, headers=headers, json=payload)
    try:
        data = resp.json()
        print(data)
    except Exception:
        return {"success": False, "msg": "蓝站接口返回非JSON", "raw": resp.text}
    if data.get("result_code") != 200:
        return {"success": False, "msg": data.get("msg", "查询失败")}
    return {
        "success": True,
        "total": data["data"]["total"],
        "list": data["data"]["list"]
    }
