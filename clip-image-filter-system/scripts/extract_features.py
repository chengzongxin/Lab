import os
import argparse
import numpy as np
from tqdm import tqdm
from app.utils import FeatureExtractor
from app.config import Config

def main(args):
    config = Config()
    extractor = FeatureExtractor(
        model_name=config.MODEL_NAME,
        pretrained=config.PRETRAINED,
        device=config.DEVICE
    )
    
    # 创建特征保存目录
    os.makedirs(config.FEATURE_DIR, exist_ok=True)
    
    # 获取所有图片路径
    image_paths = []
    for root, _, files in os.walk(config.IMAGE_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_paths.append(os.path.join(root, file))
    
    print(f"Found {len(image_paths)} images to process")
    
    # 批量提取特征
    all_features = []
    valid_paths = []
    
    for path in tqdm(image_paths):
        features = extractor.extract_image_features(path)
        if features is not None:
            all_features.append(features)
            valid_paths.append(path)
    
    # 保存特征
    features_array = np.vstack(all_features)
    np.save(os.path.join(config.FEATURE_DIR, "image_features.npy"), features_array)
    np.save(os.path.join(config.FEATURE_DIR, "image_paths.npy"), np.array(valid_paths))
    
    print(f"Features extracted and saved to {config.FEATURE_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract features from images")
    args = parser.parse_args()
    main(args)    