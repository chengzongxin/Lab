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

def search_similar_gradio(query_img, topk=5):
    # 保存上传图片为临时文件
    temp_path = "temp_query.jpg"
    query_img.save(temp_path)

    # 提取特征
    query_feat = extract_feature(temp_path).astype('float32').reshape(1, -1)
    distances, indices = model.kneighbors(query_feat)

    results = []
    for i, idx in enumerate(indices[0]):
        result_path = image_paths[idx]
        filename = result_path.split("/")[-1]  # 或用 os.path.basename(result_path)
        caption = f"{filename}  距离: {distances[0][i]:.2f}"
        results.append((result_path, caption))
    return results


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
    demo.launch()
