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
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <el-icon :size="40" color="#409EFF"><Document /></el-icon>
                    <div class="stat-info">
                      <h3>{{ stats.totalOpinions }}</h3>
                      <p>總意見數</p>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <el-icon :size="40" color="#67C23A"><Check /></el-icon>
                    <div class="stat-info">
                      <h3>{{ stats.approvedOpinions }}</h3>
                      <p>已核准</p>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <el-icon :size="40" color="#E6A23C"><Clock /></el-icon>
                    <div class="stat-info">
                      <h3>{{ stats.pendingOpinions }}</h3>
                      <p>待審核</p>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <el-icon :size="40" color="#F56C6C"><Close /></el-icon>
                    <div class="stat-info">
                      <h3>{{ stats.rejectedOpinions }}</h3>
                      <p>已拒絕</p>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
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
import { opinionAPI } from '../../api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

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
  totalOpinions: 0,
  approvedOpinions: 0,
  pendingOpinions: 0,
  rejectedOpinions: 0
})

const refreshStats = async () => {
  try {
    const data = await opinionAPI.getOpinions({ page: 1, page_size: 100 })
    stats.value.totalOpinions = data.total || 0
    stats.value.approvedOpinions = data.items?.filter(item => item.status === 'approved').length || 0
    stats.value.pendingOpinions = data.items?.filter(item => item.status === 'pending').length || 0
    stats.value.rejectedOpinions = data.items?.filter(item => item.status === 'rejected').length || 0
    ElMessage.success('統計數據已更新')
  } catch (error) {
    console.error('Failed to fetch stats:', error)
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
