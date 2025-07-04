#!/usr/bin/env python3
"""
性能测试脚本 - 比较单线程和多线程下架性能
"""

import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_single_thread_performance(product_ids, max_threads=1):
    """测试单线程性能"""
    print(f"\n=== 单线程测试（{max_threads}个线程）===")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/temu/seller/offline",
            json={
                "productIds": product_ids,
                "max_threads": max_threads
            },
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            success_count = data.get("summary", {}).get("success", 0)
            total_count = data.get("summary", {}).get("total", 0)
            thread_info = data.get("threadInfo", {})
            
            print(f"✓ 测试完成")
            print(f"  处理时间: {duration:.2f} 秒")
            print(f"  成功数量: {success_count}/{total_count}")
            print(f"  线程信息: {thread_info}")
            
            return {
                "duration": duration,
                "success_count": success_count,
                "total_count": total_count,
                "threads": thread_info.get("actualThreads", 1)
            }
        else:
            print(f"✗ 请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return None

def compare_performance():
    """比较不同线程数的性能"""
    print("=== 批量下架性能测试 ===")
    
    # 测试用的商品ID（请根据实际情况调整）
    test_product_ids = [
        77116192956, 45277466416, 92298058298, 37182111332,
        51988942280, 93401832635, 83724073267, 68180230053
    ]
    
    print(f"测试商品数量: {len(test_product_ids)}")
    print(f"测试商品ID: {test_product_ids}")
    
    # 测试不同线程数
    thread_configs = [1, 2, 4, 8]
    results = []
    
    for threads in thread_configs:
        result = test_single_thread_performance(test_product_ids, threads)
        if result:
            results.append({
                "threads": threads,
                **result
            })
    
    # 输出性能对比
    print("\n=== 性能对比结果 ===")
    print("线程数\t处理时间(秒)\t成功率\t\t效率提升")
    print("-" * 50)
    
    baseline_time = None
    for result in results:
        threads = result["threads"]
        duration = result["duration"]
        success_rate = f"{result['success_count']}/{result['total_count']}"
        
        if baseline_time is None:
            baseline_time = duration
            efficiency = "基准"
        else:
            efficiency = f"{baseline_time/duration:.2f}x"
        
        print(f"{threads}\t{duration:.2f}\t\t{success_rate}\t\t{efficiency}")
    
    # 推荐配置
    if results:
        best_result = min(results, key=lambda x: x["duration"])
        print(f"\n推荐配置: {best_result['threads']} 个线程")
        print(f"最佳性能: {best_result['duration']:.2f} 秒")

if __name__ == "__main__":
    compare_performance() 