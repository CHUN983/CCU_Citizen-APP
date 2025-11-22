<template>
  <div style="padding: 50px; text-align: center;">
    <h1 style="color: #409eff;">✅ Vue 應用正常運作！</h1>
    <p style="font-size: 18px;">如果您看到這個頁面，說明 Vue 路由和組件加載都正常。</p>

    <div style="margin: 30px 0;">
      <el-button type="primary" @click="testCount++">
        點擊測試 ({{ testCount }})
      </el-button>
    </div>

    <el-card style="max-width: 600px; margin: 20px auto;">
      <h3>系統資訊</h3>
      <p>當前時間：{{ currentTime }}</p>
      <p>Vue 版本：{{ vueVersion }}</p>
      <p>路由路徑：{{ $route.path }}</p>
    </el-card>

    <div style="margin-top: 30px;">
      <el-button @click="$router.push('/')">返回首頁</el-button>
      <el-button @click="$router.push('/opinions')">意見列表</el-button>
      <el-button @click="$router.push('/login')">登入</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { version } from 'vue'

const testCount = ref(0)
const currentTime = ref(new Date().toLocaleString('zh-TW'))
const vueVersion = version

setInterval(() => {
  currentTime.value = new Date().toLocaleString('zh-TW')
}, 1000)
</script>
