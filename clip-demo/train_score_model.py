# ------------------------------------------
# 2. train_score_model.py
# 从提取的特征训练一个评分分类器
# ------------------------------------------

import numpy as np
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
import os

# 路径设置
feature_dir = "output"
# 加载提取的特征和标签
features = np.load(os.path.join(feature_dir, "image_features.npy"))
labels = np.load(os.path.join(feature_dir, "labels.npy"))

X = torch.tensor(features, dtype=torch.float32)
y = torch.tensor(labels, dtype=torch.long)

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=64, shuffle=True)

# 定义简单的评分模型（MLP）
model = nn.Sequential(
    nn.Linear(X.shape[1], 256),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(256, 5)  # 5 个评分等级
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
loss_fn = nn.CrossEntropyLoss()

# 训练模型
for epoch in range(20):
    total_loss = 0
    for batch_x, batch_y in loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
    print(f"Epoch {epoch+1} loss: {total_loss / len(loader):.4f}")

# 保存模型
os.makedirs("output", exist_ok=True)
torch.save(model.state_dict(), "output/score_model.pt")
print("Model saved to output/score_model.pt")
