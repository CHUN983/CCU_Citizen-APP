import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,          // 或寫 0.0.0.0
    port: 5190,
    strictPort: true,
    // hmr: {
    //   host: 'localhost', // 讓瀏覽器用 localhost 與 dev server 建立 WebSocket
    //   port: 5174
    // },
    proxy: {
      '/api': {
        target: 'https://localhost:8000',
        changeOrigin: true,
        secure: false, // ← 必加！否則本機自簽證書會被擋
        rewrite: (path) => path.replace(/^\/api/, '')
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
