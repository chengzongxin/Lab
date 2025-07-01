from fastapi import APIRouter, Body
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

router = APIRouter()

@router.post("/config")
def set_config(
    seller_cookie: str = Body(...),
    compliance_cookie: str = Body(...),
    blue_cookie: str = Body(...),
    mallid: str = Body(...)
):
    config = {
        "seller_cookie": seller_cookie,
        "compliance_cookie": compliance_cookie,
        "blue_cookie": blue_cookie,
        "mallid": mallid
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return {"success": True, "msg": "配置已保存"}

@router.get("/config")
def get_config():
    if not os.path.exists(CONFIG_PATH):
        return {"success": False, "msg": "未配置"}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return {"success": True, "data": config} 