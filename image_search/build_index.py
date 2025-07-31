import os
import numpy as np
import json
from tqdm import tqdm
from extract import extract_feature

image_dir = "/Users/chengzongxin/Desktop/Lab/remove_water_mark_plus/dataset/images"  # TODO: 修改为你的图片路径
features = []
paths = []

for fname in tqdm(os.listdir(image_dir)):
    if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(image_dir, fname)
        try:
            feat = extract_feature(path)
            features.append(feat)
            paths.append(path)
        except:
            print(f"跳过损坏图片：{fname}")

features_np = np.vstack(features).astype('float32')
np.save("feature_cache.npy", features_np)

with open("path_cache.json", "w", encoding="utf-8") as f:
    json.dump(paths, f, ensure_ascii=False)

print("✅ 特征库构建完成！共处理图片：", len(paths))