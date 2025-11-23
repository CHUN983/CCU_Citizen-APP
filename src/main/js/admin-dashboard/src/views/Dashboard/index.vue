<template>
  <div class="dashboard-container">
    <el-container>
      <!-- 側邊欄 -->
      <el-aside width="200px">
        <div class="logo">
          <h3>管理後台</h3>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Grid /></el-icon>
            <span>儀表板</span>
          </el-menu-item>
          <el-menu-item index="/opinions">
            <el-icon><Document /></el-icon>
            <span>意見管理</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><List /></el-icon>
            <span>操作紀錄</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主內容區 -->
      <el-container>
        <!-- 頂部欄 -->
        <el-header>
          <div class="header-content">
            <h2>{{ pageTitle }}</h2>
            <div class="user-info">
              <span>{{ userInfo?.username || '管理員' }}</span>
              <el-button type="danger" size="small" @click="handleLogout">
                登出
              </el-button>
            </div>
          </div>
        </el-header>

        <!-- 內容區 -->
        <el-main>
          <div class="stats-container">
            <StatsRow :items="overallItems" />

            <div style="margin-top:20px">
              <StatsRow :items="todayItems" />
            </div>

            <TopCategories :categories="stats.top_categories" />
          </div>

          <el-card class="quick-actions" shadow="hover">
            <template #header>
              <h3>快速操作</h3>
            </template>
            <el-button type="primary" @click="$router.push('/opinions')">
              查看所有意見
            </el-button>
            <el-button type="success" @click="refreshStats">
              刷新統計數據
            </el-button>
          </el-card>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Document, Check, Clock, Close } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import { useDashBoardStore } from '../../store/DashBoard'

import StatsRow from './components/StatsRow.vue'
import TopCategories from './components/TopCategories.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const dashBoardStore = useDashBoardStore()

const userInfo = computed(() => userStore.userInfo)
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '儀表板',
    '/opinions': '意見管理'
  }
  return titles[route.path] || '管理後台'
})

const stats = ref({
  overall: { total: 0, approved: 0, pending: 0, rejected: 0 },
  today: { total: 0, approved: 0, pending: 0, rejected: 0 },
  top_categories: []
})

const overallItems = computed(() => ([
  { key:'total', label:'總意見數', value: stats.value.overall.total, icon: Document, color:'#409EFF' },
  { key:'approved', label:'已核准', value: stats.value.overall.approved, icon: Check, color:'#67C23A' },
  { key:'pending', label:'待審核', value: stats.value.overall.pending, icon: Clock, color:'#E6A23C' },
  { key:'rejected', label:'已拒絕', value: stats.value.overall.rejected, icon: Close, color:'#F56C6C' }
]))

const todayItems = computed(() => ([
  { key:'today_total', label:'今日意見數', value: stats.value.today.total, icon: Document, color:'#409EFF' },
  { key:'today_approved', label:'今日核准', value: stats.value.today.approved, icon: Check, color:'#67C23A' },
  { key:'today_pending', label:'今日待審核', value: stats.value.today.pending, icon: Clock, color:'#E6A23C' },
  { key:'today_rejected', label:'今日拒絕', value: stats.value.today.rejected, icon: Close, color:'#F56C6C' }
]))

const refreshStats = async () => {
  try {
    stats.value = await dashBoardStore.fetchStats()
    ElMessage.success('統計數據已更新')
  } catch (e) {
    console.error(e)
    ElMessage.error('載入統計失敗')
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('確定要登出嗎？', '提示', {
    confirmButtonText: '確定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已登出')
  }).catch(() => {})
}

onMounted(async () => {
  await userStore.getUserInfo()
  await refreshStats()
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.logo {
  padding: 20px;
  text-align: center;
  background-color: #2b3a4b;
  color: #fff;
}

.logo h3 {
  margin: 0;
}

.el-aside {
  background-color: #304156;
  height: 100vh;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #606266;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.stats-container {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info h3 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.quick-actions {
  margin-top: 20px;
}

.quick-actions h3 {
  margin: 0;
}
</style>
