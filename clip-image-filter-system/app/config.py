import os
import torch  # 添加这一行
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 模型配置
    MODEL_NAME = "ViT-B-32"
    PRETRAINED = "laion2b_s34b_b79k"
    DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
    
    # 数据路径
    IMAGE_DIR = os.getenv("IMAGE_DIR", "data/images")
    FEATURE_DIR = os.getenv("FEATURE_DIR", "data/features")
    INDEX_DIR = os.getenv("INDEX_DIR", "data/index")
    
    # API配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))    