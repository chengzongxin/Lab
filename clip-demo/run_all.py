# ------------------------------------------
# run_all.py
# 一键运行完整的图片评分流程
# ------------------------------------------

import os
import subprocess

print("🚀 Step 1: 提取图像特征")
subprocess.run(["python", "features_extract.py"])

print("\n✅ Step 1 完成\n")

print("🧠 Step 2: 训练评分模型")
subprocess.run(["python", "train_score_model.py"])

print("\n✅ Step 2 完成\n")

print("🔍 Step 3: 对所有图片进行评分预测")
subprocess.run(["python", "predict_score.py"])

print("\n🎉 所有步骤完成，预测结果保存在 output/predicted_scores.csv")
