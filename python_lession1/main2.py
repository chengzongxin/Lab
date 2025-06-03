from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
    
# 配置Chrome浏览器选项（连接已有浏览器）
chrome_options = Options()
# chrome_options.add_argument("--user-data-dir=/Users/chengzongxin/Library/Application Support/Google/Chrome/Profile 2")
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 调试地址和端口
chrome_options.add_argument("--user-data-dir=/tmp/chrome-debug")  # 必须与手动启动时一致

# 指定ChromeDriver路径（需与浏览器版本匹配）
chromedriver_path = resource_path('chromedriver-mac-arm64/chromedriver')
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1. 确保已有浏览器已打开GitHub登录页面（手动提前打开或通过代码打开）
    # 若需自动打开新标签页：
    # driver.execute_script("window.open('https://github.com/login');")
    # driver.switch_to.window(driver.window_handles[-1])
    
    # 直接访问目标页面（适用于已有浏览器未打开页面的情况）
    # driver.get('https://www.redbubble.com/shop?query=bags&ref=search_box')
    driver.get('https://github.com/login')
    print("打开GitHub登录页面")
    time.sleep(2)

    # 2. 填写用户名和密码（替换为真实账号）
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'login_field'))
    )
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'password'))
    )

    username.click()
    username.send_keys(Keys.CONTROL, 'a')  # 全选
    username.send_keys(Keys.BACKSPACE)     # 删除
    password.click()
    password.send_keys(Keys.CONTROL, 'a')
    password.send_keys(Keys.BACKSPACE)

    time.sleep(3)

    username.send_keys('chengzongxin')  # 用户名
    password.send_keys('cheng1122.')        # 密码
    print("填写登录信息")

    # 3. 点击登录按钮
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'commit'))
    )
    login_button.click()
    print("点击登录按钮")

    # 4. 等待登录成功
    WebDriverWait(driver, 10).until(
        EC.url_contains('github.com/dashboard')  # 登录成功后跳转的页面
    )
    print("登录成功")

    # 5. 在搜索框中输入Python并搜索（使用已有浏览器的搜索框）
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'q'))
    )
    search_box.clear()
    search_box.send_keys('Python')
    search_box.send_keys(Keys.RETURN)
    print("搜索Python相关仓库")

    # 6. 等待搜索结果加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.v-align-middle'))
    )
    print("搜索结果加载完成")

    # 7. 提取前5个搜索结果
    repositories = driver.find_elements(By.CSS_SELECTOR, 'a.v-align-middle')
    for repo in repositories[:5]:
        print(f"仓库名称: {repo.text}")
        print(f"仓库链接: {repo.get_attribute('href')}")
        print("-" * 50)

    # 8. 点击第一个搜索结果
    if repositories:
        repositories[0].click()
        print("点击第一个搜索结果")
        time.sleep(3)

except Exception as e:
    print(f"操作错误: {e}")
finally:
    # 不关闭已有浏览器（仅关闭Selenium控制的会话）
    driver.quit()  # 注意：这会断开连接但不会关闭浏览器窗口
    print("操作结束")