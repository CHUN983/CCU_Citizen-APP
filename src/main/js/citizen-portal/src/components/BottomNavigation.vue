<template>
  <div class="bottom-navigation">
    <div
      class="nav-item"
      :class="{ active: activeIndex === '/' }"
      @click="navigate('/')"
    >
      <el-icon :size="24"><HomeFilled /></el-icon>
      <span class="nav-label">首頁</span>
    </div>

    <div
      class="nav-item"
      :class="{ active: activeIndex === '/opinions' }"
      @click="navigate('/opinions')"
    >
      <el-icon :size="24"><Search /></el-icon>
      <span class="nav-label">瀏覽</span>
    </div>

    <div
      v-if="isLoggedIn"
      class="nav-item"
      :class="{ active: activeIndex === '/opinions/create' }"
      @click="navigate('/opinions/create')"
    >
      <el-icon :size="24"><EditPen /></el-icon>
      <span class="nav-label">發表</span>
    </div>
    <div
      v-else
      class="nav-item"
      @click="navigate('/login')"
    >
      <el-icon :size="24"><EditPen /></el-icon>
      <span class="nav-label">發表</span>
    </div>

    <div
      class="nav-item notification-item"
      :class="{ active: showNotifications }"
      @click="toggleNotifications"
    >
      <el-badge :value="unreadCount" :hidden="!hasUnread">
        <el-icon :size="24"><Bell /></el-icon>
      </el-badge>
      <span class="nav-label">通知</span>
    </div>

    <div
      class="nav-item"
      :class="{ active: activeIndex === '/profile' || showUserMenu }"
      @click="toggleUserMenu"
    >
      <el-icon :size="24"><User /></el-icon>
      <span class="nav-label">個人</span>
    </div>

    <!-- Notification Popup -->
    <transition name="slide-up">
      <div v-if="showNotifications" class="popup-panel notification-panel">
        <div class="panel-header">
          <span class="panel-title">通知</span>
          <el-button
            v-if="hasUnread && isLoggedIn"
            link
            size="small"
            @click.stop="markAllAsRead"
          >
            全部已讀
          </el-button>
          <el-button
            link
            size="small"
            @click.stop="toggleNotifications"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <el-scrollbar max-height="60vh">
          <div v-if="!isLoggedIn" class="login-prompt">
            <el-empty description="請先登入查看通知" :image-size="80" />
            <el-button type="primary" @click="navigate('/login')">登入</el-button>
          </div>
          <div v-else-if="notifications.length === 0" class="no-notifications">
            <el-empty description="暫無通知" :image-size="80" />
          </div>
          <div
            v-else
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.is_read }"
            @click="handleNotificationClick(notification.id)"
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
          </div>
        </el-scrollbar>
      </div>
    </transition>

    <!-- User Menu Popup -->
    <transition name="slide-up">
      <div v-if="showUserMenu" class="popup-panel user-panel">
        <div class="panel-header">
          <span class="panel-title">{{ isLoggedIn ? username : '訪客' }}</span>
          <el-button
            link
            size="small"
            @click.stop="toggleUserMenu"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="user-menu-content">
          <template v-if="isLoggedIn">
            <div class="menu-item" @click="navigate('/profile')">
              <el-icon><User /></el-icon>
              <span>個人資料</span>
            </div>
            <div class="menu-item logout" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              <span>登出</span>
            </div>
          </template>
          <template v-else>
            <div class="menu-item" @click="navigate('/login')">
              <el-icon><User /></el-icon>
              <span>登入</span>
            </div>
            <div class="menu-item" @click="navigate('/register')">
              <el-icon><UserFilled /></el-icon>
              <span>註冊</span>
            </div>
          </template>
        </div>
      </div>
    </transition>

    <!-- Backdrop -->
    <transition name="fade">
      <div
        v-if="showNotifications || showUserMenu"
        class="backdrop"
        @click="closeAllPanels"
      ></div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import { useNotificationStore } from '../store/notification'
import { ElMessage } from 'element-plus'
import {
  HomeFilled, Search, EditPen, Bell, User, UserFilled,
  Star, ChatDotRound, CircleCheck, CircleClose, Close, SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const showNotifications = ref(false)
const showUserMenu = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const username = computed(() => userStore.username)
const activeIndex = computed(() => route.path)
const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const hasUnread = computed(() => notificationStore.hasUnread)

const navigate = (path) => {
  closeAllPanels()
  router.push(path)
}

const toggleNotifications = () => {
  showUserMenu.value = false
  showNotifications.value = !showNotifications.value

  if (showNotifications.value && isLoggedIn.value) {
    notificationStore.fetchNotifications()
  }
}

const toggleUserMenu = () => {
  showNotifications.value = false
  showUserMenu.value = !showUserMenu.value
}

const closeAllPanels = () => {
  showNotifications.value = false
  showUserMenu.value = false
}

const handleNotificationClick = async (notificationId) => {
  try {
    await notificationStore.markAsRead(notificationId)

    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification && notification.opinion_id) {
      closeAllPanels()
      router.push(`/opinions/${notification.opinion_id}`)
    }
  } catch (error) {
    ElMessage.error('操作失敗')
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

const handleLogout = () => {
  notificationStore.clearNotifications()
  userStore.logout()
  ElMessage.success('登出成功')
  closeAllPanels()
  router.push('/')
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)

  if (diff < 60) return '剛剛'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分鐘前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小時前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-TW')
}

onMounted(() => {
  if (isLoggedIn.value) {
    notificationStore.fetchNotifications()
    notificationStore.startPolling(30000)
  }
})

onUnmounted(() => {
  notificationStore.stopPolling()
})
</script>

<style scoped>
.bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #909399;
  transition: all 0.3s ease;
  padding: 8px 0;
  position: relative;
}

.nav-item:hover {
  color: #409eff;
  background-color: #f5f7fa;
}

.nav-item.active {
  color: #409eff;
}

.nav-label {
  font-size: 12px;
  margin-top: 4px;
}

.notification-item {
  position: relative;
}

/* Popup Panels */
.popup-panel {
  position: fixed;
  bottom: 60px;
  left: 0;
  right: 0;
  background-color: #fff;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  max-height: 70vh;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fff;
  position: sticky;
  top: 0;
  z-index: 1;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.login-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  gap: 16px;
}

.no-notifications {
  padding: 40px 20px;
  text-align: center;
}

/* Notification Styles */
.notification-panel .notification-item {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-panel .notification-item:hover {
  background-color: #f5f7fa;
}

.notification-panel .notification-item.unread {
  background-color: #f0f9ff;
}

.notification-panel .notification-item.unread:hover {
  background-color: #e6f4ff;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
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
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409eff;
}

/* User Menu Styles */
.user-menu-content {
  padding: 8px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: #303133;
  font-size: 15px;
}

.menu-item:hover {
  background-color: #f5f7fa;
}

.menu-item.logout {
  color: #f56c6c;
}

/* Backdrop */
.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Design */
@media (min-width: 769px) {
  .bottom-navigation {
    display: none;
  }
}
</style>
