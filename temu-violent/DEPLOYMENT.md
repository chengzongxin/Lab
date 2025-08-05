# Docker 云服务器部署指南

## 1. 云服务器环境准备

### 1.1 安装 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 1.2 安装 Docker Compose
```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 1.3 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8080/tcp  # 应用端口
sudo ufw allow 22/tcp    # SSH

# 启用防火墙
sudo ufw enable
```

## 2. 项目部署

### 2.1 上传项目到服务器
```bash
# 方法1：使用 Git
git clone <your-repo-url>
cd temu-violent

# 方法2：使用 SCP
scp -r ./temu-violent user@your-server:/home/user/
```

### 2.2 配置环境变量（可选）
```bash
# 创建环境变量文件
cp backend/config.example.json backend/config.json
# 编辑配置文件
nano backend/config.json
```

### 2.3 执行部署
```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

## 3. 生产环境优化

### 3.1 使用 Docker Compose 生产配置
```bash
# 创建生产环境配置
cp docker-compose.yml docker-compose.prod.yml

# 编辑生产配置，添加：
# - 环境变量
# - 数据卷持久化
# - 日志配置
# - 资源限制
```

### 3.2 配置 HTTPS（推荐）
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 更新 Nginx 配置支持 HTTPS
```

### 3.3 配置域名解析
```bash
# 在域名服务商处添加 A 记录
# 类型: A
# 主机记录: @ 或 www
# 记录值: 你的服务器 IP
```

## 4. 监控和维护

### 4.1 查看服务状态
```bash
# 查看所有容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4.2 更新部署
```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 4.3 备份和恢复
```bash
# 备份数据
docker-compose exec backend tar -czf /app/backup-$(date +%Y%m%d).tar.gz /app/data

# 恢复数据
docker-compose exec backend tar -xzf /app/backup-20231201.tar.gz -C /app/
```

## 5. 常见问题

### 5.1 端口冲突
```bash
# 检查端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# 修改 docker-compose.yml 中的端口映射
```

### 5.2 内存不足
```bash
# 查看系统资源
docker stats

# 限制容器资源使用
# 在 docker-compose.yml 中添加：
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

### 5.3 磁盘空间不足
```bash
# 清理 Docker 资源
docker system prune -a

# 清理日志
docker-compose logs --tail=100
```

## 6. 安全建议

### 6.1 网络安全
- 使用防火墙限制端口访问
- 配置 HTTPS 加密传输
- 定期更新系统和 Docker 版本

### 6.2 容器安全
- 使用非 root 用户运行容器
- 限制容器资源使用
- 定期扫描镜像漏洞

### 6.3 数据安全
- 定期备份重要数据
- 使用数据卷持久化存储
- 加密敏感配置文件

## 7. 性能优化

### 7.1 Nginx 优化
```nginx
# 在 nginx-proxy.conf 中添加：
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
```

### 7.2 后端优化
```python
# 在 main.py 中添加：
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        access_log=True
    )
```

### 7.3 数据库优化（如果有）
- 配置连接池
- 优化查询语句
- 定期清理无用数据 