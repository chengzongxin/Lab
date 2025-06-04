# ------------------------------------------
# analyze_prediction.py
# 对预测结果进行分析与可视化
# ------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 配置
output_dir = "output"
pred_path = os.path.join(output_dir, "predicted_scores.csv")

# 加载数据
df = pd.read_csv(pred_path)

# 打印基本信息
print("📊 预测结果统计：")
print(df["pred_score"].describe())

# 可视化：预测评分分布（连续值）
plt.figure(figsize=(8, 5))
sns.histplot(df["pred_score"], bins=20, kde=True, color='skyblue')
plt.title("预测评分分布（连续）")
plt.xlabel("预测评分")
plt.ylabel("图像数量")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "pred_score_distribution.png"))
plt.show()

# 可视化：预测标签分布（离散标签）
plt.figure(figsize=(6, 4))
sns.countplot(x="pred_label", data=df, palette="Set2")
plt.title("预测标签分布（离散）")
plt.xlabel("预测标签 (0-4)")
plt.ylabel("图像数量")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "pred_label_distribution.png"))
plt.show()

# 如果有真实标签，也做对比
if "label" in df.columns:
    from sklearn.metrics import classification_report, confusion_matrix
    import numpy as np

    print("\n📋 分类评估报告：")
    print(classification_report(df["label"], df["pred_label"], digits=3))

    # 混淆矩阵可视化
    plt.figure(figsize=(6, 5))
    cm = confusion_matrix(df["label"], df["pred_label"])
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=range(5), yticklabels=range(5))
    plt.title("混淆矩阵（真实标签 vs 预测标签）")
    plt.xlabel("预测标签")
    plt.ylabel("真实标签")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"))
    plt.show()
