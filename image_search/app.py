# app.py
import gradio as gr
import numpy as np
import json
from extractv1 import extract_feature
from sklearn.neighbors import NearestNeighbors
from PIL import Image
import os

# 加载特征库和路径
features = np.load("feature_cache.npy")
with open("path_cache.json", "r", encoding="utf-8") as f:
    image_paths = json.load(f)

# 构建最近邻模型
model = NearestNeighbors(n_neighbors=50, algorithm="auto", metric="euclidean")  # 增加默认邻居数
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
    """单张图片搜索"""
    try:
        # 保存上传图片为临时文件
        temp_path = "temp_query.jpg"
        query_img.save(temp_path)

        # 提取特征
        query_feat = extract_feature(temp_path).astype('float32').reshape(1, -1)
        distances, indices = model.kneighbors(query_feat, n_neighbors=topk)  # 明确指定返回数量

        results = []
        for i, idx in enumerate(indices[0]):
            result_path = image_paths[idx]
            # 显示完整路径和文件名
            filename = os.path.basename(result_path)
            caption = f"{filename}\n路径: {result_path}\n距离: {distances[0][i]:.2f}"
            results.append((result_path, caption))
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return results
    except Exception as e:
        print(f"搜索过程中出现错误: {str(e)}")
        return []

def batch_search_gradio(query_images, topk=5):
    """批量图片搜索"""
    if not query_images:
        return []
    
    all_results = []
    
    for i, query_img in enumerate(query_images):
        try:
            # Gradio文件上传返回的是路径字符串，需要直接使用
            if isinstance(query_img, str):
                # 直接使用文件路径
                temp_path = query_img
            else:
                # 如果是PIL图像对象，保存为临时文件
                temp_path = f"temp_query_{i}.jpg"
                query_img.save(temp_path)

            # 提取特征
            query_feat = extract_feature(temp_path).astype('float32').reshape(1, -1)
            distances, indices = model.kneighbors(query_feat, n_neighbors=topk)  # 明确指定返回数量

            # 为每张查询图片添加标题
            query_title = f"查询图片 {i+1}"
            all_results.append((temp_path, query_title))
            
            # 添加相似图片结果
            for j, idx in enumerate(indices[0]):
                result_path = image_paths[idx]
                filename = os.path.basename(result_path)
                caption = f"查询{i+1} - {filename}\n路径: {result_path}\n距离: {distances[0][j]:.2f}"
                all_results.append((result_path, caption))
            
            # 只清理我们自己创建的临时文件
            if not isinstance(query_img, str) and os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            print(f"处理第 {i+1} 张图片时出现错误: {str(e)}")
            continue
    
    return all_results

# Gradio UI
with gr.Blocks(title="以图搜图（本地图片库）") as demo:
    gr.Markdown("# 🔍 以图搜图系统")
    gr.Markdown("上传一张或多张图片，查找本地最相似的图片（无需联网）")
    
    with gr.Tabs():
        # 单张图片搜索标签页
        with gr.TabItem("单张图片搜索"):
            with gr.Row():
                with gr.Column():
                    single_input = gr.Image(type="pil", label="上传查询图片")
                    single_topk = gr.Slider(1, 20, value=5, step=1, label="返回相似图片数")
                    single_search_btn = gr.Button("🔍 开始搜索", variant="primary")
                
                with gr.Column():
                    single_output = gr.Gallery(label="相似图片", show_label=True)
            
            single_search_btn.click(
                fn=search_similar_gradio,
                inputs=[single_input, single_topk],
                outputs=single_output
            )
        
        # 批量图片搜索标签页
        with gr.TabItem("批量图片搜索"):
            with gr.Row():
                with gr.Column():
                    batch_input = gr.File(
                        file_count="multiple",
                        file_types=["image"],
                        label="上传多张查询图片"
                    )
                    batch_topk = gr.Slider(1, 20, value=5, step=1, label="每张图片返回相似图片数")
                    batch_search_btn = gr.Button("🚀 开始批量搜索", variant="primary")
                
                with gr.Column():
                    batch_output = gr.Gallery(label="批量搜索结果", show_label=True)
            
            batch_search_btn.click(
                fn=batch_search_gradio,
                inputs=[batch_input, batch_topk],
                outputs=batch_output
            )

if __name__ == "__main__":
    # 自动获取所有允许的路径
    allowed_paths = get_allowed_paths()
    print(f"🔍 检测到的图片目录: {len(allowed_paths)} 个")
    print(f"📁 允许的路径: {allowed_paths[:5]}...")  # 只显示前5个
    
    # 启动Gradio应用
    demo.launch(
        server_name="0.0.0.0",  # 绑定到所有网络接口，允许内网访问
        server_port=7860,       # 指定端口
        allowed_paths=allowed_paths,
        share=True
    )
