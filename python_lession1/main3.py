from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# 指定你默认的 Chrome 用户数据目录（替换为你的路径）
chrome_options.add_argument("--user-data-dir=/Users/chengzongxin/Library/Application Support/Google/Chrome/Profile 2")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.redbubble.com/shop?query=bags&ref=search_box")