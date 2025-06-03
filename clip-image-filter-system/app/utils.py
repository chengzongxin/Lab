import os
import torch
import numpy as np
import open_clip
from PIL import Image
import faiss
from typing import List, Dict, Tuple

class FeatureExtractor:
    def __init__(self, model_name="ViT-B-32", pretrained="laion2b_s34b_b79k", device="mps"):
        self.model, self.preprocess, self.tokenizer = self._load_model(model_name, pretrained, device)
        self.device = device
    
    def _load_model(self, model_name, pretrained, device):
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name=model_name,
            pretrained=pretrained
        )
        model.to(device)
        model.eval()
        tokenizer = open_clip.get_tokenizer(model_name)
        return model, preprocess, tokenizer
    
    def extract_image_features(self, image_path: str) -> np.ndarray:
        try:
            image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.model.encode_image(image)
                features /= features.norm(dim=-1, keepdim=True)
            return features.cpu().numpy()
        except Exception as e:
            print(f"Error extracting features from {image_path}: {e}")
            return None
    
    def extract_text_features(self, text: str) -> np.ndarray:
        tokens = self.tokenizer([text]).to(self.device)
        with torch.no_grad():
            features = self.model.encode_text(tokens)
            features /= features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy()

class VectorDatabase:
    def __init__(self, dim=512, index_path=None):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # 内积索引，适合余弦相似度
        self.image_paths = []
        
        if index_path:
            self.load(index_path)
    
    def add_vectors(self, features: np.ndarray, image_paths: List[str]):
        self.index.add(features)
        self.image_paths.extend(image_paths)
    
    def search(self, query: np.ndarray, k=10) -> Tuple[List[float], List[str]]:
        distances, indices = self.index.search(query, k)
        results = [(distances[0][i], self.image_paths[indices[0][i]]) for i in range(k)]
        return results
    
    def save(self, path: str):
        faiss.write_index(self.index, f"{path}.index")
        np.save(f"{path}_paths.npy", np.array(self.image_paths))
    
    def load(self, path: str):
        self.index = faiss.read_index(f"{path}.index")
        self.image_paths = np.load(f"{path}_paths.npy").tolist()

class PreferenceModel:
    def __init__(self, categories: List[str]):
        self.categories = categories
        self.weights = np.ones(len(categories)) / len(categories)  # 初始均匀权重
    
    def update_weights(self, feedback: Dict[int, float]):
        """根据用户反馈更新权重"""
        for idx, delta in feedback.items():
            if 0 <= idx < len(self.weights):
                self.weights[idx] = max(0.01, min(0.99, self.weights[idx] + delta))
        
        # 归一化权重
        self.weights /= np.sum(self.weights)
    
    def score_image(self, image_features: np.ndarray, category_features: np.ndarray) -> float:
        """计算图片与偏好的加权相似度"""
        similarities = np.dot(image_features, category_features.T).flatten()
        return np.sum(similarities * self.weights)    