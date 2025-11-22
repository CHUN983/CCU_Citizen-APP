<template>
  <div class="dashboard-container">
    <el-container>
      <el-aside width="200px">
        <div class="logo">
          <h3>管理後台</h3>
        </div>
        <el-menu
          default-active="/opinions"
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

      <el-container>
        <el-header>
          <div class="header-content">
            <div>
              <el-button @click="$router.back()">
                <el-icon><ArrowLeft /></el-icon>
                返回
              </el-button>
              <span style="margin-left: 20px; font-size: 20px; font-weight: bold;">
                意見詳情
              </span>
            </div>
            <div class="user-info">
              <span>{{ userStore.userInfo?.username || '管理員' }}</span>
              <el-button type="danger" size="small" @click="handleLogout">
                登出
              </el-button>
            </div>
          </div>
        </el-header>

        <el-main v-loading="loading">
          <el-card v-if="opinion" shadow="never">
            <!-- 意見資訊 -->
            <div class="opinion-header">
              <h2>{{ opinion.title }}</h2>
              <el-tag :type="getStatusType(opinion.status)" size="large">
                {{ getStatusText(opinion.status) }}
              </el-tag>
            </div>

            <el-descriptions :column="2" border class="opinion-info">
              <el-descriptions-item label="意見 ID">{{ opinion.id }}</el-descriptions-item>
              <el-descriptions-item label="發表者">{{ opinion.username || '匿名' }}</el-descriptions-item>
              <el-descriptions-item label="地區">{{ opinion.region || '無' }}</el-descriptions-item>
              <el-descriptions-item label="狀態">
                <el-tag :type="getStatusType(opinion.status)">
                  {{ getStatusText(opinion.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="票數">
                  <el-icon color="#67c23a"><CaretTop /></el-icon>
                    {{ opinion.upvotes }}
                  <el-icon color="#f56c6c"><CaretBottom /></el-icon>
                    {{ opinion.downvotes }}
              </el-descriptions-item>
              <el-descriptions-item label="留言數">{{ opinion.comment_count }}</el-descriptions-item>
              <el-descriptions-item label="建立時間">
                {{ formatDate(opinion.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="更新時間">
                {{ formatDate(opinion.updated_at) }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 意見內容 -->
            <div class="opinion-content">
              <h3>意見內容</h3>
              <p>{{ opinion.content }}</p>
            </div>

            <!-- 媒體附件 -->
            <div v-if="opinion.media && opinion.media.length > 0" class="opinion-media">
              <h3>附件 ({{ opinion.media.length }} 個檔案)</h3>
              <div class="media-grid">
                <div
                  v-for="media in opinion.media"
                  :key="media.id"
                  class="media-item"
                >
                  <el-image
                    v-if="media.media_type === 'image'"
                    :src="getMediaUrl(media)"
                    :preview-src-list="imageMediaList"
                    fit="cover"
                    class="media-image"
                  >
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                        <span>載入失敗</span>
                      </div>
                    </template>
                  </el-image>
                  <div v-else-if="media.media_type === 'video'" class="video-wrapper">
                    <video
                      :src="getMediaUrl(media)"
                      controls
                      class="media-video"
                    >
                      您的瀏覽器不支援影片播放
                    </video>
                  </div>
                  <div class="media-info">
                    <el-tag size="small" :type="media.media_type === 'image' ? 'success' : 'primary'">
                      {{ media.media_type === 'image' ? '圖片' : '影片' }}
                    </el-tag>
                    <span class="file-size">{{ formatFileSize(media.file_size) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按鈕 -->
            <div class="opinion-actions">
              <el-button
                v-if="opinion.status === 'pending'"
                type="success"
                size="large"
                @click="handleApprove"
              >
                <el-icon><Check /></el-icon>
                核准意見
              </el-button>
              <el-button
                v-if="opinion.status === 'pending'"
                type="danger"
                size="large"
                @click="handleReject"
              >
                <el-icon><Close /></el-icon>
                拒絕意見
              </el-button>
            </div>
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
import { Grid, Document, ArrowLeft, Check, Close, Picture } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import { opinionAPI } from '../../api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const opinion = ref(null)

const fetchOpinionDetail = async () => {
  loading.value = true
  try {
    const data = await opinionAPI.getOpinionDetail(route.params.id)
    opinion.value = data
  } catch (error) {
    console.error('Failed to fetch opinion detail:', error)
    ElMessage.error('載入失敗')
    router.back()
  } finally {
    loading.value = false
  }
}

const handleApprove = async () => {
  try {
    await ElMessageBox.confirm('確定要核准這個意見嗎？', '確認', {
      confirmButtonText: '確定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await opinionAPI.approveOpinion(opinion.value.id)
    ElMessage.success('核准成功！')
    await fetchOpinionDetail()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Approve failed:', error)
    }
  }
}

const handleReject = async (id) => {
  try {
    const { value, action } = await ElMessageBox.prompt(
      '請輸入拒絕原因（必填）：',
      '拒絕意見',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '例如：內容與主題無關、含不適當言論等',
        inputValidator: (val) => {
          if (!val || !val.trim()) {
            return '拒絕原因不得為空'
          }
          return true
        },
        inputErrorMessage: '拒絕原因不得為空',
        type: 'warning'
      }
    )

    if (action === 'confirm') {
      await opinionAPI.rejectOpinion(id, value)
      ElMessage.success('已拒絕')
      fetchOpinions()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Reject failed:', error)
    }
  }
}

const getStatusType = (status) => {
  const types = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    resolved: 'primary'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    pending: '待審核',
    approved: '已核准',
    rejected: '已拒絕',
    resolved: '已解決'
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-TW')
}

const getMediaUrl = (media) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}/media/files/${media.media_type}/${media.file_path.split('/').pop()}`
}

const imageMediaList = computed(() => {
  if (!opinion.value?.media) return []
  return opinion.value.media
    .filter(m => m.media_type === 'image')
    .map(m => getMediaUrl(m))
})

const formatFileSize = (bytes) => {
  if (!bytes) return '未知大小'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
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

onMounted(() => {
  fetchOpinionDetail()
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

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.opinion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.opinion-header h2 {
  margin: 0;
}

.opinion-info {
  margin-bottom: 20px;
}

.opinion-content {
  margin: 20px 0;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.opinion-content h3 {
  margin-top: 0;
}

.opinion-content p {
  line-height: 1.8;
  white-space: pre-wrap;
}

.opinion-media {
  margin: 20px 0;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.opinion-media h3 {
  margin-top: 0;
  margin-bottom: 15px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
}

.media-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.media-image {
  width: 100%;
  height: 200px;
  cursor: pointer;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.video-wrapper {
  width: 100%;
  background: #000;
}

.media-video {
  width: 100%;
  max-height: 300px;
}

.media-info {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.opinion-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}
</style>
