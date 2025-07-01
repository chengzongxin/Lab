from fastapi import APIRouter, Query
from utils.scraper import search_blue

router = APIRouter()

@router.get("/search")
def search(keyword: str = Query(...)):
    return search_blue(keyword)
