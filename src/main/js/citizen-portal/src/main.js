import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        console.log('[PWA] Service Worker registered successfully:', registration.scope)

        // Check for updates every 60 seconds
        setInterval(() => {
          registration.update()
        }, 60000)

        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          console.log('[PWA] New Service Worker found, installing...')

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('[PWA] New content available, please refresh.')
              // Could show a notification to user here
            }
          })
        })
      })
      .catch((error) => {
        console.error('[PWA] Service Worker registration failed:', error)
      })
  })

  // Listen for messages from Service Worker
  navigator.serviceWorker.addEventListener('message', (event) => {
    console.log('[PWA] Message from Service Worker:', event.data)
  })
}
