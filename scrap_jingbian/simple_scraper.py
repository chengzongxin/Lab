#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版百度健康爬虫程序
用于测试基本功能
"""

import pandas as pd
import time
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def read_excel_titles(excel_file):
    """读取Excel文件第二列的文章标题"""
    try:
        df = pd.read_excel(excel_file)
        if len(df.columns) < 2:
            logging.error(f"Excel文件列数不足，当前只有{len(df.columns)}列")
            return []
        
        titles = df.iloc[:, 1].dropna().tolist()
        logging.info(f"成功读取{len(titles)}个文章标题")
        return titles
    except Exception as e:
        logging.error(f"读取Excel文件失败: {e}")
        return []

def create_sample_results(titles, max_count=5):
    """创建示例结果（用于测试）"""
    results = []
    
    for i, title in enumerate(titles[:max_count]):
        # 模拟爬取结果
        result = {
            'search_title': title,
            'title': f"百度健康 - {title}",
            'doctor': f"张医生{i+1}",
            'position': f"主任医师",
            'department': "泌尿外科"
        }
        results.append(result)
        logging.info(f"模拟爬取: {title}")
        time.sleep(0.5)  # 模拟延迟
    
    return results

def save_to_excel(data, filename=None):
    """保存结果到Excel文件"""
    try:
        if not filename:
            today = datetime.now().strftime("%Y%m%d")
            filename = f"百度健康爬取结果_{today}.xlsx"
        
        df = pd.DataFrame(data)
        columns_order = ['search_title', 'title', 'doctor', 'position', 'department']
        df = df.reindex(columns=columns_order)
        
        df.to_excel(filename, index=False, engine='openpyxl')
        logging.info(f"结果已保存到: {filename}")
        return filename
    except Exception as e:
        logging.error(f"保存Excel文件失败: {e}")
        return None

def main():
    """主函数"""
    try:
        # 查找Excel文件
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
        if not excel_files:
            print("当前目录下没有找到Excel文件")
            return
        
        print(f"找到以下Excel文件:")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        
        # 选择文件
        if len(excel_files) == 1:
            selected_file = excel_files[0]
            print(f"自动选择: {selected_file}")
        else:
            while True:
                try:
                    choice = int(input(f"请选择要处理的文件 (1-{len(excel_files)}): ")) - 1
                    if 0 <= choice < len(excel_files):
                        selected_file = excel_files[choice]
                        break
                    else:
                        print("选择无效，请重新输入")
                except ValueError:
                    print("请输入有效的数字")
        
        print(f"开始处理文件: {selected_file}")
        
        # 读取标题
        titles = read_excel_titles(selected_file)
        if not titles:
            print("没有找到可用的标题")
            return
        
        print(f"找到{len(titles)}个标题，将处理前5个进行测试")
        
        # 创建示例结果
        results = create_sample_results(titles, max_count=5)
        
        # 保存结果
        if results:
            filename = save_to_excel(results)
            print(f"测试完成！结果已保存到: {filename}")
            print(f"共处理{len(results)}个标题")
        else:
            print("没有生成任何结果")
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
