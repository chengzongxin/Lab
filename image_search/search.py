import numpy as np
import json
from extractv1 import extract_feature
from sklearn.neighbors import NearestNeighbors

def search_similar(query_image_path, topk=5):
    query_feat = extract_feature(query_image_path).astype('float32').reshape(1, -1)
    features = np.load("feature_cache.npy")

    model = NearestNeighbors(n_neighbors=topk, algorithm="auto", metric="euclidean")
    model.fit(features)
    distances, indices = model.kneighbors(query_feat)

    with open("path_cache.json", "r", encoding="utf-8") as f:
        paths = json.load(f)

    print(f"\n📷 查询图像: {query_image_path}")
    print("🔍 Top 相似图片:")
    for i, idx in enumerate(indices[0]):
        print(f"{i+1}. {paths[idx]}  距离: {distances[0][i]:.2f}")
