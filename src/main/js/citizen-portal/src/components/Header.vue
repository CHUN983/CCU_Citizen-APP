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
        <!-- Notification Icon -->
        <el-badge :value="unreadCount" :hidden="!hasUnread" class="notification-badge">
          <el-dropdown trigger="click" @command="handleNotificationCommand" @visible-change="handleNotificationDropdown">
            <el-button circle class="notification-button">
              <el-icon :size="20"><Bell /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="notification-dropdown">
                <div class="notification-header">
                  <span class="notification-title">通知</span>
                  <el-button
                    v-if="hasUnread"
                    link
                    size="small"
                    @click.stop="markAllAsRead"
                  >
                    全部已讀
                  </el-button>
                </div>
                <el-scrollbar max-height="400px">
                  <div v-if="notifications.length === 0" class="no-notifications">
                    <el-empty description="暫無通知" :image-size="80" />
                  </div>
                  <el-dropdown-item
                    v-for="notification in notifications"
                    :key="notification.id"
                    :command="notification.id"
                    :class="{ 'unread': !notification.is_read }"
                    class="notification-item"
                  >
                    <div class="notification-content">
                      <div class="notification-icon">
                        <el-icon v-if="notification.type === 'like'" color="#409eff"><Star /></el-icon>
                        <el-icon v-else-if="notification.type === 'comment'" color="#67c23a"><ChatDotRound /></el-icon>
                        <el-icon v-else-if="notification.type === 'approved'" color="#67c23a"><CircleCheck /></el-icon>
                        <el-icon v-else-if="notification.type === 'rejected'" color="#f56c6c"><CircleClose /></el-icon>
                        <el-icon v-else color="#909399"><Bell /></el-icon>
                      </div>
                      <div class="notification-text">
                        <div class="notification-item-title">{{ notification.title }}</div>
                        <div class="notification-item-content">{{ notification.content }}</div>
                        <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                      </div>
                      <div v-if="!notification.is_read" class="unread-dot"></div>
                    </div>
                  </el-dropdown-item>
                </el-scrollbar>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-badge>

        <!-- User Dropdown -->
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
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import { useNotificationStore } from '../store/notification'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const username = computed(() => userStore.username)
const activeIndex = computed(() => route.path)
const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const hasUnread = computed(() => notificationStore.hasUnread)

const handleSelect = (key) => {
  router.push(key)
}

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    notificationStore.clearNotifications()
    userStore.logout()
    ElMessage.success('登出成功')
    router.push('/')
  }
}

const handleNotificationCommand = async (notificationId) => {
  try {
    await notificationStore.markAsRead(notificationId)

    // Find notification and navigate to opinion if available
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification && notification.opinion_id) {
      router.push(`/opinions/${notification.opinion_id}`)
    }
  } catch (error) {
    ElMessage.error('操作失敗')
  }
}

const handleNotificationDropdown = (visible) => {
  if (visible && isLoggedIn.value) {
    // Refresh notifications when dropdown opens
    notificationStore.fetchNotifications()
  }
}

const markAllAsRead = async () => {
  try {
    await notificationStore.markAllAsRead()
    ElMessage.success('已全部標記為已讀')
  } catch (error) {
    ElMessage.error('操作失敗')
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000) // seconds

  if (diff < 60) return '剛剛'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分鐘前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小時前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-TW')
}

onMounted(() => {
  if (isLoggedIn.value) {
    // Fetch notifications on mount
    notificationStore.fetchNotifications()
    // Start polling for new notifications
    notificationStore.startPolling(30000) // Poll every 30 seconds
  }
})

onUnmounted(() => {
  // Stop polling when component unmounts
  notificationStore.stopPolling()
})
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
  gap: 15px;
}

.notification-badge {
  margin-right: 5px;
}

.notification-button {
  background-color: transparent;
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
}

.notification-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: #fff;
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

/* Notification Dropdown Styles */
.notification-dropdown {
  min-width: 360px;
  max-width: 420px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.notification-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.no-notifications {
  padding: 20px;
  text-align: center;
}

.notification-item {
  padding: 0 !important;
}

.notification-item.unread {
  background-color: #f0f9ff;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  width: 100%;
  position: relative;
}

.notification-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.notification-text {
  flex: 1;
  min-width: 0;
}

.notification-item-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.4;
}

.notification-item-content {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.unread-dot {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409eff;
  flex-shrink: 0;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread:hover {
  background-color: #e6f4ff;
}
</style>
