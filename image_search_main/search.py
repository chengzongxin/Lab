import numpy as np
import json
from extractv1 import extract_feature
from sklearn.neighbors import NearestNeighbors

def search_similar(query_image_path, topk=5, return_results=False):
    """
    搜索相似图片
    
    Args:
        query_image_path: 查询图片路径
        topk: 返回相似图片数量
        return_results: 是否返回结果列表（用于批量处理）
    
    Returns:
        如果 return_results=True，返回 [(图片路径, 距离), ...] 的列表
        否则返回 None，直接打印结果
    """
    query_feat = extract_feature(query_image_path).astype('float32').reshape(1, -1)
    features = np.load("feature_cache.npy")

    model = NearestNeighbors(n_neighbors=topk, algorithm="auto", metric="euclidean")
    model.fit(features)
    distances, indices = model.kneighbors(query_feat)

    with open("path_cache.json", "r", encoding="utf-8") as f:
        paths = json.load(f)

    # 收集结果
    results = []
    for i, idx in enumerate(indices[0]):
        result_path = paths[idx]
        distance = distances[0][i]
        results.append((result_path, distance))
        
        if not return_results:
            print(f"{i+1}. {result_path}  距离: {distance:.2f}")

    if return_results:
        return results
    else:
        print(f"\n📷 查询图像: {query_image_path}")
        print("🔍 Top 相似图片:")
        for i, (result_path, distance) in enumerate(results, 1):
            print(f"{i+1}. {result_path}  距离: {distance:.2f}")
