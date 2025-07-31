import os
import numpy as np
import json
from tqdm import tqdm
from extractv1 import extract_feature

image_dir = "E:/shop/images"  # TODO: 修改为你的图片路径


def get_all_image_files(root_dir):
    """
    递归获取所有图片文件
    支持的文件格式：.jpg, .jpeg, .png, .bmp, .gif, .tiff
    """
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    image_files = []
    
    print(f"🔍 正在扫描目录：{root_dir}")
    
    # 递归遍历所有子文件夹
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(root, file)
                image_files.append(full_path)
    
    return image_files

# 图片目录路径

# 检查图片目录是否存在
if not os.path.exists(image_dir):
    print(f"❌ 错误：图片目录不存在：{image_dir}")
    print("请修改 build_index.py 中的 image_dir 变量为正确的图片路径")
    exit(1)

# 获取所有图片文件（包括子文件夹）
print("📁 正在扫描所有图片文件...")
image_files = get_all_image_files(image_dir)

if not image_files:
    print(f"❌ 错误：在目录 {image_dir} 及其子文件夹中没有找到图片文件")
    print("支持的格式：.jpg, .jpeg, .png, .bmp, .gif, .tiff")
    exit(1)

print(f"📁 找到 {len(image_files)} 个图片文件")

features = []
paths = []
failed_files = []

# 处理每个图片文件
for image_path in tqdm(image_files, desc="处理图片"):
    try:
        feat = extract_feature(image_path)
        features.append(feat)
        paths.append(image_path)
        print(f"✅ 成功处理：{os.path.basename(image_path)}")
    except Exception as e:
        error_msg = f"❌ 跳过损坏图片：{os.path.basename(image_path)} - 错误：{str(e)}"
        print(error_msg)
        failed_files.append((image_path, str(e)))

# 检查是否成功提取了特征
if not features:
    print("\n❌ 错误：没有成功提取任何图片特征")
    print("可能的原因：")
    print("1. 图片文件损坏或格式不支持")
    print("2. 没有足够的磁盘空间")
    print("3. 缺少必要的依赖包")
    print("4. 图片文件权限问题")
    
    if failed_files:
        print("\n失败的图片文件：")
        for file_path, error in failed_files[:5]:  # 只显示前5个错误
            print(f"  - {os.path.basename(file_path)}: {error}")
        if len(failed_files) > 5:
            print(f"  ... 还有 {len(failed_files) - 5} 个文件失败")
    
    exit(1)

# 保存特征和路径
print(f"\n💾 正在保存特征数据...")
features_np = np.vstack(features).astype('float32')
np.save("feature_cache.npy", features_np)

with open("path_cache.json", "w", encoding="utf-8") as f:
    json.dump(paths, f, ensure_ascii=False)

print("✅ 特征库构建完成！")
print(f"📊 统计信息：")
print(f"  - 成功处理：{len(paths)} 个图片")
print(f"  - 失败文件：{len(failed_files)} 个")
print(f"  - 特征维度：{features_np.shape}")

if failed_files:
    print(f"\n⚠️  有 {len(failed_files)} 个文件处理失败，详细信息已在上方显示")