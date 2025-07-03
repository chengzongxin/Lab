from fastapi import APIRouter, Query, Body
from utils.scraper import search_temu
from utils.craw import ViolationListCrawler
from utils.request import NetworkRequest
import os
from typing import Optional, List

router = APIRouter()


@router.get("/compliance/list")
def get_compliance_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量")
):
    crawler = ViolationListCrawler(config_type="compliance")
    data = crawler.get_page_data(page, page_size)
    if data is not None:
        return {"success": True, "data": data}
    else:
        return {"success": False, "msg": "获取数据失败"}

@router.post("/seller/product")
def get_product(
    productIds: Optional[List[int]] = Body(None, embed=True),
    productName: Optional[str] = Body(None, embed=True),
    page: int = Body(1, embed=True),
    pageSize: int = Body(20, embed=True)
):
    req = NetworkRequest(config_type="seller")
    url = "https://seller.kuajingmaihuo.com/bg-visage-mms/product/skc/pageQuery"
    payload = {"page": page, "pageSize": pageSize}
    if productIds is not None:
        payload["productIds"] = productIds
    if productName is not None:
        payload["productName"] = productName
    result = req.post(url, data=payload)
    if not result or not result.get("success"):
        return {"success": False, "msg": "查询失败"}
    items = result.get("result", {}).get("pageItems", [])
    if not items:
        return {"success": False, "msg": "未找到商品"}
    # 返回所有商品列表
    products = [
        {
            "productId": item.get("productId"),
            "productName": item.get("productName"),
            "mainImageUrl": item.get("mainImageUrl"),
            "goodsId": item.get("goodsId"),
            "categories": item.get("categories"),
            # 可根据需要补充更多字段
        }
        for item in items
    ]
    return {
        "success": True,
        "data": products
    }

@router.post("/seller/offline")
def offline_products(productIds: List[int] = Body(..., embed=True)):
    req = NetworkRequest(config_type="seller")
    # 1. 获取所有工具
    tool_list_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/querySelfServiceTools"
    tool_list_resp = req.post(tool_list_url, data={})
    tool_id = None
    if tool_list_resp and tool_list_resp.get("success"):
        tools = tool_list_resp.get("result", {}).get("list", [])
        for tool in tools:
            if tool.get("toolName") == "商品下架":
                tool_id = tool.get("toolId")
                break
    if not tool_id:
        return {"success": False, "msg": "未找到商品下架工具ID"}

    # 2. 下架操作
    url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/queryPreInterceptForToolSubmit"
    results = []
    for data_id in productIds:
        payload = {
            "toolId": tool_id,
            "dataId": data_id
        }
        result = req.post(url, data=payload)
        results.append({
            "dataId": data_id,
            "result": result
        })
    return {
        "success": True,
        "results": results
    }
