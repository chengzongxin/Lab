import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image
from keras.applications.mobilenet import MobileNet
from keras.layers import GlobalAveragePooling2D, Dropout, Dense, Input
from keras.models import Model
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing import image
import numpy as np
import os

# 获取当前脚本文件的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接权重文件的绝对路径，确保无论从哪里运行都能找到
NIMA_WEIGHTS = os.path.join(BASE_DIR, 'weights_mobilenet_aesthetic_0.07.hdf5')
if not os.path.exists(NIMA_WEIGHTS):
    raise FileNotFoundError(f"未找到NIMA权重文件: {NIMA_WEIGHTS}")

def build_nima_model():
    input_layer = Input(shape=(224, 224, 3))
    base_model = MobileNet(input_tensor=input_layer, include_top=False, weights=None)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.75)(x)
    x = Dense(10, activation='softmax')(x)
    model = Model(inputs=input_layer, outputs=x)
    return model

nima_model = build_nima_model()
nima_model.load_weights(NIMA_WEIGHTS)

def nima_score(img_path, model=nima_model):
    """
    用NIMA模型对图片进行美学评分，返回1~10分
    """
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x)[0]
        mean_score = sum([(i+1)*p for i, p in enumerate(preds)])
        return mean_score
    except Exception as e:
        print(f"评分失败: {img_path}, 错误: {e}")
        return 0

if __name__ == "__main__":
    print(nima_score("results/test.jpg")) 