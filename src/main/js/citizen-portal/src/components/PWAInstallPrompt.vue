<template>
  <transition name="slide-up">
    <div v-if="showPrompt" class="pwa-install-prompt">
      <div class="prompt-content">
        <div class="prompt-icon">
          <el-icon :size="32" color="#409eff"><Download /></el-icon>
        </div>
        <div class="prompt-text">
          <h3>安裝市民平台 APP</h3>
          <p>安裝到手機桌面，隨時隨地參與城市規劃</p>
        </div>
        <div class="prompt-actions">
          <el-button type="primary" @click="installPWA" :loading="installing">
            安裝
          </el-button>
          <el-button text @click="dismissPrompt">
            稍後再說
          </el-button>
        </div>
        <el-button
          class="close-btn"
          text
          circle
          @click="closePrompt"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Download, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const showPrompt = ref(false)
const installing = ref(false)
const deferredPrompt = ref(null)

onMounted(() => {
  // Check if already dismissed
  const dismissed = localStorage.getItem('pwa-install-dismissed')
  const installed = localStorage.getItem('pwa-installed')

  if (dismissed || installed) {
    return
  }

  // Listen for beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', (e) => {
    console.log('[PWA] beforeinstallprompt event fired')

    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault()

    // Stash the event so it can be triggered later
    deferredPrompt.value = e

    // Show the install prompt after 3 seconds
    setTimeout(() => {
      showPrompt.value = true
    }, 3000)
  })

  // Listen for app installed event
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed successfully')
    showPrompt.value = false
    localStorage.setItem('pwa-installed', 'true')
    ElMessage.success('APP 安裝成功！')
  })

  // Check if already installed (standalone mode)
  if (window.matchMedia('(display-mode: standalone)').matches) {
    console.log('[PWA] App is running in standalone mode')
    localStorage.setItem('pwa-installed', 'true')
  }

  // iOS detection (iOS doesn't support beforeinstallprompt)
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream
  const isStandalone = window.navigator.standalone === true

  if (isIOS && !isStandalone && !dismissed) {
    // Show iOS installation instructions after 5 seconds
    setTimeout(() => {
      showIOSInstructions()
    }, 5000)
  }
})

const installPWA = async () => {
  if (!deferredPrompt.value) {
    ElMessage.warning('您的瀏覽器不支援 APP 安裝功能')
    return
  }

  installing.value = true

  try {
    // Show the install prompt
    deferredPrompt.value.prompt()

    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.value.userChoice
    console.log(`[PWA] User response: ${outcome}`)

    if (outcome === 'accepted') {
      ElMessage.success('感謝您安裝市民平台！')
      localStorage.setItem('pwa-installed', 'true')
    } else {
      ElMessage.info('您可以稍後從瀏覽器選單安裝')
    }

    // Clear the deferred prompt
    deferredPrompt.value = null
    showPrompt.value = false
  } catch (error) {
    console.error('[PWA] Installation error:', error)
    ElMessage.error('安裝失敗，請稍後再試')
  } finally {
    installing.value = false
  }
}

const dismissPrompt = () => {
  showPrompt.value = false
  // Don't show again for 7 days
  const dismissUntil = Date.now() + (7 * 24 * 60 * 60 * 1000)
  localStorage.setItem('pwa-install-dismissed', dismissUntil.toString())
}

const closePrompt = () => {
  showPrompt.value = false
}

const showIOSInstructions = () => {
  ElMessage({
    message: '在 Safari 瀏覽器中，點擊「分享」按鈕，然後選擇「加入主畫面」即可安裝 APP',
    type: 'info',
    duration: 10000,
    showClose: true
  })
}
</script>

<style scoped>
.pwa-install-prompt {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  padding: 16px;
  animation: slideUp 0.3s ease-out;
}

.prompt-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.prompt-icon {
  flex-shrink: 0;
}

.prompt-text {
  flex: 1;
  min-width: 0;
}

.prompt-text h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.prompt-text p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.prompt-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.close-btn {
  position: absolute;
  top: -8px;
  right: -8px;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out, opacity 0.3s ease-out;
}

.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@media (max-width: 768px) {
  .prompt-content {
    flex-wrap: wrap;
  }

  .prompt-text {
    flex-basis: 100%;
    order: 2;
  }

  .prompt-icon {
    order: 1;
  }

  .prompt-actions {
    order: 3;
    flex-basis: 100%;
    margin-top: 8px;
  }

  .prompt-actions button {
    flex: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
