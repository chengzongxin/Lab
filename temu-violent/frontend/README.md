# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      ...tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      ...tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      ...tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

# React + Vite 前端部署与打包说明

## 1. 本地开发

```bash
npm install
npm run dev
```

---

## 2. 打包构建（生产环境）

```bash
npm run build
```
- 构建后静态文件在 `dist/` 目录下。

---

## 3. 本地预览

```bash
npm run preview -- --host
```
- 其他电脑可通过 `http://你的IP:4173` 访问。

---

## 4. 用 nginx 部署静态文件（推荐生产环境）

1. 安装 nginx（如 Ubuntu: `sudo apt install nginx`）。
2. 将 `dist/` 目录内容上传到服务器（如 `/var/www/temu-frontend`）。
3. 配置 nginx：

```nginx
server {
    listen 80;
    server_name your.domain.com;
    root /var/www/temu-frontend;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
4. 重载 nginx：
```bash
sudo nginx -s reload
```

---

## 5. 访问方式
- 浏览器访问 `http://your.domain.com` 或 `http://服务器IP`。
- 前端所有 `/api` 请求会自动转发到后端。

---

## 6. 用 Docker 部署前端项目（推荐自动化部署）

### 1. 打包前端静态文件
```bash
npm install
npm run build
```

### 2. 构建 Docker 镜像
```bash
docker build -t temu-frontend .
```

### 3. 运行 Docker 容器
```bash
docker run -d -p 3000:80 temu-frontend
```
这样你就可以通过 http://localhost:3000 访问前端页面。

- 现在可以通过 `http://localhost` 或 `http://服务器IP` 访问前端页面。
- 如需自定义 Nginx 配置，可将 `nginx.conf` 拷贝到项目根目录，并取消 Dockerfile 中相关注释。

---

如需详细部署帮助，请查阅本项目文档或联系开发者。
