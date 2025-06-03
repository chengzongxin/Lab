# extract_features.py
import os
import clip
import torch
from PIL import Image
import numpy as np
import csv

# 1. 加载模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 2. 准备读取文件
image_dir = "images"
features = []
scores = []

# 3. 从 labels.csv 中读取每张图及其评分
with open("labels.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        filename = row["filename"]
        score = float(row["score"])
        image_path = os.path.join(image_dir, filename)

        # 4. 加载图像并提取特征
        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image).cpu().numpy()

        features.append(image_features[0])  # 每张图得到一个512维向量
        scores.append(score)

# 5. 保存特征和评分到本地文件
np.save("image_features.npy", np.array(features))
np.save("image_scores.npy", np.array(scores))

print("✅ 特征提取完成，文件已保存为 image_features.npy 和 image_scores.npy")
