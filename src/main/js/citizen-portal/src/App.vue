<template>
  <div id="app">
    <el-container>
      <el-header height="60px">
        <Header />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
      <el-footer height="60px">
        <Footer />
      </el-footer>
    </el-container>

    <!-- Bottom Navigation (Mobile Only) -->
    <BottomNavigation />

    <!-- PWA Install Prompt -->
    <PWAInstallPrompt />
  </div>
</template>

<script setup>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import BottomNavigation from './components/BottomNavigation.vue'
import PWAInstallPrompt from './components/PWAInstallPrompt.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.el-header {
  background-color: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-main {
  background-color: #f5f5f5;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.el-footer {
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

/* 移動端響應式樣式 - 適配底部導航欄布局 */
@media (max-width: 768px) {
  .el-header {
    padding: 0 10px;
    height: 60px !important; /* 手機版 Header 只顯示 App Icon，保持原高度 */
  }

  .el-main {
    padding: 10px;
    padding-bottom: 70px; /* 為底部導航欄留出空間 (60px + 10px 邊距) */
    min-height: calc(100vh - 120px); /* 調整主區域高度 (60px header + 60px bottom nav) */
  }

  /* 手機版隱藏 Footer，使用底部導航欄替代 */
  .el-footer {
    display: none;
  }
}

/* 針對小螢幕（手機）的額外優化 */
@media (max-width: 480px) {
  .el-main {
    padding: 8px;
    padding-bottom: 68px; /* 為底部導航欄留出空間 (60px + 8px 邊距) */
  }
}
</style>
