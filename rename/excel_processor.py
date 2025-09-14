#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel商品名称处理脚本
功能：根据正则表达式匹配商品名称，修改标题并输出到新文件
"""

import pandas as pd
import re
import os
from datetime import datetime
import sys

# ==================== 配置区域 ====================
# 在这里修改配置，无需修改代码逻辑

# Sock Drawstring Tote Sports Scarf Apron a Unisex Cooling

# 要匹配的品类关键词（不区分大小写）
CATEGORY_KEYWORD = "Sports"  # 可以改为 "Backpack", "Tote", "Pouch", "Bag" 等

# 新的品类名称（替换后的名称）
NEW_CATEGORY = "Lite Trend Sports"  # 可以改为其他品类名称

# 输出文件前缀（会自动包含品类关键词）
OUTPUT_PREFIX = "processed"

# ================================================

def process_excel_file(input_file):
    """
    处理Excel文件的主要函数
    
    参数:
        input_file (str): 输入Excel文件路径
    
    返回:
        bool: 处理是否成功
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(input_file):
            print(f"❌ 错误：文件 '{input_file}' 不存在！")
            return False
        
        print(f"📖 正在读取文件：{input_file}")
        
        # 读取Excel文件
        df = pd.read_excel(input_file)
        
        # 检查是否有数据
        if df.empty:
            print("❌ 错误：Excel文件为空！")
            return False
        
        print(f"📊 原始数据行数：{len(df)}")
        
        # 获取第一列的名称（商品名称列）
        first_column = df.columns[0]
        print(f"📝 商品名称列：{first_column}")
        
        # 使用配置区域的品类关键词
        print(f"🔍 匹配品类关键词：{CATEGORY_KEYWORD}")
        
        # 定义正则表达式模式：匹配数字+品类关键词
        # 例如：Fishes 3 Drawstring Bags -> 匹配 "3 Drawstring"
        pattern = rf'(\d+)\s+{re.escape(CATEGORY_KEYWORD)}'
        
        # 创建匹配结果列
        df['匹配结果'] = df[first_column].str.contains(pattern, case=False, na=False)
        
        # 筛选匹配的行
        matched_df = df[df['匹配结果'] == True].copy()
        
        print(f"✅ 匹配到的行数：{len(matched_df)}")
        
        if len(matched_df) == 0:
            print("⚠️  警告：没有找到匹配的商品！")
            return False
        
        # 修改商品标题：在数字后添加"th"
        def modify_product_name(name):
            """
            修改商品名称，在数字后添加"th"和新的品类名称
            例如：Fishes 3 Drawstring Bags -> Fishes 3th Lite Trend Drawstring Bags
            """
            # 使用配置区域的新品类名称
            print(f"🔄 替换为：{NEW_CATEGORY}")
            
            # 使用正则表达式替换（忽略大小写）
            pattern = rf'(\d+)\s+{re.escape(CATEGORY_KEYWORD)}'
            replacement = rf'\1th {NEW_CATEGORY}'
            modified_name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
            return modified_name
        
        # 应用修改函数
        matched_df[first_column] = matched_df[first_column].apply(modify_product_name)
        
        # 删除临时的匹配结果列
        matched_df = matched_df.drop('匹配结果', axis=1)
        
        # 生成输出文件名（包含品类关键词和时间）
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 将品类关键词转换为小写，用于文件名
        category_lower = CATEGORY_KEYWORD.lower()
        output_file = f"{OUTPUT_PREFIX}_{category_lower}_{current_time}.xlsx"
        
        # 保存到新文件
        matched_df.to_excel(output_file, index=False)
        
        print(f"💾 处理完成！输出文件：{output_file}")
        print(f"📈 处理统计：")
        print(f"   - 原始行数：{len(df)}")
        print(f"   - 匹配行数：{len(matched_df)}")
        print(f"   - 处理率：{len(matched_df)/len(df)*100:.1f}%")
        
        # 显示前几行处理结果
        print(f"\n📋 处理结果预览：")
        for i, row in matched_df.head().iterrows():
            print(f"   {i+1}. {row[first_column]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误：{str(e)}")
        return False

def create_sample_excel():
    """
    创建一个示例Excel文件用于测试
    """
    sample_data = {
        '商品名称': [
            'Fishes 3 Drawstring Bags',
            'Regular T-Shirt',
            'Cats 5 Drawstring Bags',
            'Normal Backpack',
            'Dogs 2 Drawstring Bags',
            'Plain Hat',
            'Birds 7 Drawstring Bags',
            'Simple Shoes',
            'Fish 1 Drawstring Bag',
            'Basic Pants'
        ],
        '价格': [15.99, 25.50, 18.99, 35.00, 12.99, 20.00, 22.50, 45.00, 10.99, 30.00],
        '库存': [100, 50, 75, 25, 80, 60, 40, 30, 90, 35]
    }
    
    df = pd.DataFrame(sample_data)
    sample_file = 'sample_products.xlsx'
    df.to_excel(sample_file, index=False)
    print(f"📝 已创建示例文件：{sample_file}")
    return sample_file

def main():
    """
    主函数
    """
    print("🚀 Excel商品名称处理工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # 如果没有提供参数，先创建示例文件
        print("📝 未指定输入文件，正在创建示例文件...")
        input_file = create_sample_excel()
        print()
    
    # 处理文件
    success = process_excel_file(input_file)
    
    if success:
        print("\n🎉 处理完成！")
    else:
        print("\n💥 处理失败！")

if __name__ == "__main__":
    main()
