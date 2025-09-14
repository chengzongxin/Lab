#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量Excel商品名称处理脚本
功能：一次性处理多个品类的商品名称，修改标题并输出到新文件
"""

import pandas as pd
import re
import os
from datetime import datetime
import sys

# ==================== 配置区域 ====================
# 在这里修改配置，无需修改代码逻辑

# 要处理的所有品类配置
CATEGORY_CONFIGS = {
    "Sock": "Lite Trend Sock",
    "Drawstring": "Lite Trend Drawstring", 
    "Tote": "Lite Trend Tote",
    "Sports": "Lite Trend Sports",
    "Scarf": "Lite Trend Scarf",
    "Apron": "Lite Trend Apron",
    "Unisex": "Lite Trend Unisex",  # 注意：a Unisex 中的 "a" 会被忽略
    "Cooling": "Lite Trend Cooling"
}

# 输出文件前缀
OUTPUT_PREFIX = "processed"

# ================================================

def process_single_category(df, category_keyword, new_category, first_column):
    """
    处理单个品类的商品
    
    参数:
        df: 原始数据框
        category_keyword: 品类关键词
        new_category: 新的品类名称
        first_column: 商品名称列名
    
    返回:
        tuple: (匹配的数据框, 匹配数量)
    """
    # 定义正则表达式模式：匹配数字+品类关键词
    pattern = rf'(\d+)\s+{re.escape(category_keyword)}'
    
    # 创建匹配结果列
    df['匹配结果'] = df[first_column].str.contains(pattern, case=False, na=False)
    
    # 筛选匹配的行
    matched_df = df[df['匹配结果'] == True].copy()
    
    if len(matched_df) == 0:
        return None, 0
    
    # 修改商品标题：在数字后添加"th"和新的品类名称
    def modify_product_name(name):
        # 使用正则表达式替换（忽略大小写）
        replacement = rf'\1th {new_category}'
        modified_name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
        return modified_name
    
    # 应用修改函数
    matched_df[first_column] = matched_df[first_column].apply(modify_product_name)
    
    # 删除临时的匹配结果列
    matched_df = matched_df.drop('匹配结果', axis=1)
    
    return matched_df, len(matched_df)

def process_excel_file(input_file):
    """
    批量处理Excel文件的主要函数
    
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
        print(f"🎯 要处理的品类数量：{len(CATEGORY_CONFIGS)}")
        print("=" * 60)
        
        # 存储所有处理结果
        all_results = []
        total_matched = 0
        
        # 逐个处理每个品类
        for i, (category_keyword, new_category) in enumerate(CATEGORY_CONFIGS.items(), 1):
            print(f"🔍 [{i}/{len(CATEGORY_CONFIGS)}] 处理品类：{category_keyword}")
            
            # 处理当前品类
            matched_df, match_count = process_single_category(df, category_keyword, new_category, first_column)
            
            if matched_df is not None and match_count > 0:
                print(f"   ✅ 匹配到 {match_count} 个商品")
                print(f"   🔄 替换为：{new_category}")
                
                # 添加品类标识列
                matched_df['处理品类'] = category_keyword
                all_results.append(matched_df)
                total_matched += match_count
            else:
                print(f"   ⚠️  未找到匹配的商品")
            print()
        
        # 检查是否有任何匹配结果
        if not all_results:
            print("❌ 警告：没有找到任何匹配的商品！")
            return False
        
        # 合并所有结果
        print("📋 合并所有处理结果...")
        final_df = pd.concat(all_results, ignore_index=True)
        
        # 生成输出文件名（包含时间戳）
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{OUTPUT_PREFIX}_all_categories_{current_time}.xlsx"
        
        # 保存到新文件
        final_df.to_excel(output_file, index=False)
        
        print("=" * 60)
        print(f"💾 批量处理完成！输出文件：{output_file}")
        print(f"📈 处理统计：")
        print(f"   - 原始行数：{len(df)}")
        print(f"   - 总匹配行数：{total_matched}")
        print(f"   - 处理率：{total_matched/len(df)*100:.1f}%")
        print(f"   - 处理品类数：{len(all_results)}")
        
        # 显示各品类处理结果
        print(f"\n📊 各品类处理结果：")
        for category_keyword, new_category in CATEGORY_CONFIGS.items():
            category_df = final_df[final_df['处理品类'] == category_keyword]
            if len(category_df) > 0:
                print(f"   - {category_keyword}: {len(category_df)} 个商品")
        
        # 显示前几行处理结果
        print(f"\n📋 处理结果预览：")
        for i, row in final_df.head(10).iterrows():
            print(f"   {i+1}. [{row['处理品类']}] {row[first_column]}")
        
        if len(final_df) > 10:
            print(f"   ... 还有 {len(final_df) - 10} 个商品")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误：{str(e)}")
        return False

def create_sample_excel():
    """
    创建一个包含多个品类的示例Excel文件用于测试
    """
    sample_data = {
        '商品名称': [
            # Sock品类
            'Fishes 3 Sock Bags',
            'Cats 5 Sock Items',
            
            # Drawstring品类
            'Dogs 2 Drawstring Bags',
            'Birds 7 Drawstring Bags',
            
            # Tote品类
            'Fish 1 Tote Bag',
            'Animals 4 Tote Bags',
            
            # Sports品类
            'Pets 6 Sports Bags',
            'Wild 8 Sports Items',
            
            # Scarf品类
            'Canvas 3 Scarf Items',
            'Fashion 2 Scarf Bags',
            
            # Apron品类
            'Kitchen 4 Apron Items',
            'Cooking 1 Apron Bag',
            
            # Unisex品类
            'Style 5 Unisex Items',
            'Trend 3 Unisex Bags',
            
            # Cooling品类
            'Summer 2 Cooling Items',
            'Heat 4 Cooling Bags',
            
            # 不匹配的商品
            'Regular T-Shirt',
            'Normal Backpack',
            'Plain Hat'
        ],
        '价格': [15.99, 25.50, 18.99, 35.00, 12.99, 20.00, 22.50, 45.00, 10.99, 30.00, 
                15.50, 18.00, 25.99, 22.00, 19.99, 28.50, 35.00, 40.00, 15.00],
        '库存': [100, 50, 75, 25, 80, 60, 40, 30, 90, 35, 55, 45, 65, 70, 85, 20, 30, 25, 40]
    }
    
    df = pd.DataFrame(sample_data)
    sample_file = 'sample_multi_categories.xlsx'
    df.to_excel(sample_file, index=False)
    print(f"📝 已创建多品类示例文件：{sample_file}")
    return sample_file

def main():
    """
    主函数
    """
    print("🚀 批量Excel商品名称处理工具")
    print("=" * 60)
    print(f"🎯 配置的品类：{', '.join(CATEGORY_CONFIGS.keys())}")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # 如果没有提供参数，先创建示例文件
        print("📝 未指定输入文件，正在创建多品类示例文件...")
        input_file = create_sample_excel()
        print()
    
    # 处理文件
    success = process_excel_file(input_file)
    
    if success:
        print("\n🎉 批量处理完成！")
    else:
        print("\n💥 批量处理失败！")

if __name__ == "__main__":
    main()
