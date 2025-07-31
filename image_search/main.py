import argparse
from search import search_similar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="以图搜图工具")
    parser.add_argument("image", help="要查询的图片路径")
    parser.add_argument("--topk", type=int, default=5, help="返回相似图片数量")
    args = parser.parse_args()

    search_similar(args.image, topk=args.topk)