import requests
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional, Any
import threading
import platform
import subprocess
import os
from ..system_config.config import SystemConfig
from ..logger.logger import Logger

class NetworkRequest:
    """网络请求封装类"""
    
    def __init__(self):
        self.config = SystemConfig()
        self.logger = Logger()
        self.session = requests.Session()
        # 用于存储根窗口的引用
        self._root_window = None
        self._is_macos = platform.system() == "Darwin"
        self._is_windows = platform.system() == "Windows"
        
    def _show_config_error_dialog(self, error_msg: str):
        """显示配置错误弹窗 - 跨平台兼容"""
        try:
            if self._is_macos:
                # macOS: 使用系统原生通知
                self._show_macos_notification(error_msg)
            elif self._is_windows:
                # Windows: 使用 tkinter 弹窗
                self._show_windows_dialog(error_msg)
            else:
                # 其他系统: 记录日志
                self.logger.error(f"配置错误: {error_msg}")
                self.logger.error("请前往'系统配置'页面检查Cookie和MallID设置")
                
        except Exception as e:
            # 如果弹窗失败，至少记录日志
            self.logger.error(f"显示配置错误弹窗失败: {str(e)}")
            self.logger.error(f"原始错误信息: {error_msg}")
            self.logger.error("请前往'系统配置'页面检查Cookie和MallID设置")
            
    def _show_macos_notification(self, error_msg: str):
        """在 macOS 上显示系统原生通知"""
        try:
            # 构建通知消息
            title = "配置错误"
            message = f"{error_msg}\n\n请前往'系统配置'页面检查Cookie和MallID设置"
            
            # 使用 osascript 调用系统通知
            script = f'''
            display notification "{message}" with title "{title}" sound name "Glass"
            '''
            
            # 执行 AppleScript
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                self.logger.error(f"macOS 通知失败: {result.stderr}")
                # 如果通知失败，记录日志
                self.logger.error(f"配置错误: {error_msg}")
                self.logger.error("请前往'系统配置'页面检查Cookie和MallID设置")
            else:
                self.logger.info("macOS 通知已发送")
                
        except subprocess.TimeoutExpired:
            self.logger.error("macOS 通知超时")
            self.logger.error(f"配置错误: {error_msg}")
        except Exception as e:
            self.logger.error(f"macOS 通知异常: {str(e)}")
            self.logger.error(f"配置错误: {error_msg}")
            
    def _show_windows_dialog(self, error_msg: str):
        """在 Windows 上显示 tkinter 弹窗"""
        try:
            # 创建隐藏的根窗口来显示弹窗
            if self._root_window is None:
                self._root_window = tk.Tk()
                self._root_window.withdraw()  # 隐藏主窗口
                self._root_window.attributes('-topmost', True)  # 置顶显示
                
                # 设置窗口关闭时的清理
                def on_closing():
                    self._root_window.destroy()
                    self._root_window = None
                
                self._root_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # 显示错误弹窗
            messagebox.showerror("配置错误", f"{error_msg}\n\n请前往'系统配置'页面检查Cookie和MallID设置")
            
        except Exception as e:
            self.logger.error(f"Windows 弹窗失败: {str(e)}")
            self.logger.error(f"配置错误: {error_msg}")
            # 清理根窗口引用
            if self._root_window:
                try:
                    self._root_window.destroy()
                except:
                    pass
                self._root_window = None
        
    def _get_headers(self, use_compliance: bool = False) -> Dict[str, str]:
        """获取请求头"""
        cookie = self.config.get_compliance_cookie() if use_compliance else self.config.get_seller_cookie()
        mallid = self.config.get_mallid()
        return {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "anti-content": "",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "cookie": cookie,
            "mallid": mallid,
            "origin": "https://seller.kuajingmaihuo.com",
            "referer": "https://seller.kuajingmaihuo.com/goods/product/list",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
        }
        
    def get(self, url: str, params: Optional[Dict] = None, use_compliance: bool = False) -> Optional[Dict]:
        """发送GET请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            self.logger.info(f"GET请求成功")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = f"GET请求失败: 403 Forbidden - 访问被拒绝\n"
                error_msg += f"可能原因：\n"
                error_msg += f"1. Cookie已过期或无效\n"
                error_msg += f"2. MallID配置错误\n"
                error_msg += f"3. 权限不足\n"
                error_msg += f"请检查系统配置中的Cookie和MallID设置"
                self.logger.error(error_msg)
                # 直接显示弹窗
                self._show_config_error_dialog(error_msg)
                return None
            else:
                self.logger.error(f"GET请求失败: HTTP {e.response.status_code} - {str(e)}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET请求失败: {str(e)}")
            return None
            
    def post(self, url: str, data: Dict[str, Any], use_compliance: bool = False) -> Optional[Dict]:
        """发送POST请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            self.logger.info(f"POST请求成功")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = f"POST请求失败: 403 Forbidden - 访问被拒绝\n"
                error_msg += f"可能原因：\n"
                error_msg += f"1. Cookie已过期或无效\n"
                error_msg += f"2. MallID配置错误\n"
                error_msg += f"3. 权限不足\n"
                error_msg += f"请检查系统配置中的Cookie和MallID设置"
                self.logger.error(error_msg)
                # 直接显示弹窗
                self._show_config_error_dialog(error_msg)
                return None
            else:
                self.logger.error(f"POST请求失败: HTTP {e.response.status_code} - {str(e)}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST请求失败: {str(e)}")
            return None
            
    def put(self, url: str, data: Dict[str, Any], use_compliance: bool = False) -> Optional[Dict]:
        """发送PUT请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.put(url, json=data, headers=headers)
            response.raise_for_status()
            self.logger.info(f"PUT请求成功")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = f"PUT请求失败: 403 Forbidden - 访问被拒绝\n"
                error_msg += f"可能原因：\n"
                error_msg += f"1. Cookie已过期或无效\n"
                error_msg += f"2. MallID配置错误\n"
                error_msg += f"3. 权限不足\n"
                error_msg += f"请检查系统配置中的Cookie和MallID设置"
                self.logger.error(error_msg)
                # 直接显示弹窗
                self._show_config_error_dialog(error_msg)
                return None
            else:
                self.logger.error(f"PUT请求失败: HTTP {e.response.status_code} - {str(e)}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PUT请求失败: {str(e)}")
            return None
            
    def delete(self, url: str, use_compliance: bool = False) -> Optional[Dict]:
        """发送DELETE请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.delete(url, headers=headers)
            response.raise_for_status()
            self.logger.info(f"DELETE请求成功")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = f"DELETE请求失败: 403 Forbidden - 访问被拒绝\n"
                error_msg += f"可能原因：\n"
                error_msg += f"1. Cookie已过期或无效\n"
                error_msg += f"2. MallID配置错误\n"
                error_msg += f"3. 权限不足\n"
                error_msg += f"请检查系统配置中的Cookie和MallID设置"
                self.logger.error(error_msg)
                # 直接显示弹窗
                self._show_config_error_dialog(error_msg)
                return None
            else:
                self.logger.error(f"DELETE请求失败: HTTP {e.response.status_code} - {str(e)}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE请求失败: {str(e)}")
            return None
            
    def download_file(self, url: str, save_path: str, use_compliance: bool = False) -> bool:
        """下载文件"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"文件下载失败: {str(e)}")
            return False
            
    def cleanup(self):
        """清理资源，特别是 tkinter 窗口"""
        try:
            if self._root_window:
                self._root_window.destroy()
                self._root_window = None
        except Exception as e:
            self.logger.error(f"清理资源时出错: {str(e)}") 