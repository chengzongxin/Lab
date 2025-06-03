import torch
import clip
from PIL import Image
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import os
device = "cuda" if torch.cuda.is_available() else "cpu"
import torch
torch.autograd.set_detect_anomaly(True)
# 映射函数：评分 -> 标签索引
def score_to_label(score):
    if score < 2:
        return 0
    elif score < 3:
        return 1
    elif score < 4:
        return 2
    elif score < 4.5:
        return 3
    else:
        return 4

score_texts = [
    "terrible",
    "poor",
    "mediocre",
    "excellent",
    "outstanding"
]

class ImageDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.data['label'] = self.data['score'].apply(score_to_label)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        image = Image.open(row['image_path']).convert('RGB')
        label = row['label']
        return image, label

def collate_fn(batch):
    images, labels = zip(*batch)
    return images, torch.tensor(labels)

def main():
    # 加载模型
    model, preprocess = clip.load("ViT-B/32", device=device)

    dataset = ImageDataset("labels.csv")
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True, collate_fn=collate_fn)

    optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)
    loss_fn = torch.nn.CrossEntropyLoss()

    # 预先编码文本描述
    text_tokens = clip.tokenize(score_texts).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    model.train()
    for epoch in range(10):
        total_loss = 0
        for images, labels in dataloader:
            images = torch.stack([preprocess(img) for img in images]).to(device)
            labels = labels.to(device)

            image_features = model.encode_image(images)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            # 计算相似度
            logits = (image_features @ text_features.T) * 100.0

            loss = loss_fn(logits, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
        print(f"Epoch {epoch+1} finished, loss: {total_loss / len(dataloader):.4f}")

    os.makedirs("output", exist_ok=True)
    torch.save(model.state_dict(), "output/best.pt")

if __name__ == "__main__":
    main()
