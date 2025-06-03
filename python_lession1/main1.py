import requests
from bs4 import BeautifulSoup
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class DoubanMovieCrawler:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("豆瓣电影Top250爬虫")
        self.root.geometry("800x600")
        
        # 设置窗口样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # 创建界面元素
        self.create_widgets()
        
        # 爬虫相关变量
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        self.is_crawling = False

    def create_widgets(self):
        # 创建开始按钮
        self.start_button = ttk.Button(
            self.root, 
            text="开始爬取", 
            command=self.start_crawling
        )
        self.start_button.pack(pady=10)
        
        # 创建进度条
        self.progress = ttk.Progressbar(
            self.root, 
            orient="horizontal", 
            length=700, 
            mode="determinate"
        )
        self.progress.pack(pady=10)
        
        # 创建状态标签
        self.status_label = ttk.Label(
            self.root, 
            text="准备就绪"
        )
        self.status_label.pack(pady=5)
        
        # 创建结果显示区域
        self.result_text = scrolledtext.ScrolledText(
            self.root, 
            width=80, 
            height=25
        )
        self.result_text.pack(pady=10)

    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.root.update()

    def update_progress(self, value):
        """更新进度条"""
        self.progress["value"] = value
        self.root.update()

    def append_result(self, text):
        """添加结果到文本框"""
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
        self.root.update()

    def crawl_movies(self):
        """爬取电影信息的主要函数"""
        self.is_crawling = True
        self.start_button.config(state="disabled")
        self.result_text.delete(1.0, tk.END)
        all_movies = []
        
        try:
            for start in range(0, 250, 25):  # 爬取10页
                if not self.is_crawling:
                    break
                    
                url = f'https://movie.douban.com/top250?start={start}'
                self.update_status(f"正在爬取第{start//25+1}页...")
                
                response = requests.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    self.append_result(f"第{start//25+1}页请求失败: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                movies = soup.select('div.hd a span')
                
                for movie in movies:
                    all_movies.append(movie.text.strip())
                
                self.append_result(f"已爬取第{start//25+1}页，共{len(movies)}部电影")
                self.update_progress((start + 25) / 250 * 100)
                time.sleep(2)  # 每页间隔2秒
            
            # 显示结果
            self.append_result("\n豆瓣电影Top250（前100部）:")
            for i, movie in enumerate(all_movies[:100], 1):
                self.append_result(f"{i}. {movie}")
                
        except Exception as e:
            self.append_result(f"发生错误: {str(e)}")
        finally:
            self.is_crawling = False
            self.start_button.config(state="normal")
            self.update_status("爬取完成")

    def start_crawling(self):
        """开始爬取按钮的回调函数"""
        if not self.is_crawling:
            # 在新线程中运行爬虫
            thread = threading.Thread(target=self.crawl_movies)
            thread.daemon = True
            thread.start()

    def run(self):
        """运行GUI程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DoubanMovieCrawler()
    app.run()