"""
配置文件
"""
import os
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 基础URL
BASE_URL = "https://www.redbubble.com"

# 数据存储目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products")
os.makedirs(DATA_DIR, exist_ok=True)

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 5      # 重试延迟（秒）

# 爬虫配置
REQUEST_DELAY_MIN = 2  # 请求最小延迟（秒）
REQUEST_DELAY_MAX = 5  # 请求最大延迟（秒）
PAGE_DELAY_MIN = 5    # 页面间最小延迟（秒）
PAGE_DELAY_MAX = 10   # 页面间最大延迟（秒）

# 数据存储配置
CSV_FILENAME = "redbubble_products.csv"
JSON_FILENAME = "redbubble_products.json"

# 用户代理
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# 初始化Cookie
INITIAL_COOKIES = [
    {
        'name': 'rbzid',
        'value': 'eyJ0eXBlIjoiSldUIiwidHlwZSI6IkpXVCIsImFsZyI6IkhTMjU2In0.eyJpZCI6IjE3MTE0NDQ5NDYtMTU5MjYtNGM5ZC1hMjM1LTY5ZjM5ZjM5ZjM5ZiIsImNsaWVudF9pZCI6InJlZGJ1YmJsZS1jb20iLCJleHAiOjE3MTE0NDg1NDZ9.eyJ0eXBlIjoiSldUIiwidHlwZSI6IkpXVCIsImFsZyI6IkhTMjU2In0.eyJpZCI6IjE3MTE0NDQ5NDYtMTU5MjYtNGM5ZC1hMjM1LTY5ZjM5ZjM5ZjM5ZiIsImNsaWVudF9pZCI6InJlZGJ1YmJsZS1jb20iLCJleHAiOjE3MTE0NDg1NDZ9',
        'domain': '.redbubble.com',
        'path': '/'
    },
    {
        'name': 'rbzidtc',
        'value': 'eyJ0eXBlIjoiSldUIiwidHlwZSI6IkpXVCIsImFsZyI6IkhTMjU2In0.eyJpZCI6IjE3MTE0NDQ5NDYtMTU5MjYtNGM5ZC1hMjM1LTY5ZjM5ZjM5ZjM5ZiIsImNsaWVudF9pZCI6InJlZGJ1YmJsZS1jb20iLCJleHAiOjE3MTE0NDg1NDZ9.eyJ0eXBlIjoiSldUIiwidHlwZSI6IkpXVCIsImFsZyI6IkhTMjU2In0.eyJpZCI6IjE3MTE0NDQ5NDYtMTU5MjYtNGM5ZC1hMjM1LTY5ZjM5ZjM5ZjM5ZiIsImNsaWVudF9pZCI6InJlZGJ1YmJsZS1jb20iLCJleHAiOjE3MTE0NDg1NDZ9',
        'domain': '.redbubble.com',
        'path': '/'
    }
]

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# Cookie配置
COOKIE_STRING = '_tt_enable_cookie=1; _ttp=01JTHHTVWCCCXP6PMT0J4XNVWE_.tt.1; CookieConsent={stamp:%27-1%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27implied%27%2Cver:1%2Cutc:1746493338188%2Ciab2:%27%27%2Cregion:%27TW%27}; _ga=GA1.1.1655618352.1746493338; _gcl_au=1.1.692838628.1746493338; gclid=undefined; _pin_unauth=dWlkPU56WTFZekptTm1FdE9EQTFOeTAwTnpOaUxUaGxORGd0T0RneVpqbGtPREE0T1dWbQ; FPID=FPID2.2.XuRo%2FQTmfbzrBi5ywwmiOQYtyUi2r1rOdmOneXyiPow%3D.1746493338; FPAU=1.2.384362019.1746493339; IR_PI=c3344da5-2a15-11f0-89ea-7b9fb3032810%7C1746493339808; _axwrt=ee44f2d3-8333-4cce-b86b-9959b6dfd0d0; __attentive_id=6c3af7acb62c4127a1cb23621efb11df; __attentive_cco=1746493342982; ajs_anonymous_id=3beb1d65-e1d1-4089-8fed-1d3d3d82c71a; rbVisitorId=01JV4JQZHV3MX9049DS6R0PND3; _fbp=fb.1.1747131832261.1184864979; _rb_session=84375f6a2a85498e88b270cc66e3b11e085dab1fc7a864be4e133e6ed37e0b44; _cfuvid=gJn_c0PPvEGLtDkdZGkcjY0Q87w_rmh6JUCpfK9h79A-1748937848855-0.0.1.1-604800000; IR_gbd=redbubble.com; __attentive_dv=1; open_id_token=eyJhbGciOiJFUzI1NiIsImtpZCI6InJlZGJ1YmJsZS00IiwidHlwIjoiSldUIn0.eyJhbXIiOlsidW5hdXRoZW50aWNhdGVkIl0sImlzcyI6Imh0dHBzOi8vd3d3LnJlZGJ1YmJsZS5jb20iLCJzdWIiOiJyZWRidWJibGU6MDFKVEhIVFFHMkIwS05aSEc0MktFVlZZVEciLCJhdWQiOiJyZWRidWJibGUtc2VydmljZXMiLCJleHAiOjE3NDkwMTcyNDIsImlhdCI6MTc0OTAxNjY0Mn0.m5Yrki13R79kJkwCfdPaXUiW041XiJfIEUq1h6dKzA_nDETzhJRoE0yt3yJuABVVe17vwE8n7wM3jdXqdUp_aA; IR_11754=1749016647417%7C2364980%7C1749016647417%7C%7C; _uetsid=579bff60405111f088ba8f47c802bd7a; _uetvid=c2d199502a1511f0af5f6152cb7ed53a; _attn_=eyJ1Ijoie1wiY29cIjoxNzQ2NDkzMzQyOTgxLFwidW9cIjoxNzQ2NDkzMzQyOTgxLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjZjM2FmN2FjYjYyYzQxMjdhMWNiMjM2MjFlZmIxMWRmXCJ9Iiwic2VzIjoie1widmFsXCI6XCI0OGI1MmQ0ZTBiNzI0ZmQ5YWFlZWJiZDdkYjI2ZDQzYlwiLFwidW9cIjoxNzQ5MDE2NjQ3ODc0LFwiY29cIjoxNzQ5MDE2NjQ3ODc0LFwibWFcIjowLjAyMDgzMzMzMzMzMzMzMzMzMn0ifQ==; FPLC=I3wyjMNmdCsrSbk7V4RKQ3NGd4CrFw2XO2LGTgazBXadS2QepWLbNR3zms6DKDhSv9BZ5Kl0EEbihaxk%2F6bb7UObLoGSrjpCC9I%2Bx7CWxBsbPpd%2FYF8u0WInTxXYzA%3D%3D; ttcsid=1749016646973::T03qjbtr3hgsJNKMTgOL.14.1749016682615; _ga_QB79Q66SYP=GS2.1.s1749016648$o22$g1$t1749016682$j26$l0$h1198121627; ttcsid_CCFTEB3C77U0P3N5IJVG=1749016646973::VOqJ8cEcmogFRrJeDKsR.14.1749016683228; _rb_session4=Q1N1ekFIMnhKYWFQSGQwREpmVDZFMVBVSVpEYnBYa1l5Q1ZwZGNjU0RCcldJYjNqbWhhMkFqQVVtRmNFd2ZVTlQzYzhaZElUMFRpSmQzS0JBN2d5K285ZmlDWnU0TWEzSVFEMkVWby95VFZVckthcjVNaXBjK01NS1Y2OEFtekUtLUVMbDRjbkZYVmF5U0oxQ2M2VkpoK1E9PQ%3D%3D--9005f50d4db964d82e16f417e4635383ec5ffbdd; _dd_s=; ax_visitor=%7B%22firstVisitTs%22%3A1746493342132%2C%22lastVisitTs%22%3A1749007976207%2C%22currentVisitStartTs%22%3A1749016646779%2C%22ts%22%3A1749020257232%2C%22visitCount%22%3A19%7D' 