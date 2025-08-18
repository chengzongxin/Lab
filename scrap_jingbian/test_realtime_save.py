#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实时保存功能
模拟爬虫程序实时保存数据到Excel
"""

import pandas as pd
import os
from datetime import datetime
import time

def test_realtime_save():
    """测试实时保存功能"""
    
    print("=== 测试实时保存功能 ===\n")
    
    # 模拟爬虫数据
    test_data = [
        {
            'search_title': '牙疼怎么办',
            'title': '牙疼的常见原因和治疗方法',
            'doctor': '张医生',
            'position': '主任医师',
            'department': '口腔科',
            'content': '牙疼是一种常见的口腔疾病症状...'
        },
        {
            'search_title': '头痛怎么缓解',
            'title': '头痛的原因和缓解方法',
            'doctor': '李医生',
            'position': '副主任医师',
            'department': '神经内科',
            'content': '头痛可能由多种原因引起...'
        },
        {
            'search_title': '感冒吃什么药',
            'title': '感冒的药物治疗建议',
            'doctor': '王医生',
            'position': '主治医师',
            'department': '呼吸内科',
            'content': '感冒是一种常见的呼吸道疾病...'
        }
    ]
    
    # 模拟实时保存过程
    excel_file = None
    
    for i, data in enumerate(test_data, 1):
        print(f"正在处理第{i}条数据: {data['search_title']}")
        
        try:
            if not excel_file:
                # 第一次写入，创建新文件
                today = datetime.now().strftime("%Y%m%d")
                excel_file = f"测试实时保存_{today}.xlsx"
                
                # 创建包含新数据的DataFrame
                df = pd.DataFrame([data])
                
                # 重新排列列顺序
                columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                df = df.reindex(columns=columns_order)
                
                # 保存到Excel
                df.to_excel(excel_file, index=False, engine='openpyxl')
                print(f"   创建新Excel文件并保存第一条数据: {excel_file}")
                
            else:
                # 追加到现有文件
                try:
                    # 读取现有数据
                    existing_df = pd.read_excel(excel_file)
                    print(f"   现有文件包含{len(existing_df)}条数据")
                    
                    # 添加新数据
                    new_df = pd.DataFrame([data])
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                    
                    # 重新排列列顺序
                    columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                    updated_df = updated_df.reindex(columns=columns_order)
                    
                    # 保存更新后的数据
                    updated_df.to_excel(excel_file, index=False, engine='openpyxl')
                    print(f"   成功追加数据到Excel文件，现在共有{len(updated_df)}条数据")
                    
                except FileNotFoundError:
                    print("   Excel文件不存在，重新创建...")
                    excel_file = None
                    continue
                    
        except Exception as e:
            print(f"   保存数据失败: {e}")
            # 如果保存失败，尝试保存到备用文件
            try:
                backup_file = f"备用文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df = pd.DataFrame([data])
                columns_order = ['search_title', 'title', 'doctor', 'position', 'department', 'content']
                df = df.reindex(columns=columns_order)
                df.to_excel(backup_file, index=False, engine='openpyxl')
                print(f"   数据已保存到备用文件: {backup_file}")
            except Exception as backup_error:
                print(f"   保存到备用文件也失败: {backup_error}")
        
        # 模拟处理时间
        time.sleep(1)
        print()
    
    # 验证最终文件
    if excel_file and os.path.exists(excel_file):
        try:
            final_df = pd.read_excel(excel_file)
            print(f"=== 最终验证 ===")
            print(f"Excel文件: {excel_file}")
            print(f"总数据条数: {len(final_df)}")
            print(f"列名: {list(final_df.columns)}")
            print(f"前3行数据预览:")
            print(final_df.head(3).to_string(index=False))
            
            # 检查数据完整性
            expected_titles = [data['search_title'] for data in test_data]
            actual_titles = final_df['search_title'].tolist()
            
            if expected_titles == actual_titles:
                print("\n✅ 数据完整性验证通过！")
            else:
                print("\n❌ 数据完整性验证失败！")
                print(f"期望的标题: {expected_titles}")
                print(f"实际的标题: {actual_titles}")
                
        except Exception as e:
            print(f"验证最终文件失败: {e}")
    else:
        print("❌ 最终Excel文件不存在或无法访问")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_realtime_save()
