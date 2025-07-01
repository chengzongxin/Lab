import requests
from bs4 import BeautifulSoup
import os

TEMU_COOKIE = os.getenv("TEMU_COOKIE", "")
BLUE_COOKIE = os.getenv("BLUE_COOKIE", "")

headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": TEMU_COOKIE
}

def search_temu(keyword: str):
    url = f"https://www.temu.com/api/search?q={keyword}"
    response = requests.get(url, headers=headers)
    return response.json()

def search_blue(keyword: str):
    url = f"https://www.blueimagesite.com/search?q={keyword}"
    headers["Cookie"] = BLUE_COOKIE
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for img in soup.select("img.search-result"):
        results.append({
            "src": img["src"],
            "alt": img.get("alt", "")
        })
    return results
