# ------------------------------------------
# 1. features_extract.py
# 提取所有图片的特征并保存
# ------------------------------------------

import os
import torch
import pandas as pd
import numpy as np
from PIL import Image
from torchvision import transforms
from tqdm import tqdm
from clip import load as load_clip

# 设置路径
data_path = "images"
label_csv = "labels.csv"
out_dir = "output"
os.makedirs(out_dir, exist_ok=True)

# 加载 CLIP 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = load_clip("ViT-B/32", device=device)

# 读取标签文件
df = pd.read_csv(label_csv)

# 将浮点评分映射为离散标签（0~4）
def score_to_label(score):
    if score < 2:
        return 0
    elif score < 3:
        return 1
    elif score < 4:
        return 2
    elif score < 4.5:
        return 3
    else:
        return 4

features = []
labels = []
paths = []

print("Extracting image features...")
for _, row in tqdm(df.iterrows(), total=len(df)):
    image_path = row["image_path"]
    score = row["score"]

    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        image_feature = model.encode_image(image).cpu().numpy()[0]

    features.append(image_feature)
    labels.append(score_to_label(score))
    paths.append(image_path)

# 保存成 npy
os.makedirs(out_dir, exist_ok=True)
np.save(os.path.join(out_dir, "image_features.npy"), np.array(features))
np.save(os.path.join(out_dir, "labels.npy"), np.array(labels))
pd.DataFrame({"path": paths, "label": labels}).to_csv(os.path.join(out_dir, "meta.csv"), index=False)
print("Done.")
