# ------------------------------------------
# 3. predict_score.py
# 使用训练好的模型进行评分预测
# ------------------------------------------

import os
import torch
import numpy as np
import pandas as pd
from torch import nn

# 路径设置
feature_dir = "output"
model_path = os.path.join(feature_dir, "score_model.pt")
feature_path = os.path.join(feature_dir, "image_features.npy")
label_path = os.path.join(feature_dir, "labels.npy")
meta_path = os.path.join(feature_dir, "meta.csv")
output_path = os.path.join(feature_dir, "predicted_scores.csv")

# 加载特征、标签、元信息
features = np.load(feature_path)
labels = np.load(label_path)
meta = pd.read_csv(meta_path)

# 加载训练好的模型
if not os.path.exists(model_path):
    raise FileNotFoundError(f"未找到模型文件：{model_path}")

# 使用 PyTorch 加载模型
device = "cuda" if torch.cuda.is_available() else "cpu"
state_dict = torch.load(model_path, map_location=device)

# 创建与训练时相同的模型结构
model = nn.Sequential(
    nn.Linear(features.shape[1], 256),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(256, 5)  # 5 个评分等级
)
model.load_state_dict(state_dict)
model.to(device)
model.eval()  # 设置为评估模式

# 将特征转换为 PyTorch tensor
features_tensor = torch.FloatTensor(features).to(device)

# 进行预测
with torch.no_grad():
    outputs = model(features_tensor)
    pred_labels = outputs.argmax(dim=1).cpu().numpy()
    
    # 计算概率分布
    prob = torch.softmax(outputs, dim=1).cpu().numpy()
    
    # 新的分数计算方式
    # 1. 找到最高概率的类别
    max_prob_idx = np.argmax(prob, axis=1)
    # 2. 获取最高概率值
    max_probs = np.max(prob, axis=1)
    # 3. 计算预测分数：基础分数 + 概率调整
    base_scores = max_prob_idx + 1  # 基础分数（1-5）
    # 4. 根据概率值调整分数
    pred_scores = base_scores + (max_probs - 0.5) * 0.5  # 概率越高，分数越高

# 保存结果
meta["pred_label"] = pred_labels
meta["pred_score"] = pred_scores
meta.to_csv(output_path, index=False)

print(f"✅ 预测完成，结果已保存至：{output_path}")
