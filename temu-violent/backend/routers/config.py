from fastapi import APIRouter, Body
import json
import os
from typing import Dict, Any, Optional

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

router = APIRouter()

@router.post("/config")
def set_config(
    seller_cookie: str = Body(...),
    compliance_cookie: str = Body(...),
    blue_cookie: str = Body(...),
    mallid: str = Body(...),
    blue_token: str = Body(...)
):
    # 读取现有配置
    existing_config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            existing_config = json.load(f)
    
    # 检查配置是否有变化
    config_changed = (
        existing_config.get("seller_cookie") != seller_cookie or
        existing_config.get("compliance_cookie") != compliance_cookie or
        existing_config.get("blue_cookie") != blue_cookie or
        existing_config.get("mallid") != mallid or
        existing_config.get("blue_token") != blue_token
    )
    
    config: Dict[str, Any] = {
        "seller_cookie": seller_cookie,
        "compliance_cookie": compliance_cookie,
        "blue_cookie": blue_cookie,
        "mallid": mallid,
        "blue_token": blue_token
    }
    
    # 如果配置没有变化，保留现有的缓存数据
    if not config_changed:
        config["parent_msg_id"] = existing_config.get("parent_msg_id")
        config["parent_msg_timestamp"] = existing_config.get("parent_msg_timestamp")
        config["tool_id"] = existing_config.get("tool_id")
    else:
        # 配置有变化，清除缓存数据
        config["parent_msg_id"] = None
        config["parent_msg_timestamp"] = None
        config["tool_id"] = None
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True, 
        "msg": "配置已保存",
        "config_changed": config_changed
    }

@router.get("/config")
def get_config():
    if not os.path.exists(CONFIG_PATH):
        return {"success": False, "msg": "未配置"}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return {"success": True, "data": config}

@router.post("/config/cache")
def update_cache(
    parent_msg_id: Optional[str] = Body(None),
    parent_msg_timestamp: Optional[str] = Body(None),
    tool_id: Optional[str] = Body(None)
):
    """更新缓存数据"""
    if not os.path.exists(CONFIG_PATH):
        return {"success": False, "msg": "未配置"}
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 只更新提供的字段
    if parent_msg_id is not None:
        config["parent_msg_id"] = parent_msg_id
    if parent_msg_timestamp is not None:
        config["parent_msg_timestamp"] = parent_msg_timestamp
    if tool_id is not None:
        config["tool_id"] = tool_id
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return {"success": True, "msg": "缓存已更新"}

@router.delete("/config")
def clear_config():
    """清除所有配置"""
    try:
        # 如果配置文件存在，则删除它
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
            return {"success": True, "msg": "配置已清除"}
        else:
            return {"success": True, "msg": "配置文件不存在"}
    except Exception as e:
        return {"success": False, "msg": f"清除配置失败: {str(e)}"} 