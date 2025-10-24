<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="hero-card">
          <div class="hero-content">
            <el-icon :size="80" color="#409eff"><ChatDotRound /></el-icon>
            <h1>歡迎來到市民意見平台</h1>
            <p class="subtitle">讓您的聲音被聽見，參與城市規劃決策</p>
            <div class="action-buttons">
              <el-button type="primary" size="large" @click="$router.push('/opinions')">
                <el-icon><View /></el-icon>
                瀏覽意見
              </el-button>
              <el-button v-if="isLoggedIn" type="success" size="large" @click="$router.push('/opinions/create')">
                <el-icon><EditPen /></el-icon>
                提交意見
              </el-button>
              <el-button v-else type="success" size="large" @click="$router.push('/register')">
                <el-icon><UserFilled /></el-icon>
                立即註冊
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :xs="24" :sm="8">
        <el-card class="feature-card">
          <el-icon :size="40" color="#409eff"><EditPen /></el-icon>
          <h3>提交意見</h3>
          <p>針對城市規劃、公共設施等議題提出您的意見和建議</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="feature-card">
          <el-icon :size="40" color="#67c23a"><Select /></el-icon>
          <h3>投票表決</h3>
          <p>對其他市民的意見進行投票，支持您認同的提案</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="feature-card">
          <el-icon :size="40" color="#e6a23c"><ChatDotSquare /></el-icon>
          <h3>討論交流</h3>
          <p>在意見下方留言討論，與其他市民交流想法</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最新意見</span>
              <el-link type="primary" @click="$router.push('/opinions')">查看更多 →</el-link>
            </div>
          </template>
          <div v-loading="loading">
            <el-empty v-if="!loading && recentOpinions.length === 0" description="暫無意見" />
            <div v-else class="opinion-list">
              <div
                v-for="opinion in recentOpinions"
                :key="opinion.opinion_id"
                class="opinion-item"
                @click="$router.push(`/opinions/${opinion.opinion_id}`)"
              >
                <h4>{{ opinion.title }}</h4>
                <p class="description">{{ opinion.content }}</p>
                <div class="meta">
                  <el-tag size="small" type="info">{{ opinion.category_name }}</el-tag>
                  <span class="status">{{ getStatusText(opinion.status) }}</span>
                  <span class="votes">
                    <el-icon><CaretTop /></el-icon>
                    {{ opinion.upvotes }}
                    <el-icon><CaretBottom /></el-icon>
                    {{ opinion.downvotes }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../store/user'
import { useOpinionStore } from '../../store/opinion'

const userStore = useUserStore()
const opinionStore = useOpinionStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const loading = ref(false)
const recentOpinions = ref([])

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待審核',
    'approved': '已通過',
    'rejected': '已拒絕',
    'under_review': '審核中',
    'in_progress': '處理中',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await opinionStore.fetchOpinions({ page: 1, page_size: 5, status: 'approved' })
    recentOpinions.value = data.items || []
  } catch (error) {
    console.error('Failed to fetch recent opinions:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-card {
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.hero-card :deep(.el-card__body) {
  padding: 60px 20px;
}

.hero-content h1 {
  font-size: 36px;
  margin: 20px 0 10px;
}

.subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-card {
  text-align: center;
  margin-top: 20px;
}

.feature-card :deep(.el-card__body) {
  padding: 30px 20px;
}

.feature-card h3 {
  margin: 15px 0 10px;
  font-size: 20px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.opinion-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.opinion-item {
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.opinion-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.opinion-item h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.description {
  color: #606266;
  font-size: 14px;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.meta {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
  color: #909399;
}

.votes {
  display: flex;
  align-items: center;
  gap: 5px;
}

@media (max-width: 768px) {
  .hero-content h1 {
    font-size: 28px;
  }

  .subtitle {
    font-size: 16px;
  }
}
</style>
