# app.py
import gradio as gr
import numpy as np
import json
from extractv1 import extract_feature
from sklearn.neighbors import NearestNeighbors
from PIL import Image

# 加载特征库和路径
features = np.load("feature_cache.npy")
with open("path_cache.json", "r", encoding="utf-8") as f:
    image_paths = json.load(f)

# 构建最近邻模型
model = NearestNeighbors(n_neighbors=5, algorithm="auto", metric="euclidean")
model.fit(features)

import os

def get_allowed_paths():
    """
    自动获取所有图片所在的目录路径
    """
    allowed_paths = set()
    
    # 添加当前工作目录
    allowed_paths.add(os.getcwd())
    
    # 从图片路径中提取所有唯一的目录
    for path in image_paths:
        if os.path.exists(path):
            # 获取图片所在的目录
            dir_path = os.path.dirname(path)
            allowed_paths.add(dir_path)
            
            # 也添加父目录（以防万一）
            parent_dir = os.path.dirname(dir_path)
            if parent_dir != dir_path:  # 避免重复
                allowed_paths.add(parent_dir)
    
    return list(allowed_paths)

def search_similar_gradio(query_img, topk=5):
    try:
        # 保存上传图片为临时文件
        temp_path = "temp_query.jpg"
        query_img.save(temp_path)

        # 提取特征
        query_feat = extract_feature(temp_path).astype('float32').reshape(1, -1)
        distances, indices = model.kneighbors(query_feat)

        results = []
        for i, idx in enumerate(indices[0]):
            result_path = image_paths[idx]
            # 使用os.path.basename更安全地获取文件名
            filename = os.path.basename(result_path)
            caption = f"{filename}  距离: {distances[0][i]:.2f}"
            results.append((result_path, caption))
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return results
    except Exception as e:
        print(f"搜索过程中出现错误: {str(e)}")
        return []


# Gradio UI
demo = gr.Interface(
    fn=search_similar_gradio,
    inputs=[
        gr.Image(type="pil", label="上传查询图片"),
        gr.Slider(1, 20, value=5, step=1, label="返回相似图片数")
    ],
    outputs=gr.Gallery(label="相似图片"),
    title="以图搜图（本地图片库）",
    description="上传一张图片，查找本地最相似的图片（无需联网）"
)

if __name__ == "__main__":
    # 自动获取所有允许的路径
    allowed_paths = get_allowed_paths()
    print(f"🔍 检测到的图片目录: {len(allowed_paths)} 个")
    print(f"📁 允许的路径: {allowed_paths[:5]}...")  # 只显示前5个
    
    # 启动Gradio应用
    demo.launch(
        allowed_paths=allowed_paths,
        share=True
    )
