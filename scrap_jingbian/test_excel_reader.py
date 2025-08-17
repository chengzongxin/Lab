#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel读取功能
用于验证Excel文件是否能正确读取
"""

import pandas as pd
import os

def test_excel_reading():
    """测试Excel文件读取功能"""
    try:
        # 查找Excel文件
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
        if not excel_files:
            print("当前目录下没有找到Excel文件")
            return
        
        print(f"找到以下Excel文件:")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        
        # 测试第一个文件
        test_file = excel_files[0]
        print(f"\n正在测试文件: {test_file}")
        
        # 读取Excel文件
        df = pd.read_excel(test_file)
        
        print(f"\n文件信息:")
        print(f"总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        
        print(f"\n列名:")
        for i, col in enumerate(df.columns):
            print(f"第{i+1}列: {col}")
        
        print(f"\n前5行数据预览:")
        print(df.head())
        
        # 检查第二列
        if len(df.columns) >= 2:
            second_col = df.iloc[:, 1]
            print(f"\n第二列数据统计:")
            print(f"非空值数量: {second_col.count()}")
            print(f"前5个值:")
            for i, value in enumerate(second_col.head()):
                print(f"  {i+1}. {value}")
        else:
            print("\n警告: 文件列数不足，无法读取第二列")
        
        print(f"\nExcel文件读取测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_excel_reading()
