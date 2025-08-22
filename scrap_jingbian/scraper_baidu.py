import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
import os
import logging
import json
from datetime import datetime

class BaiduHealthScraper:
    def __init__(self, input_file, output_file, checkpoint_file="checkpoint.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        ]
        self.checkpoint = self.load_checkpoint()
        self.data = self.load_excel()

    def load_checkpoint(self):
        """加载断点文件"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"last_index": -1}

    def save_checkpoint(self, index):
        """保存断点"""
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump({"last_index": index}, f, ensure_ascii=False, indent=2)

    def load_excel(self):
        """加载 Excel 文件"""
        df = pd.read_excel(self.input_file)
        df["百度健康链接"] = ""
        df["是否百度健康"] = ""
        df["标题"] = ""
        df["医生"] = ""
        df["职称"] = ""
        df["科室"] = ""
        df["正文"] = ""
        return df

    def save_excel(self):
        """保存 Excel 文件"""
        self.data.to_excel(self.output_file, index=False)

    def random_headers(self):
        return {"User-Agent": random.choice(self.user_agents)}

    def search_baidu(self, title):
        """用 requests 搜索百度"""
        try:
            resp = self.session.get(
                f"https://www.baidu.com/s?wd={title}", 
                headers=self.random_headers(), 
                timeout=10
            )
            if resp.status_code == 200:
                logging.info(f"搜索成功: {title}")
                return resp.text
            else:
                logging.warning(f"搜索失败，状态码: {resp.status_code}")
                return None
        except Exception as e:
            logging.error(f"搜索请求失败: {e}")
            return None

    def find_baidu_health_result(self, html):
        """解析百度搜索结果，查找百度健康链接"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            results = soup.select("div.result, div[class*='result']")

            for res in results:
                source = res.select_one("span.cosc-source-text")
                if source and "百度健康" in source.get_text():
                    a = res.select_one("h3 a")
                    if a and a.get("href"):
                        url = a["href"]
                        logging.info(f"找到百度健康结果: {a.get_text()} - {url}")
                        return url
            return None
        except Exception as e:
            logging.error(f"解析搜索结果失败: {e}")
            return None

    def verify_baidu_health_page(self, url):
        """验证并返回百度健康详情页HTML"""
        try:
            resp = self.session.get(
                url, headers=self.random_headers(), timeout=10, allow_redirects=True
            )
            if resp.status_code == 200 and "health.baidu.com" in resp.url:
                logging.info(f"验证通过: {resp.url}")
                return resp.text
            else:
                logging.warning(f"不是百度健康页面: {resp.url}")
                return None
        except Exception as e:
            logging.error(f"请求详情页失败: {e}")
            return None

    def extract_health_info(self, html):
        """提取百度健康页面信息"""
        info = {"title": "", "doctor": "", "position": "", "department": "", "content": ""}

        try:
            soup = BeautifulSoup(html, "html.parser")

            # 标题
            title = soup.select_one("h1, .title, .article-title")
            if title:
                info["title"] = title.get_text(strip=True)

            # 医生信息
            doctor = soup.select_one("span.index_name__0Yl8k")
            position = soup.select_one("span.index_title__wNRZD")
            dept = soup.select_one("span.index_department__y9DFE")
            if doctor:
                info["doctor"] = doctor.get_text(strip=True)
            if position:
                info["position"] = position.get_text(strip=True)
            if dept:
                info["department"] = dept.get_text(strip=True)

            # 文章内容
            content_parts = [
                p.get_text(strip=True) for p in soup.select("p") if len(p.get_text(strip=True)) > 5
            ]
            info["content"] = "\n\n".join(content_parts)

        except Exception as e:
            logging.error(f"提取健康信息失败: {e}")

        return info

    def process_entry(self, index, title):
        """处理一条数据"""
        try:
            search_html = self.search_baidu(title)
            if not search_html:
                return

            result_url = self.find_baidu_health_result(search_html)
            if not result_url:
                return

            detail_html = self.verify_baidu_health_page(result_url)
            if not detail_html:
                return

            info = self.extract_health_info(detail_html)

            # 写入结果
            self.data.at[index, "百度健康链接"] = result_url
            self.data.at[index, "是否百度健康"] = "是"
            self.data.at[index, "标题"] = info["title"]
            self.data.at[index, "医生"] = info["doctor"]
            self.data.at[index, "职称"] = info["position"]
            self.data.at[index, "科室"] = info["department"]
            self.data.at[index, "正文"] = info["content"]

            self.save_checkpoint(index)

            if index % 5 == 0:
                self.save_excel()

            # 模拟人工延时
            time.sleep(random.uniform(1.5, 4.0))

        except Exception as e:
            logging.error(f"处理 {title} 失败: {e}")

    def run(self):
        """运行主流程"""
        start_index = self.checkpoint["last_index"] + 1
        for i in range(start_index, len(self.data)):
            title = self.data.at[i, "文章标题"]
            logging.info(f"处理第 {i+1}/{len(self.data)} 条: {title}")
            self.process_entry(i, title)

        self.save_excel()
        logging.info("全部完成 ✅")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("scraper.log", encoding="utf-8")]
    )

    scraper = BaiduHealthScraper("E:\Lab\scrap_jingbian\精编词1.xlsx", "output.xlsx")
    scraper.run()
