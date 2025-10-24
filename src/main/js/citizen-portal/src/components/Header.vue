<template>
  <div class="header-container">
    <div class="logo" @click="$router.push('/')">
      <el-icon :size="24"><ChatDotRound /></el-icon>
      <span class="title">市民意見平台</span>
    </div>

    <div class="nav-menu">
      <el-menu
        mode="horizontal"
        :default-active="activeIndex"
        background-color="#409eff"
        text-color="#fff"
        active-text-color="#ffd04b"
        @select="handleSelect"
      >
        <el-menu-item index="/">首頁</el-menu-item>
        <el-menu-item index="/opinions">意見列表</el-menu-item>
        <el-menu-item v-if="isLoggedIn" index="/opinions/create">提交意見</el-menu-item>
      </el-menu>
    </div>

    <div class="user-section">
      <template v-if="isLoggedIn">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon :size="20"><User /></el-icon>
            <span>{{ username }}</span>
            <el-icon :size="12"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">個人資料</el-dropdown-item>
              <el-dropdown-item command="logout" divided>登出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <el-button type="primary" plain @click="$router.push('/login')">登入</el-button>
        <el-button type="success" @click="$router.push('/register')">註冊</el-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const username = computed(() => userStore.username)
const activeIndex = computed(() => route.path)

const handleSelect = (key) => {
  router.push(key)
}

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    userStore.logout()
    ElMessage.success('登出成功')
    router.push('/')
  }
}
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 20px;
  font-weight: bold;
}

.title {
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  margin: 0 30px;
}

.nav-menu :deep(.el-menu) {
  border-bottom: none;
}

.nav-menu :deep(.el-menu-item) {
  border-bottom: none !important;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #fff;
  padding: 0 10px;
}

.user-info:hover {
  opacity: 0.8;
}
</style>
