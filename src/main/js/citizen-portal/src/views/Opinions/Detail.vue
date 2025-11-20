<template>
  <div class="opinion-detail-container">
    <el-button class="back-button" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      返回列表
    </el-button>

    <div v-loading="loading">
      <el-card v-if="opinion" class="opinion-card">
        <!-- Opinion Header -->
        <div class="opinion-header">
          <h1>{{ opinion.title }}</h1>
          <div class="meta-info">
            <el-tag size="large">{{ opinion.category_name }}</el-tag>
            <el-tag size="large" :type="getStatusType(opinion.status)">
              {{ getStatusText(opinion.status) }}
            </el-tag>
          </div>
        </div>

        <!-- Opinion Content -->
        <div class="opinion-content">
          <p>{{ opinion.content }}</p>
        </div>

        <!-- Location Info -->
        <div v-if="opinion.location" class="location-info">
          <el-icon><Location /></el-icon>
          <span>位置：{{ opinion.location }}</span>
        </div>

        <!-- Opinion Meta -->
        <div class="opinion-footer">
          <div class="author-info">
            <el-icon><User /></el-icon>
            <span>{{ opinion.username || '匿名' }}</span>
          </div>
          <div class="date-info">
            <el-icon><Clock /></el-icon>
            <span>{{ formatDate(opinion.created_at) }}</span>
          </div>
        </div>

        <!-- Voting Section -->
        <el-divider />
        <div class="voting-section">
          <div class="vote-buttons">
            <el-button
              :type="opinion.user_vote === 'up' ? 'success' : 'default'"
              :disabled="!isLoggedIn"
              @click="handleVote('like')"
            >
              <el-icon><CaretTop /></el-icon>
              支持 ({{ opinion.upvotes }})
            </el-button>
            <el-button
              :type="opinion.user_vote === 'down' ? 'danger' : 'default'"
              :disabled="!isLoggedIn"
              @click="handleVote('support')"
            >
              <el-icon><CaretBottom /></el-icon>
              反對 ({{ opinion.downvotes }})
            </el-button>
            <el-button
              :type="opinion.is_bookmarked ? 'warning' : 'default'"
              :disabled="!isLoggedIn"
              @click="handleBookmark"
            >
              <el-icon><Star /></el-icon>
              {{ opinion.is_bookmarked ? '已收藏' : '收藏' }}
            </el-button>
          </div>
          <el-alert
            v-if="!isLoggedIn"
            type="info"
            :closable="false"
            show-icon
          >
            請先<el-link type="primary" @click="$router.push('/login')">登入</el-link>後才能投票或收藏
          </el-alert>
        </div>
      </el-card>

      <!-- Comments Section -->
      <el-card class="comments-card" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <span><el-icon><ChatDotRound /></el-icon> 留言討論 ({{ comments.length }})</span>
          </div>
        </template>

        <!-- Comment Input -->
        <div v-if="isLoggedIn" class="comment-input-section">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="3"
            placeholder="發表您的看法..."
            maxlength="500"
            show-word-limit
          />
          <el-button
            type="primary"
            :loading="commentLoading"
            :disabled="!newComment.trim()"
            @click="handleSubmitComment"
            style="margin-top: 10px"
          >
            <el-icon><Promotion /></el-icon>
            發表留言
          </el-button>
        </div>
        <el-alert
          v-else
          type="info"
          :closable="false"
          show-icon
        >
          請先<el-link type="primary" @click="$router.push('/login')">登入</el-link>後才能發表留言
        </el-alert>

        <el-divider v-if="comments.length > 0" />

        <!-- Comments List -->
        <div v-loading="commentsLoading" class="comments-list">
          <el-empty v-if="!commentsLoading && comments.length === 0" description="暫無留言" />
          <div
            v-for="comment in comments"
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-header">
              <div class="comment-author">
                <el-icon><User /></el-icon>
                <span>{{ comment.author_name || '匿名' }}</span>
              </div>
              <div class="comment-date">
                {{ formatDate(comment.created_at) }}
              </div>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { useOpinionStore } from '../../store/opinion'
import { commentAPI } from '../../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const opinionStore = useOpinionStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const opinion = computed(() => opinionStore.currentOpinion)
const loading = ref(false)

const comments = ref([])
const commentsLoading = ref(false)
const newComment = ref('')
const commentLoading = ref(false)


const opinionId = computed(() => parseInt(route.params.id))

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'under_review': 'info',
    'in_progress': 'primary',
    'completed': 'success'
  }
  return typeMap[status] || 'info'
}

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

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW') + ' ' + date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

const handleVote = async (voteType) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('請先登入')
    return
  }

  try {
    await opinionStore.voteOpinion(opinionId.value, voteType)
    ElMessage.success('投票成功')
  } catch (error) {
    ElMessage.error(error.detail || '投票失敗')
  }
}

const handleBookmark = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('請先登入')
    return
  }

  try {
    if (opinion.value.is_bookmarked) {
      await opinionStore.unbookmarkOpinion(opinionId.value)
      ElMessage.success('已取消收藏')
    } else {
      await opinionStore.bookmarkOpinion(opinionId.value)
      ElMessage.success('收藏成功')
    }
    // Refresh opinion data
    await fetchOpinion()
  } catch (error) {
    ElMessage.error(error.detail || '操作失敗')
  }
}

const fetchOpinion = async () => {
  loading.value = true
  try {

    await opinionStore.fetchOpinionById(opinionId.value)
  } catch (error) {
    ElMessage.error('載入意見失敗')
    router.back()
  } finally {
    loading.value = false
  }
}

const fetchComments = async () => {
  commentsLoading.value = true
  try {
    const data = await commentAPI.getList(opinionId.value, { limit: 50 })
    comments.value = data || []
  } catch (error) {
    console.error('Failed to fetch comments:', error)
  } finally {
    commentsLoading.value = false
  }
}

const handleSubmitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('請輸入留言內容')
    return
  }

  commentLoading.value = true
  try {
    await commentAPI.create(opinionId.value, { content: newComment.value })
    ElMessage.success('留言發表成功')
    newComment.value = ''
    // Refresh comments
    await fetchComments()
  } catch (error) {
    ElMessage.error(error.detail || '發表留言失敗')
  } finally {
    commentLoading.value = false
  }
}

onMounted(async () => {
  
  await fetchOpinion()
  await fetchComments()
})
</script>

<style scoped>
.opinion-detail-container {
  max-width: 1000px;
  margin: 0 auto;
}

.back-button {
  margin-bottom: 20px;
}

.opinion-header {
  margin-bottom: 20px;
}

.opinion-header h1 {
  font-size: 28px;
  margin: 0 0 15px 0;
  color: #303133;
}

.meta-info {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.opinion-content {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
  margin: 20px 0;
  white-space: pre-wrap;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  margin: 15px 0;
  font-size: 14px;
}

.opinion-footer {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-top: 20px;
  font-size: 14px;
  color: #909399;
}

.author-info,
.date-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.voting-section {
  padding: 20px 0;
}

.vote-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.comment-input-section {
  margin-bottom: 20px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #303133;
}

.comment-date {
  font-size: 12px;
  color: #909399;
}

.comment-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .opinion-header h1 {
    font-size: 22px;
  }

  .opinion-content {
    font-size: 14px;
  }

  .vote-buttons {
    flex-direction: column;
  }

  .vote-buttons .el-button {
    width: 100%;
  }
}
</style>
