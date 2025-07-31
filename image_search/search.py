import numpy as np
import faiss
import json
from extract import extract_feature

def search_similar(query_image_path, topk=5):
    query_feat = extract_feature(query_image_path).astype('float32').reshape(1, -1)
    features = np.load("feature_cache.npy")

    index = faiss.IndexFlatL2(features.shape[1])
    index.add(features)

    D, I = index.search(query_feat, topk)

    with open("path_cache.json", "r", encoding="utf-8") as f:
        paths = json.load(f)

    print(f"\n📷 查询图像: {query_image_path}")
    print("🔍 Top 相似图片:")
    for i, idx in enumerate(I[0]):
        print(f"{i+1}. {paths[idx]}  距离: {D[0][i]:.2f}")