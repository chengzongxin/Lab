"""
Redbubble爬虫启动脚本
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from spiders.product_spider import RedbubbleSpider

if __name__ == "__main__":
    spider = RedbubbleSpider()
    spider.crawl(1, 3)  # 测试爬取前3页 