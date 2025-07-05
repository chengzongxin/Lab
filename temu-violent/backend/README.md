# FastAPI 后端部署与打包说明

source venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

## 1. 直接运行（开发/测试）

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 2. 打包为可执行文件（PyInstaller，适合分发给不会装 Python 的用户）

### 安装 PyInstaller
```bash
pip install pyinstaller
```

### 打包
```bash
pyinstaller --onefile main.py
```
- 生成的可执行文件在 `dist/` 目录下，直接运行即可：
  ```bash
  ./dist/main
  ```

---

## 3. Docker 镜像打包（推荐生产环境）

### 新建 Dockerfile（已提供示例）
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir fastapi uvicorn
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 构建镜像
```bash
docker build -t temu-backend .
```

### 运行容器
```bash
docker run -d -p 8000:8000 temu-backend
```
---

## 4. 依赖管理

建议将依赖写入 `requirements.txt`，如：
```
fastapi
uvicorn
requests
```

---

如需详细打包/部署帮助，请查阅本项目文档或联系开发者。 