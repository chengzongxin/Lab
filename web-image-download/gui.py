"""
GUI界面模块
使用tkinter构建用户友好的图形界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from downloader import ImageDownloader
from playwright_downloader import PlaywrightDownloaderSync
from site_detector import SiteDetector


class ImageDownloaderGUI:
    """
    图片下载器GUI类
    提供用户友好的图形界面
    """
    
    def __init__(self, root):
        """
        初始化GUI界面
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("网页图片下载工具")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建下载器实例
        self.downloader = ImageDownloader()
        self.playwright_downloader = PlaywrightDownloaderSync()
        
        # 设置回调函数
        self.downloader.set_callbacks(
            progress_callback=self.update_progress,
            status_callback=self.update_status
        )
        self.playwright_downloader.set_callbacks(
            progress_callback=self.update_progress,
            status_callback=self.update_status
        )
        
        # 下载线程
        self.download_thread = None
        self.is_downloading = False
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """
        创建界面组件
        """
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="网页图片下载工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL输入区域
        url_frame = ttk.LabelFrame(main_frame, text="网站地址", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        # URL输入框
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, 
                                  font=("Arial", 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 示例URL按钮
        example_btn = ttk.Button(url_frame, text="示例", 
                                command=self.insert_example_url)
        example_btn.grid(row=0, column=1)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="下载设置", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 下载路径设置
        path_frame = ttk.Frame(settings_frame)
        path_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Label(path_frame, text="下载路径:").grid(row=0, column=0, sticky=tk.W)
        
        self.path_var = tk.StringVar(value="./downloads")
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        path_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_path)
        browse_btn.grid(row=1, column=1)
        
        # 下载模式选择
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(mode_frame, text="下载模式:").grid(row=0, column=0, sticky=tk.W)
        
        self.mode_var = tk.StringVar(value="auto")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                                 values=["auto", "simple", "advanced"], 
                                 state="readonly", width=15)
        mode_combo.grid(row=0, column=1, padx=(10, 0))
        
        # 模式说明标签
        self.mode_info_label = ttk.Label(mode_frame, text="自动检测网站类型", 
                                        foreground="blue", font=("Arial", 9))
        self.mode_info_label.grid(row=0, column=2, padx=(10, 0))
        
        # 绑定模式选择事件
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # 最大下载数量设置
        limit_frame = ttk.Frame(settings_frame)
        limit_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(limit_frame, text="最大下载数量:").grid(row=0, column=0, sticky=tk.W)
        
        self.limit_var = tk.StringVar(value="")
        limit_entry = ttk.Entry(limit_frame, textvariable=self.limit_var, width=10)
        limit_entry.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(limit_frame, text="(留空表示下载所有图片)").grid(row=0, column=2, padx=(10, 0))
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # 开始下载按钮
        self.download_btn = ttk.Button(button_frame, text="开始下载", 
                                      command=self.start_download, style="Accent.TButton")
        self.download_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 停止下载按钮
        self.stop_btn = ttk.Button(button_frame, text="停止下载", 
                                  command=self.stop_download, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 清空日志按钮
        clear_btn = ttk.Button(button_frame, text="清空日志", command=self.clear_log)
        clear_btn.grid(row=0, column=2)
        
        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        ttk.Label(progress_frame, text="下载进度:").grid(row=0, column=0, sticky=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=1, column=1, padx=(10, 0))
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="下载状态", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # 状态文本框
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, 
                                                    font=("Consolas", 9))
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_frame, text="下载统计", padding="10")
        stats_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # 统计标签
        self.total_label = ttk.Label(stats_frame, text="总图片数: 0")
        self.total_label.grid(row=0, column=0, padx=(0, 20))
        
        self.downloaded_label = ttk.Label(stats_frame, text="已下载: 0")
        self.downloaded_label.grid(row=0, column=1, padx=(0, 20))
        
        self.failed_label = ttk.Label(stats_frame, text="失败: 0")
        self.failed_label.grid(row=0, column=2, padx=(0, 20))
        
        self.size_label = ttk.Label(stats_frame, text="总大小: 0 B")
        self.size_label.grid(row=0, column=3)
        
        # 绑定回车键和URL变化事件
        self.url_entry.bind('<Return>', lambda e: self.start_download())
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        
        # 初始状态
        self.update_status("准备就绪，请输入网站地址开始下载")
        
    def insert_example_url(self):
        """
        插入示例URL
        """
        example_urls = [
            "https://www.python.org",
            "https://github.com",
            "https://stackoverflow.com"
        ]
        
        # 创建示例URL选择窗口
        example_window = tk.Toplevel(self.root)
        example_window.title("选择示例URL")
        example_window.geometry("400x200")
        example_window.transient(self.root)
        example_window.grab_set()
        
        ttk.Label(example_window, text="选择示例网站:").pack(pady=10)
        
        for url in example_urls:
            btn = ttk.Button(example_window, text=url, 
                           command=lambda u=url: self.select_example_url(u, example_window))
            btn.pack(pady=5)
    
    def select_example_url(self, url, window):
        """
        选择示例URL
        
        Args:
            url (str): 选择的URL
            window: 示例窗口
        """
        self.url_var.set(url)
        window.destroy()
    
    def browse_path(self):
        """
        浏览选择下载路径
        """
        path = filedialog.askdirectory(title="选择下载路径")
        if path:
            self.path_var.set(path)
            self.downloader.download_path = path
    
    def start_download(self):
        """
        开始下载
        """
        if self.is_downloading:
            return
        
        # 获取URL
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入网站地址")
            return
        
        # 获取最大下载数量
        max_images = None
        limit_str = self.limit_var.get().strip()
        if limit_str:
            try:
                max_images = int(limit_str)
                if max_images <= 0:
                    messagebox.showerror("错误", "最大下载数量必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "最大下载数量必须是数字")
                return
        
        # 更新下载路径
        self.downloader.download_path = self.path_var.get()
        
        # 更新界面状态
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_var.set(0)
        
        # 清空统计信息
        self.total_label.config(text="总图片数: 0")
        self.downloaded_label.config(text="已下载: 0")
        self.failed_label.config(text="失败: 0")
        self.size_label.config(text="总大小: 0 B")
        
        # 在新线程中执行下载
        self.download_thread = threading.Thread(
            target=self.download_worker,
            args=(url, max_images)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def download_worker(self, url, max_images):
        """
        下载工作线程
        
        Args:
            url (str): 要下载的URL
            max_images (int): 最大下载数量
        """
        try:
            # 获取当前下载器和设置
            downloader, settings = self.get_current_downloader()
            
            # 更新下载路径
            downloader.downloader.download_path = self.path_var.get()
            
            # 执行下载
            if hasattr(downloader, 'download_images_from_url'):
                # Playwright下载器
                scroll_count = settings.get('scroll_count', 5)
                stats = downloader.download_images_from_url(url, max_images, scroll_count)
            else:
                # 普通下载器
                stats = downloader.download_images_from_url(url, max_images)
            
            # 更新统计信息
            self.root.after(0, self.update_stats, stats)
            
        except Exception as e:
            # 显示错误信息
            self.root.after(0, lambda: messagebox.showerror("下载错误", str(e)))
        finally:
            # 恢复界面状态
            self.root.after(0, self.download_finished)
    
    def stop_download(self):
        """
        停止下载
        """
        if self.is_downloading:
            self.is_downloading = False
            self.update_status("正在停止下载...")
            # 注意：这里只是设置标志，实际的停止逻辑需要在下载器中实现
    
    def download_finished(self):
        """
        下载完成后的处理
        """
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status("下载已完成")
    
    def update_progress(self, progress):
        """
        更新进度条
        
        Args:
            progress (float): 进度百分比
        """
        self.root.after(0, lambda: self.progress_var.set(progress))
        self.root.after(0, lambda: self.progress_label.config(text=f"{progress:.1f}%"))
    
    def update_status(self, message):
        """
        更新状态信息
        
        Args:
            message (str): 状态消息
        """
        def update():
            self.status_text.insert(tk.END, f"{message}\n")
            self.status_text.see(tk.END)
        
        self.root.after(0, update)
    
    def update_stats(self, stats):
        """
        更新统计信息
        
        Args:
            stats (dict): 统计信息字典
        """
        self.total_label.config(text=f"总图片数: {stats['total_images']}")
        self.downloaded_label.config(text=f"已下载: {stats['downloaded_images']}")
        self.failed_label.config(text=f"失败: {stats['failed_images']}")
        self.size_label.config(text=f"总大小: {stats['total_size_str']}")
    
    def on_mode_change(self, event=None):
        """
        模式选择变化时的处理
        """
        mode = self.mode_var.get()
        if mode == "auto":
            self.mode_info_label.config(text="自动检测网站类型", foreground="blue")
        elif mode == "simple":
            self.mode_info_label.config(text="简单模式 (Requests)", foreground="green")
        elif mode == "advanced":
            self.mode_info_label.config(text="高级模式 (Playwright)", foreground="orange")
    
    def on_url_change(self, event=None):
        """
        URL变化时的处理
        """
        if self.mode_var.get() == "auto":
            url = self.url_var.get().strip()
            if url and len(url) > 10:  # 避免频繁检测
                try:
                    recommendation = SiteDetector.get_download_recommendation(url)
                    if recommendation['method'] == 'playwright':
                        self.mode_info_label.config(text="推荐: 高级模式", foreground="orange")
                    else:
                        self.mode_info_label.config(text="推荐: 简单模式", foreground="green")
                except:
                    pass
    
    def get_current_downloader(self):
        """
        获取当前使用的下载器
        
        Returns:
            下载器实例
        """
        mode = self.mode_var.get()
        
        if mode == "auto":
            # 自动检测
            url = self.url_var.get().strip()
            if url:
                try:
                    recommendation = SiteDetector.get_download_recommendation(url)
                    if recommendation['method'] == 'playwright':
                        return self.playwright_downloader, recommendation
                    else:
                        return self.downloader, recommendation
                except:
                    # 默认使用高级模式
                    return self.playwright_downloader, {'scroll_count': 5}
            else:
                return self.playwright_downloader, {'scroll_count': 5}
        elif mode == "simple":
            return self.downloader, {'scroll_count': 3}
        else:  # advanced
            return self.playwright_downloader, {'scroll_count': 8}
    
    def clear_log(self):
        """
        清空日志
        """
        self.status_text.delete(1.0, tk.END)
        self.update_status("日志已清空")
    
    def on_closing(self):
        """
        窗口关闭时的处理
        """
        if self.is_downloading:
            if messagebox.askokcancel("退出", "下载正在进行中，确定要退出吗？"):
                self.is_downloading = False
                self.root.destroy()
        else:
            self.root.destroy() 