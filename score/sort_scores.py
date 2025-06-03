#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def sort_scores(filename):
    """
    读取文件并按分数排序
    :param filename: 输入文件名
    :return: 排序后的结果列表
    """
    # 存储结果的列表
    items = []
    
    # 读取文件
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            # 跳过空行和分隔符行
            if not line.strip() or '****' in line:
                continue
                
            # 检查是否包含分数
            if 'Score =' in line:
                try:
                    # 分割文件名和分数
                    parts = line.split(' : Score = ')
                    if len(parts) == 2:
                        # 提取序号和文件名
                        rank_part = parts[0].split(') ')[-1]
                        filename = rank_part.strip()
                        score = float(parts[1].strip())
                        items.append((filename, score))
                except Exception as e:
                    print(f"处理行时出错: {line}")
                    print(f"错误信息: {e}")
    
    # 按分数排序（从高到低）
    sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
    
    # 输出排序结果
    print("\n排序结果（从高到低）：")
    print("=" * 50)
    for i, (filename, score) in enumerate(sorted_items, 1):
        print(f"{i}) {filename} : Score = {score:.5f}")
    
    return sorted_items

if __name__ == "__main__":
    # 使用函数
    sorted_results = sort_scores('score.txt')
    
    # 输出一些统计信息
    print("\n统计信息：")
    print("=" * 50)
    print(f"总条目数: {len(sorted_results)}")
    print(f"最高分: {sorted_results[0][1]:.5f}")
    print(f"最低分: {sorted_results[-1][1]:.5f}")
    print(f"平均分: {sum(score for _, score in sorted_results) / len(sorted_results):.5f}") 