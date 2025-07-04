#!/usr/bin/env python3
"""
测试缓存功能的脚本
"""

import json
import os
import time

def test_cache_functionality():
    """测试缓存功能"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    print("=== 缓存功能测试 ===")
    
    # 1. 检查配置文件是否存在
    if os.path.exists(config_path):
        print("✓ 配置文件存在")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 2. 检查缓存字段
        cached_parent_msg_id = config.get("parent_msg_id")
        cached_tool_id = config.get("tool_id")
        cached_timestamp = config.get("parent_msg_timestamp")
        
        print(f"缓存数据:")
        print(f"  parent_msg_id: {cached_parent_msg_id}")
        print(f"  tool_id: {cached_tool_id}")
        print(f"  timestamp: {cached_timestamp}")
        
        # 3. 检查缓存是否有效
        cache_valid = False
        if cached_parent_msg_id and cached_tool_id and cached_timestamp:
            try:
                cache_time = int(cached_timestamp)
                current_time = int(time.time() * 1000)  # 毫秒时间戳
                time_diff = current_time - cache_time
                hours_diff = time_diff / (1000 * 60 * 60)
                
                print(f"缓存时间差: {hours_diff:.2f} 小时")
                
                if time_diff < 24 * 60 * 60 * 1000:  # 24小时
                    cache_valid = True
                    print("✓ 缓存有效（未过期）")
                else:
                    print("✗ 缓存已过期")
            except Exception as e:
                print(f"✗ 缓存时间戳解析失败: {e}")
        else:
            print("✗ 缓存数据不完整")
        
        return cache_valid
    else:
        print("✗ 配置文件不存在")
        return False

def simulate_config_change():
    """模拟配置更改"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    print("\n=== 模拟配置更改 ===")
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 保存原始数据
        original_config = config.copy()
        
        # 模拟配置更改
        config["seller_cookie"] = "new_cookie_value"
        
        # 清除缓存数据
        config["parent_msg_id"] = None
        config["parent_msg_timestamp"] = None
        config["tool_id"] = None
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✓ 已模拟配置更改并清除缓存")
        
        # 恢复原始配置
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(original_config, f, ensure_ascii=False, indent=2)
        
        print("✓ 已恢复原始配置")

if __name__ == "__main__":
    # 测试缓存功能
    cache_valid = test_cache_functionality()
    
    # 模拟配置更改
    simulate_config_change()
    
    print("\n=== 测试完成 ===")
    print("缓存功能测试完成，请检查上述输出结果。") 