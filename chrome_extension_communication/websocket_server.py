#!/usr/bin/env python3
"""
WebSocket服务端 - 用于与Chrome插件通信 (非阻塞版本)
支持后端主动发送命令到Chrome插件
"""
import asyncio
import websockets
import json
import sys
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor

# 存储所有连接的客户端
connected_clients = set()
# 命令队列：用于主线程向WebSocket线程发送命令
command_queue = queue.Queue()
# 响应队列：用于接收来自插件的响应
response_queue = queue.Queue()

async def handle_client(websocket, path):
    """
    处理单个客户端连接
    websocket: WebSocket连接对象
    path: 连接路径
    """
    # 将新客户端添加到连接集合中
    connected_clients.add(websocket)
    print(f"新客户端已连接，当前连接数: {len(connected_clients)}")
    
    try:
        # 持续监听客户端消息
        async for message in websocket:
            try:
                # 解析收到的JSON消息
                data = json.loads(message)
                print(f"收到消息: {data}")
                
                # 根据消息类型处理不同的逻辑
                if data.get('type') == 'greeting':
                    # 回应问候消息
                    response = {
                        'type': 'response',
                        'message': f"你好！我收到了你的消息: {data.get('content', '')}"
                    }
                elif data.get('type') == 'calculation':
                    # 处理计算请求
                    try:
                        num1 = data.get('num1', 0)
                        num2 = data.get('num2', 0)
                        operation = data.get('operation', '+')
                        
                        if operation == '+':
                            result = num1 + num2
                        elif operation == '-':
                            result = num1 - num2
                        elif operation == '*':
                            result = num1 * num2
                        elif operation == '/':
                            result = num1 / num2 if num2 != 0 else "除数不能为0"
                        else:
                            result = "不支持的操作"
                            
                        response = {
                            'type': 'calculation_result',
                            'result': result
                        }
                    except Exception as e:
                        response = {
                            'type': 'error',
                            'message': f"计算错误: {str(e)}"
                        }
                elif data.get('type') == 'query_headers':
                    # 处理请求头查询
                    query_type = data.get('query_type', 'all')
                    
                    if query_type == 'by_name':
                        header_name = data.get('header_name', '')
                        header_value = data.get('header_value', '')
                        response = {
                            'type': 'header_query_result',
                            'query_type': 'by_name',
                            'header_name': header_name,
                            'header_value': header_value,
                            'message': f"查询包含请求头 '{header_name}' 的请求",
                            'instructions': "请在Chrome插件中使用'搜索'功能查看结果"
                        }
                    elif query_type == 'by_domain':
                        domain = data.get('domain', '')
                        response = {
                            'type': 'header_query_result',
                            'query_type': 'by_domain',
                            'domain': domain,
                            'message': f"查询域名 '{domain}' 的所有请求",
                            'instructions': "请在Chrome插件中使用'按域名搜索'功能查看结果"
                        }
                    elif query_type == 'statistics':
                        response = {
                            'type': 'header_query_result',
                            'query_type': 'statistics',
                            'message': "请求拦截统计信息查询",
                            'instructions': "请在Chrome插件中点击'统计信息'按钮查看详细数据"
                        }
                    else:
                        response = {
                            'type': 'header_query_result',
                            'query_type': 'all',
                            'message': "获取所有拦截的请求",
                            'instructions': "请在Chrome插件中点击'查看拦截请求'按钮查看数据"
                        }
                elif data.get('type') == 'command_response':
                    # 处理来自插件的命令响应
                    print(f"收到插件响应: {data.get('data', {})}")
                    response_queue.put(data)
                    # 不需要回复，只记录响应
                    continue
                elif data.get('type') == 'text':
                    # 处理自定义文本消息
                    text_content = data.get('content', '')
                    response = {
                        'type': 'response',
                        'message': f"收到文本消息: {text_content}",
                        'echo': text_content
                    }
                else:
                    # 默认回应
                    response = {
                        'type': 'echo',
                        'original_message': data,
                        'timestamp': str(asyncio.get_event_loop().time())
                    }
                
                # 发送回应消息
                await websocket.send(json.dumps(response, ensure_ascii=False))
                print(f"已发送回应: {response}")
                
            except json.JSONDecodeError:
                # 处理无效的JSON消息
                error_response = {
                    'type': 'error',
                    'message': '无效的JSON格式'
                }
                await websocket.send(json.dumps(error_response, ensure_ascii=False))
                
    except websockets.exceptions.ConnectionClosed:
        print("客户端连接已断开")
    except Exception as e:
        print(f"处理客户端时发生错误: {e}")
    finally:
        # 从连接集合中移除客户端
        connected_clients.discard(websocket)
        print(f"客户端已断开，当前连接数: {len(connected_clients)}")

async def broadcast_message(message):
    """
    向所有连接的客户端广播消息
    """
    if connected_clients:
        # 创建发送任务列表
        tasks = [client.send(json.dumps(message, ensure_ascii=False)) for client in connected_clients]
        # 并发发送给所有客户端
        await asyncio.gather(*tasks, return_exceptions=True)

async def send_command_to_plugin(command):
    """
    向Chrome插件发送命令
    """
    if connected_clients:
        message = {
            'type': 'backend_command',
            'command': command.get('action'),
            'params': command.get('params', {}),
            'command_id': command.get('command_id', f"cmd_{int(time.time())}")
        }
        await broadcast_message(message)
        return True
    return False

async def command_handler():
    """
    处理来自主线程的命令队列
    """
    while True:
        try:
            # 非阻塞检查命令队列
            command = command_queue.get_nowait()
            success = await send_command_to_plugin(command)
            if not success:
                print("❌ 没有连接的Chrome插件")
        except queue.Empty:
            # 队列为空，等待一下再检查
            await asyncio.sleep(0.1)

async def websocket_server():
    """
    WebSocket服务器主函数
    """
    # 服务器配置
    host = "localhost"
    port = 8765
    
    print(f"🚀 WebSocket服务器启动中...")
    print(f"📡 监听地址: ws://{host}:{port}")
    
    # 启动WebSocket服务器和命令处理器
    async with websockets.serve(handle_client, host, port):
        # 同时运行命令处理器
        await command_handler()

def run_websocket_server():
    """
    在单独线程中运行WebSocket服务器
    """
    asyncio.run(websocket_server())

def wait_for_response(timeout=10):
    """
    等待插件响应
    """
    try:
        response = response_queue.get(timeout=timeout)
        return response.get('data', {})
    except queue.Empty:
        return None

def send_command(action, params=None):
    """
    发送命令到Chrome插件并等待响应
    """
    if not connected_clients:
        print("❌ 没有连接的Chrome插件")
        return None
    
    command_id = f"cmd_{int(time.time())}"
    command = {
        'action': action,
        'params': params or {},
        'command_id': command_id
    }
    
    # 清空响应队列
    while not response_queue.empty():
        response_queue.get_nowait()
    
    # 发送命令
    command_queue.put(command)
    print(f"📤 发送命令: {action}")
    
    # 等待响应
    print("⏳ 等待插件响应...")
    response = wait_for_response()
    
    if response:
        print(f"✅ 收到响应:")
        return response
    else:
        print("❌ 响应超时")
        return None

def get_domain_cookies(domain):
    """
    获取指定域名的Cookie
    """
    print(f"\n🍪 获取域名 '{domain}' 的Cookie...")
    response = send_command('get_cookies_by_domain', {'domain': domain})
    
    if response and response.get('success'):
        cookies = response.get('cookies', [])
        print(f"📊 找到 {len(cookies)} 个Cookie:")
        for cookie in cookies:
            print(f"  - {cookie.get('name', 'Unknown')}: {cookie.get('value', '')[:50]}...")
        
        # 打印cookie，以;拼接
        formatted_cookies = "; ".join([f"{cookie.get('name', '')}={cookie.get('value', '')}" for cookie in cookies])
        print(f"🍪 格式化后的Cookie: {formatted_cookies}")
    else:
        print("❌ 获取Cookie失败")

def get_domain_requests(domain):
    """
    获取指定域名的拦截请求
    """
    print(f"\n🕵️ 获取域名 '{domain}' 的拦截请求...")
    response = send_command('get_requests_by_domain', {'domain': domain})
    
    if response and response.get('success'):
        requests = response.get('requests', [])
        print(f"📊 找到 {len(requests)} 个请求:")
        for req in requests[:10]:  # 只显示前10个
            print(f"  - {req.get('method', 'GET')} {req.get('path', '')} | 请求头: {len(req.get('headers', []))}个")
        if len(requests) > 10:
            print(f"  ... 还有 {len(requests) - 10} 个请求")
    else:
        print("❌ 获取请求失败")

def get_requests_by_header(header_name, header_value=None):
    """
    根据请求头查询拦截的请求
    """
    print(f"\n🔍 查询包含请求头 '{header_name}' 的请求...")
    params = {'headerName': header_name}
    if header_value:
        params['headerValue'] = header_value
    
    response = send_command('find_requests_by_header', params)
    
    if response and response.get('success'):
        requests = response.get('requests', [])
        print(f"📊 找到 {len(requests)} 个匹配的请求:")
        for req in requests[:10]:
            print(f"  - {req.get('method', 'GET')} {req.get('domain', '')} | {req.get('timestamp', '')}")
    else:
        print("❌ 查询请求失败")

def command_line_interface():
    """
    命令行交互界面
    """
    print("\n" + "="*60)
    print("🎮 Chrome插件后端控制台")
    print("="*60)
    print("可用命令:")
    print("  1. cookie <域名>          - 获取指定域名的Cookie")
    print("  2. requests <域名>        - 获取指定域名的拦截请求") 
    print("  3. header <请求头名称>     - 查询包含指定请求头的请求")
    print("  4. status                - 查看连接状态")
    print("  5. quit/exit             - 退出程序")
    print("="*60)
    
    while True:
        try:
            cmd = input("\n💬 请输入命令: ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            action = parts[0].lower()
            
            if action in ['quit', 'exit']:
                print("👋 再见!")
                break
            elif action == 'status':
                print(f"📊 连接状态: {len(connected_clients)} 个Chrome插件已连接")
            elif action == 'cookie' and len(parts) > 1:
                get_domain_cookies(parts[1])
            elif action == 'requests' and len(parts) > 1:
                get_domain_requests(parts[1])
            elif action == 'header' and len(parts) > 1:
                header_value = parts[2] if len(parts) > 2 else None
                get_requests_by_header(parts[1], header_value)
            else:
                print("❌ 无效命令，请查看帮助信息")
                
        except KeyboardInterrupt:
            print("\n👋 程序已终止")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def main():
    """
    主函数 - 启动WebSocket服务器和命令行界面
    """
    # 在后台线程启动WebSocket服务器
    server_thread = threading.Thread(target=run_websocket_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(1)
    print("✅ WebSocket服务器已在后台启动")
    
    # 启动命令行界面
    command_line_interface()

if __name__ == "__main__":
    try:
        # 运行主函数
        main()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1) 