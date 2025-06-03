import os
import argparse
import numpy as np
from app.utils import VectorDatabase
from app.config import Config

def main(args):
    config = Config()
    
    # 加载特征
    features = np.load(os.path.join(config.FEATURE_DIR, "image_features.npy"))
    image_paths = np.load(os.path.join(config.FEATURE_DIR, "image_paths.npy")).tolist()
    
    print(f"Loaded {len(features)} image features")
    
    # 创建向量数据库
    os.makedirs(config.INDEX_DIR, exist_ok=True)
    index_path = os.path.join(config.INDEX_DIR, "image_index")
    
    db = VectorDatabase(dim=features.shape[1])
    db.add_vectors(features, image_paths)
    db.save(index_path)
    
    print(f"Vector index built and saved to {index_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index for image features")
    args = parser.parse_args()
    main(args)    