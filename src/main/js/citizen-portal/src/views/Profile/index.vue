<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8">
        <el-card>
          <div class="user-info">
            <el-avatar :size="100">
              <el-icon :size="50"><UserFilled /></el-icon>
            </el-avatar>
            <h2>{{ user?.username }}</h2>
            <p class="role-badge">
              <el-tag :type="getRoleType(user?.role)">{{ getRoleText(user?.role) }}</el-tag>
            </p>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="16">
        <el-card>
          <template #header>
            <span>個人資料</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用戶名">{{ user?.username }}</el-descriptions-item>
            <el-descriptions-item label="電子郵件">{{ user?.email }}</el-descriptions-item>
            <el-descriptions-item label="真實姓名">{{ user?.real_name || '未設定' }}</el-descriptions-item>
            <el-descriptions-item label="電話">{{ user?.phone || '未設定' }}</el-descriptions-item>
            <el-descriptions-item label="註冊時間">{{ formatDate(user?.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的意見</span>
              <el-button type="primary" size="small" @click="$router.push('/opinions/create')">
                <el-icon><Plus /></el-icon>
                提交新意見
              </el-button>
            </div>
          </template>
          <el-empty description="功能開發中..." />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed , onMounted } from 'vue'
import { useUserStore } from '../../store/user'

const userStore = useUserStore()

const user = computed(() => userStore.user)

onMounted(async () => {
  try {
    await userStore.getProfile()
  } catch (e) {
    console.error('載入個人資料失敗', e)
  }
})

const getRoleType = (role) => {
  const typeMap = {
    'admin': 'danger',
    'moderator': 'warning',
    'citizen': 'success'
  }
  return typeMap[role] || 'info'
}

const getRoleText = (role) => {
  const textMap = {
    'admin': '管理員',
    'moderator': '審核員',
    'citizen': '市民'
  }
  return textMap[role] || role
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW') + ' ' + date.toLocaleTimeString('zh-TW')
}
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

.user-info {
  text-align: center;
  padding: 20px;
}

.user-info h2 {
  margin: 15px 0 10px;
}

.role-badge {
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
