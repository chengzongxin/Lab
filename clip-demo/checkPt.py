import torch

path = "/Users/chengzongxin/.cache/clip/ViT-B-32.pt"
state_dict = torch.load(path, map_location="cpu", weights_only=False)
print(state_dict)
