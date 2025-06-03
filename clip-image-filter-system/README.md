如何添加更多图片进行搜索？
将新图片放入data/images目录（或你在.env中配置的IMAGE_DIR）。
重新提取特征：
bash
python -m scripts.extract_features


重新构建索引：
bash
python -m scripts.build_index


重启 API 服务：
bash
source clip-image-filter-env/bin/activate 
uvicorn app.main:app --reload
KMP_DUPLICATE_LIB_OK=TRUE uvicorn app.main:app --reload --port 8000

