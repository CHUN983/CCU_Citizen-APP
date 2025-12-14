import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.spec.js',
        '**/*.test.js'
      ]
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://140.123.105.199:8443/',
        changeOrigin: true,
        secure: false, // 允許自簽名證書
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
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-vendor': ['vue', 'vue-router', 'pinia']
        }
      }
    }
  }
})
