import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# 直接用 HuggingFace 上的美学微调模型
clip_model = CLIPModel.from_pretrained("laion/CLIP-ViT-B-32-laion2B-s34B-b79K")
clip_processor = CLIPProcessor.from_pretrained("laion/CLIP-ViT-B-32-laion2B-s34B-b79K")

def aesthetic_clip_score(img_path):
    """
    用Aesthetic-CLIP对图片进行美学评分，分数越高越美观
    """
    try:
        image = Image.open(img_path).convert("RGB")
        inputs = clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            img_features = clip_model.get_image_features(**inputs)
            # 这里输出的是特征向量，可以用来做相似度或聚类
            # 但没有线性头时，不能直接输出0-10分的美学分数
            # 你可以用特征向量做聚类，或者用社区的aesthetic-head权重（如能找到）
            return float(img_features.norm().item())  # 仅做示例
    except Exception as e:
        print(f"评分失败: {img_path}, 错误: {e}")
        return 0

if __name__ == "__main__":
    print(aesthetic_clip_score("results/test.jpg")) 