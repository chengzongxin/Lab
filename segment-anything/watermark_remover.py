# watermark_remover.py

import os
import cv2
import numpy as np
import torch
from segment_anything import sam_model_registry, SamPredictor

# 修改成你的模型路径
SAM_CHECKPOINT = "sam_vit_h_4b8939.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化模型
sam = sam_model_registry["vit_h"](checkpoint=SAM_CHECKPOINT)
predictor = SamPredictor(sam.to(DEVICE))

def is_watermark_region(mask, image):
    area_ratio = np.sum(mask) / (image.shape[0] * image.shape[1])
    if area_ratio > 0.05:  # 太大可能不是水印
        return False
    mean_color = image[mask].mean(axis=0)
    return np.all(mean_color > 180)  # 偏亮（白）

def process_image(image_path, output_mask_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image_rgb)

    # 多区域自动分割
    masks, _, _ = predictor.predict(point_coords=None,
                                    point_labels=None,
                                    multimask_output=False)

    final_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for mask in masks:
        if is_watermark_region(mask, image):
            final_mask[mask] = 255

    cv2.imwrite(output_mask_path, final_mask)

def batch_process(input_dir, mask_dir):
    os.makedirs(mask_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(mask_dir, file)
            print(f"Processing {file} ...")
            process_image(input_path, output_path)

if __name__ == "__main__":
    # 根据你的实际路径修改
    INPUT_DIR = "input_images"
    MASK_DIR = "mask_output"
    batch_process(INPUT_DIR, MASK_DIR)
