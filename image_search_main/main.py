import argparse
import os
import glob
from search import search_similar

def batch_search_images(input_dir, output_dir=None, topk=5):
    """
    批量搜索图片功能
    
    Args:
        input_dir: 输入图片目录
        output_dir: 输出结果目录（可选）
        topk: 返回相似图片数量
    """
    # 支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']
    
    # 获取所有图片文件
    image_files = []
    for ext in image_extensions:
        pattern = os.path.join(input_dir, ext)
        image_files.extend(glob.glob(pattern))
        # 也搜索大写扩展名
        pattern = os.path.join(input_dir, ext.upper())
        image_files.extend(glob.glob(pattern))
    
    if not image_files:
        print(f"❌ 在目录 {input_dir} 中没有找到图片文件")
        return
    
    print(f"📁 找到 {len(image_files)} 个图片文件")
    
    # 创建输出目录
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")
    
    # 批量处理每个图片
    for i, image_path in enumerate(image_files, 1):
        print(f"\n🔍 处理第 {i}/{len(image_files)} 个图片: {os.path.basename(image_path)}")
        
        try:
            # 搜索相似图片
            results = search_similar(image_path, topk=topk, return_results=True)
            
            # 保存结果到文件
            if output_dir:
                output_file = os.path.join(output_dir, f"results_{os.path.splitext(os.path.basename(image_path))[0]}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"查询图片: {image_path}\n")
                    f.write(f"相似图片数量: {topk}\n")
                    f.write("-" * 50 + "\n")
                    for j, (result_path, distance) in enumerate(results, 1):
                        f.write(f"{j}. {os.path.basename(result_path)} (距离: {distance:.2f})\n")
                        f.write(f"   路径: {result_path}\n\n")
                print(f"✅ 结果已保存到: {output_file}")
            
        except Exception as e:
            print(f"❌ 处理图片 {image_path} 时出错: {str(e)}")
    
    print(f"\n🎉 批量处理完成！共处理 {len(image_files)} 个图片")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="以图搜图工具")
    parser.add_argument("input", help="要查询的图片路径或目录")
    parser.add_argument("--topk", type=int, default=5, help="返回相似图片数量")
    parser.add_argument("--output", help="输出结果目录（批量模式时使用）")
    parser.add_argument("--batch", action="store_true", help="批量处理模式")
    
    args = parser.parse_args()

    if args.batch or os.path.isdir(args.input):
        # 批量处理模式
        print("🚀 启动批量图片搜索模式")
        batch_search_images(args.input, args.output, args.topk)
    else:
        # 单张图片模式
        print("🔍 单张图片搜索模式")
        search_similar(args.input, topk=args.topk)