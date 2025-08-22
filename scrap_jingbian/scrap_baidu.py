#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度健康爬虫（requests + BeautifulSoup 版，保留原有类架构）
功能：读取Excel文件中的文章标题，搜索百度健康相关内容，爬取医生信息
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 用户代理池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

class BaiduHealthScraper:
    def __init__(self):
        self.results = []

    def get_html(self, url, retries=3):
        """请求页面"""
        for i in range(retries):
            try:
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.text
            except Exception as e:
                logging.warning(f"请求失败 {url}, 重试 {i+1}/{retries}: {e}")
                time.sleep(2)
        return None

    def read_excel_titles(self, excel_file):
        """读取Excel文件第二列的文章标题"""
        df = pd.read_excel(excel_file)
        if len(df.columns) < 2:
            logging.error("Excel文件列数不足")
            return []
        return df.iloc[:, 1].dropna().tolist()

    def search_baidu(self, title, max_pages=3):
        """搜索百度并找到百度健康链接"""
        for page in range(max_pages):
            pn = page * 10
            url = f"https://www.baidu.com/s?wd={title}&pn={pn}"
            html = self.get_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")
            results = soup.select("div.result, div[class*='result']")
            for r in results:
                indicator = r.select_one("span.cosc-source-text")
                if indicator and "百度健康" in indicator.text:
                    link = r.select_one("a")
                    if link and link.get("href"):
                        logging.info(f"找到百度健康链接: {link['href']}")
                        return link["href"]
        return None

    def extract_health_info(self, url):
        """进入百度健康页面提取信息"""
        html = self.get_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")
        info = {
            "title": "",
            "doctor": "",
            "position": "",
            "department": "",
            "content": ""
        }

        # 标题
        title_tag = soup.find("h1") or soup.find("h2")
        if title_tag:
            info["title"] = title_tag.get_text(strip=True)

        # 医生信息
        doctor_name = soup.select_one("span.index_name__0Yl8k")
        doctor_title = soup.select_one("span.index_title__wNRZD")
        doctor_dept = soup.select_one("span.index_department__y9DFE")
        info["doctor"] = doctor_name.get_text(strip=True) if doctor_name else "未找到医生"
        info["position"] = doctor_title.get_text(strip=True) if doctor_title else "未找到职位"
        info["department"] = doctor_dept.get_text(strip=True) if doctor_dept else "未找到科室"

        # 文章内容
        content_divs = soup.select("div[data-anchor-id='content'], div.index_articleWrap__nPJne, div.index_richText__vkNnU")
        if content_divs:
            texts = [div.get_text(" ", strip=True) for div in content_divs]
            info["content"] = "\n".join(texts)
        else:
            p_texts = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 5]
            info["content"] = "\n".join(p_texts)

        return info

    def run(self, excel_file):
        """执行爬取流程"""
        titles = self.read_excel_titles(excel_file)
        for title in titles:
            logging.info(f"搜索标题: {title}")
            link = self.search_baidu(title)
            if link:
                health_info = self.extract_health_info(link)
                if health_info:
                    health_info["search_title"] = title
                    self.results.append(health_info)
                    logging.info(f"成功提取: {health_info['title']} -> {health_info['doctor']}")
            # 加入随机延迟
            time.sleep(random.uniform(1, 3))

        # 保存到Excel
        df = pd.DataFrame(self.results)
        df.to_excel("baidu_health_results.xlsx", index=False)
        logging.info("全部数据已保存 baidu_health_results.xlsx")


if __name__ == "__main__":
    scraper = BaiduHealthScraper()
    scraper.run("你的excel文件路径.xlsx")
