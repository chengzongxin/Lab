#!/usr/bin/env python3
"""
WebSocket服务端 - 用于与Chrome插件通信
"""
import asyncio
import websockets
import json
import sys

# 存储所有连接的客户端
connected_clients = set()

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

async def main():
    """
    主函数 - 启动WebSocket服务器
    """
    # 服务器配置
    host = "localhost"
    port = 8765
    
    print(f"WebSocket服务器启动中...")
    print(f"监听地址: ws://{host}:{port}")
    print("按 Ctrl+C 停止服务器")
    
    # 启动WebSocket服务器
    async with websockets.serve(handle_client, host, port):
        # 保持服务器运行
        await asyncio.Future()  # 永远运行

if __name__ == "__main__":
    try:
        # 运行主函数
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1) 