from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Tuple
import numpy as np
import os
from app.utils import FeatureExtractor, VectorDatabase, PreferenceModel
from app.config import Config

app = FastAPI(title="AI Image Filter & Scoring System")
config = Config()

# 初始化组件
extractor = FeatureExtractor(
    model_name=config.MODEL_NAME,
    pretrained=config.PRETRAINED,
    device=config.DEVICE
)

db = VectorDatabase(index_path=os.path.join(config.INDEX_DIR, "image_index"))

# 定义偏好类别
preference_categories = [
    "stripes", "spots", "small animals", "minimalist and fashionable"
]

# 提取类别特征
category_features = np.vstack([
    extractor.extract_text_features(cat)[0] 
    for cat in preference_categories
])

# 初始化偏好模型
preference_model = PreferenceModel(preference_categories)

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Image Filter & Scoring System"}

@app.post("/score-image/")
async def score_image(file: UploadFile = File(...)):
    """对上传的图片进行评分"""
    try:
        # 保存临时文件
        temp_path = "temp_image.jpg"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # 提取特征
        features = extractor.extract_image_features(temp_path)
        if features is None:
            raise HTTPException(status_code=400, detail="Failed to process image")
        
        # 计算每个类别的相似度
        similarities = {}
        for i, category in enumerate(preference_categories):
            sim = np.dot(features, category_features[i].reshape(-1, 1))[0][0]
            similarities[category] = float(sim)
        
        # 计算最终评分
        final_score = preference_model.score_image(features, category_features)
        
        # 删除临时文件
        os.remove(temp_path)
        
        return {
            "categories": preference_categories,
            "category_scores": similarities,
            "final_score": float(final_score),
            "preference_weights": preference_model.weights.tolist()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-similar/")
async def search_similar(category: str = None, top_k: int = 10):
    """搜索与指定类别或整体偏好相似的图片"""
    try:
        if category and category in preference_categories:
            # 搜索特定类别的相似图片
            category_idx = preference_categories.index(category)
            query = category_features[category_idx:category_idx+1]
        else:
            # 搜索符合整体偏好的图片
            weighted_query = np.sum(
                category_features * preference_model.weights.reshape(-1, 1), 
                axis=0
            ).reshape(1, -1)
            query = weighted_query / np.linalg.norm(weighted_query)
        
        # 搜索相似图片
        results = db.search(query, k=top_k)
        
        return {
            "query_category": category if category else "overall_preference",
            "results": [{"score": float(score), "path": path} for score, path in results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-preference/")
async def update_preference(feedback: Dict[int, float]):
    """更新用户偏好权重"""
    try:
        preference_model.update_weights(feedback)
        return {
            "message": "Preference weights updated successfully",
            "new_weights": preference_model.weights.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    