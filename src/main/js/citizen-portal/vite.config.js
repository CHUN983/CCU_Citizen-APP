import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,          // 或寫 0.0.0.0
    port: 5190,
    https: false,
    strictPort: true,
    // hmr: {
    //   host: 'localhost', // 讓瀏覽器用 localhost 與 dev server 建立 WebSocket
    //   port: 5174
    // },
    proxy: {
      '/api': {
        target: 'https://140.123.105.199:8443/',  // 更新為 HTTPS 端口
        changeOrigin: true,
        secure: false, // ← 必加！忽略自簽名證書
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/media': {
        target: 'https://140.123.105.199:8443/',  // 媒體文件代理
        changeOrigin: true,
        secure: false, // 忽略自簽名證書
        // 不需要 rewrite，直接轉發 /media 路徑
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 将 node_modules 中的依赖打包成一个 vendor chunk
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        }
      }
    }
  }
})
