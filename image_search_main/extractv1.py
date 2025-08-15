import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
from PIL import Image

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

model = resnet50(pretrained=True)
model.eval()

def extract_feature(image_path):
    img = Image.open(image_path).convert('RGB')
    tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        feature = model(tensor)
    return feature.squeeze().numpy()