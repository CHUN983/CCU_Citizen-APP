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
        target: 'http://localhost:8000',
        changeOrigin: true,
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
