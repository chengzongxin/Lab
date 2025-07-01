from fastapi import APIRouter, Query
from utils.scraper import search_temu
from utils.craw import ViolationListCrawler
import os

router = APIRouter()

@router.get("/search")
def search(keyword: str = Query(...)):
    return search_temu(keyword)

@router.get("/violations")
def get_violations(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    cookie: str = Query(None, description="可选，TEMU Cookie，不传则用 .env")
):
    # 优先用传入 cookie，否则用环境变量
    cookie_val = cookie or os.getenv("TEMU_COOKIE", "")
    if not cookie_val:
        return {"success": False, "msg": "未提供 Cookie"}
    crawler = ViolationListCrawler(cookie_val)
    data = crawler.get_page_data(page, page_size)
    if data is not None:
        return {"success": True, "data": data}
    else:
        return {"success": False, "msg": "获取数据失败"}

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
