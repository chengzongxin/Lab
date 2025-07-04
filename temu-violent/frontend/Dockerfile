# 基于官方 Nginx 镜像
FROM nginx:alpine

# 拷贝前端打包后的静态文件到 Nginx 默认目录
COPY dist/ /usr/share/nginx/html/

# 拷贝自定义 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 