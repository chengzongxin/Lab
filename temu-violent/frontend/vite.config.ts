import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 根据环境选择不同的 API 地址
  const apiTarget = mode === 'development' 
    ? 'http://localhost:8000'  // 本地开发
    : 'http://localhost:8082'; // Docker 环境（通过 nginx-proxy）

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    // 生产环境构建配置
    build: {
      rollupOptions: {
        output: {
          manualChunks: undefined,
        },
      },
    },
  }
})
