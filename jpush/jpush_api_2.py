try:
    import requests
except ImportError:
    print("请先安装 requests 库：")
    print("1. 创建虚拟环境：python3 -m venv jpush_env")
    print("2. 激活虚拟环境：source jpush_env/bin/activate")
    print("3. 安装依赖：pip install requests")
    exit(1)
    
import json
import base64
import sys
import argparse

class JPushAPI:
    def __init__(self):
        # 配置极光推送的认证信息
        self.app_key = "6c584015f84f593044e28b0b"
        self.master_secret = "584cd454347a8c295ce21188"
        self.push_url = "https://api.jpush.cn/v3/push"
        
        # 生成认证头
        auth_string = f"{self.app_key}:{self.master_secret}"
        self.auth_header = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
    def push_to_all(self, title, content, extras=None):
        """
        推送消息给所有用户
        extras: 字典类型，包含额外的自定义参数
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.auth_header}"
        }
        
        payload = {
            "platform": "all",
            "audience": "all",
            "notification": {
                "android": {
                    "alert": content,
                    "title": title,
                    "extras": extras or {}
                },
                "ios": {
                    "alert": content,
                    "sound": "default",
                    "badge": "+1",
                    "extras": extras or {}
                }
            },
            "options": {
                "apns_production": False  # 默认使用开发环境
            }
        }
        
        try:
            response = requests.post(
                self.push_url, 
                headers=headers,
                data=json.dumps(payload)
            )
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return response.json()
        except Exception as e:
            print(f"推送失败: {str(e)}")
            return None
            
    def push_to_alias(self, alias, title, content, extras=None):
        """
        推送消息给指定别名用户
        extras: 字典类型，包含额外的自定义参数
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.auth_header}"
        }
        
        payload = {
            "platform": "all",
            "audience": {
                "alias": [alias]
            },
            "notification": {
                "android": {
                    "alert": content,
                    "title": title,
                    "extras": extras or {}
                },
                "ios": {
                    "alert": {
                        "title": title,
                        "body": content
                    },
                    "sound": "default",
                    "badge": "+1",
                    "extras": extras or {}
                }
            },
            "options": {
                "apns_production": False  # 默认使用开发环境
            }
        }
        
        try:
            response = requests.post(
                self.push_url, 
                headers=headers,
                data=json.dumps(payload)
            )
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return response.json()
        except Exception as e:
            print(f"推送失败: {str(e)}")
            return None

    def push_to_tag(self, tag, title, content, extras=None):
        """
        推送消息给指定标签用户
        extras: 字典类型，包含额外的自定义参数
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.auth_header}"
        }
        
        payload = {
            "platform": "all",
            "audience": {
                "tag": [tag]
            },
            "notification": {
                "android": {
                    "alert": content,
                    "title": title,
                    "extras": extras or {}
                },
                "ios": {
                    "alert": {
                        "title": title,
                        "body": content
                    },
                    "sound": "default",
                    "badge": "+1",
                    "extras": extras or {}
                }
            },
            "options": {
                "apns_production": False
            }
        }
        
        try:
            response = requests.post(
                self.push_url, 
                headers=headers,
                data=json.dumps(payload)
            )
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return response.json()
        except Exception as e:
            print(f"推送失败: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser(description='极光推送工具 - 应用2')
    parser.add_argument('action', choices=['all', 'alias', 'tag'], help='推送类型：all(所有用户)、alias(指定用户)或tag(标签用户)')
    parser.add_argument('--alias', help='用户别名，当action为alias时必需')
    parser.add_argument('--tag', help='用户标签，当action为tag时必需')
    parser.add_argument('--title', required=True, help='推送标题')
    parser.add_argument('--content', required=True, help='推送内容')
    parser.add_argument('--router-url', help='路由URL')
    parser.add_argument('--audio-url', help='音频URL')
    parser.add_argument('--extra', nargs=2, action='append', help='自定义参数，格式：--extra key value')

    args = parser.parse_args()
    
    # 构建extras字典
    extras = {}
    if args.router_url:
        extras['routerUrl'] = args.router_url
    if args.audio_url:
        extras['audioUrl'] = args.audio_url
    if args.extra:
        for key, value in args.extra:
            extras[key] = value
    
    jpush = JPushAPI()
    
    if args.action == 'all':
        print(f"推送给所有用户: {args.title}")
        jpush.push_to_all(args.title, args.content, extras)
    elif args.action == 'alias':
        if not args.alias:
            parser.error('使用alias操作时必须提供--alias参数')
        print(f"推送给用户 {args.alias}")
        jpush.push_to_alias(args.alias, args.title, args.content, extras)
    elif args.action == 'tag':
        if not args.tag:
            parser.error('使用tag操作时必须提供--tag参数')
        print(f"推送给标签 {args.tag} 的用户")
        jpush.push_to_tag(args.tag, args.title, args.content, extras)

if __name__ == "__main__":
    main() 