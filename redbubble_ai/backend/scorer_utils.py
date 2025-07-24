"""
AI美学评分工具模块 
从 crawler/scorer.py 迁移而来，适配backend环境
使用NIMA (Neural Image Assessment) 模型对图片进行美学评分
"""

import os
import numpy as np
import logging
from PIL import Image

# 配置日志
logger = logging.getLogger(__name__)

# 延迟导入Keras相关模块，避免启动时加载过慢
_nima_model = None

def get_model_weights_path():
    """
    获取NIMA模型权重文件路径
    """
    # 在backend目录下查找权重文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    weights_path = os.path.join(base_dir, 'weights_mobilenet_aesthetic_0.07.hdf5')
    
    # 如果backend目录下没有，尝试从crawler目录获取
    if not os.path.exists(weights_path):
        crawler_weights_path = os.path.join(base_dir, '..', 'crawler', 'weights_mobilenet_aesthetic_0.07.hdf5')
        if os.path.exists(crawler_weights_path):
            weights_path = crawler_weights_path
            logger.info(f"使用crawler目录下的权重文件: {weights_path}")
        else:
            logger.error(f"未找到NIMA权重文件，请确保以下任一路径存在权重文件:")
            logger.error(f"1. {os.path.join(base_dir, 'weights_mobilenet_aesthetic_0.07.hdf5')}")
            logger.error(f"2. {crawler_weights_path}")
            raise FileNotFoundError("NIMA权重文件不存在")
    
    return weights_path

def build_nima_model():
    """
    构建NIMA模型
    从 crawler/scorer.py 迁移而来
    """
    try:
        # 延迟导入Keras模块
        from keras.applications.mobilenet import MobileNet
        from keras.layers import GlobalAveragePooling2D, Dropout, Dense, Input
        from keras.models import Model
        
        logger.info("正在构建NIMA模型...")
        
        # 构建模型架构
        input_layer = Input(shape=(224, 224, 3))
        base_model = MobileNet(input_tensor=input_layer, include_top=False, weights=None)
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dropout(0.75)(x)
        x = Dense(10, activation='softmax')(x)
        model = Model(inputs=input_layer, outputs=x)
        
        logger.info("NIMA模型构建完成")
        return model
        
    except ImportError as e:
        logger.error(f"导入Keras模块失败: {e}")
        logger.error("请确保已安装 tensorflow 和 keras")
        raise e
    except Exception as e:
        logger.error(f"构建NIMA模型失败: {e}")
        raise e

def get_nima_model():
    """
    获取NIMA模型实例（单例模式）
    """
    global _nima_model
    
    if _nima_model is None:
        try:
            logger.info("初始化NIMA模型...")
            
            # 构建模型
            _nima_model = build_nima_model()
            
            # 加载权重
            weights_path = get_model_weights_path()
            logger.info(f"加载模型权重: {weights_path}")
            _nima_model.load_weights(weights_path)
            
            logger.info("NIMA模型初始化完成")
            
        except Exception as e:
            logger.error(f"初始化NIMA模型失败: {e}")
            _nima_model = None
            raise e
    
    return _nima_model

def nima_score(img_path, model=None):
    """
    使用NIMA模型对图片进行美学评分
    从 crawler/scorer.py 迁移而来，优化了错误处理
    :param img_path: 图片文件路径
    :param model: NIMA模型实例（可选，自动获取）
    :return: 美学评分 (1-10分)
    """
    try:
        # 检查图片文件是否存在
        if not os.path.exists(img_path):
            logger.warning(f"图片文件不存在: {img_path}")
            return 0.0
        
        # 获取模型实例
        if model is None:
            model = get_nima_model()
        
        if model is None:
            logger.error("NIMA模型未初始化")
            return 0.0
        
        # 延迟导入图像处理模块
        from keras.preprocessing import image
        from keras.applications.mobilenet import preprocess_input
        
        # 加载和预处理图片
        logger.debug(f"正在评分: {img_path}")
        
        # 加载图片并调整尺寸
        img = image.load_img(img_path, target_size=(224, 224))
        
        # 转换为数组
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        
        # 预处理
        x = preprocess_input(x)
        
        # 模型预测
        preds = model.predict(x, verbose=0)[0]
        
        # 计算加权平均分数
        mean_score = sum([(i+1)*p for i, p in enumerate(preds)])
        
        logger.debug(f"评分完成: {img_path} -> {mean_score:.2f}")
        return float(mean_score)
        
    except Exception as e:
        logger.error(f"评分失败: {img_path}, 错误: {e}")
        return 0.0

def batch_nima_score(img_paths, batch_size=8):
    """
    批量处理图片评分，提高效率
    :param img_paths: 图片路径列表
    :param batch_size: 批处理大小
    :return: 评分列表
    """
    try:
        # 获取模型实例
        model = get_nima_model()
        if model is None:
            logger.error("NIMA模型未初始化")
            return [0.0] * len(img_paths)
        
        scores = []
        
        # 批量处理
        for i in range(0, len(img_paths), batch_size):
            batch_paths = img_paths[i:i+batch_size]
            batch_scores = []
            
            for img_path in batch_paths:
                score = nima_score(img_path, model)
                batch_scores.append(score)
            
            scores.extend(batch_scores)
            logger.info(f"批量评分进度: {min(i+batch_size, len(img_paths))}/{len(img_paths)}")
        
        return scores
        
    except Exception as e:
        logger.error(f"批量评分失败: {e}")
        return [0.0] * len(img_paths)

def is_nima_available():
    """
    检查NIMA模型是否可用
    :return: True if available, False otherwise
    """
    try:
        weights_path = get_model_weights_path()
        return os.path.exists(weights_path)
    except:
        return False

def preload_nima_model():
    """
    预加载NIMA模型，用于应用启动时初始化
    """
    try:
        logger.info("预加载NIMA模型...")
        model = get_nima_model()
        if model is not None:
            logger.info("NIMA模型预加载完成")
            return True
        else:
            logger.warning("NIMA模型预加载失败")
            return False
    except Exception as e:
        logger.error(f"预加载NIMA模型失败: {e}")
        return False 