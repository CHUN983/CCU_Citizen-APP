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

    <!-- PWA Install Prompt -->
    <PWAInstallPrompt />
  </div>
</template>

<script setup>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
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

/* 移動端響應式樣式 */
@media (max-width: 768px) {
  .el-header {
    padding: 0 10px;
  }

  .el-main {
    padding: 10px;
  }
}

/* 針對小螢幕（手機）的額外優化 */
@media (max-width: 480px) {
  .el-main {
    padding: 8px;
  }
}
</style>
