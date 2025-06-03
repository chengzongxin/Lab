import torch
import clip
from PIL import Image
import os

device = "cuda" if torch.cuda.is_available() else "cpu"

score_texts = [
    "terrible",
    "poor",
    "mediocre",
    "excellent",
    "outstanding"
]

def predict(image_path):
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.load_state_dict(torch.load("output/best.pt", map_location=device))
    model.eval()

    text_tokens = clip.tokenize(score_texts).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)

        similarity = (image_features @ text_features.T).squeeze(0)
        probs = similarity.softmax(dim=0)

        for text, prob in zip(score_texts, probs):
            print(f"{text}: {prob.item():.4f}")

        pred_idx = probs.argmax().item()
        print(f"Predicted rating: {score_texts[pred_idx]}")

if __name__ == "__main__":
    images_dir = "images"
    # 遍历目录下所有文件
    for filename in os.listdir(images_dir):
        # 只处理常见图片格式，可以根据需要扩展
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            image_path = os.path.join(images_dir, filename)
            print(f"Predicting for image: {image_path}")
            predict(image_path)
