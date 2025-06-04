```
project/
├── images/                 # 存放原始图片
├── labels.csv              # 图片评分标签
├── features_extract.py     # 步骤1：提取特征
├── train_score_model.py    # 步骤2：训练评分模型
├── predict_score.py        # 步骤3：预测评分
├── run_all.py              # 一键执行
├── output/                 # 模型和预测输出
│   ├── image_features.npy
│   ├── labels.npy
│   ├── score_model.pt
│   └── predicted_scores.csv
└── ...

```