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

          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="已通過" name="approved">
              <div v-loading="myOpinionsLoading">
                <el-empty
                  v-if="!myOpinionsLoading && approvedOpinions.length === 0"
                  description="目前沒有已通過的意見"
                />

                <div v-else class="opinion-list">
                  <div
                    v-for="op in approvedOpinions"
                    :key="op.id"
                    class="opinion-item"
                    @click="$router.push(`/opinions/${op.id}`)"
                  >
                    <div class="opinion-header">
                      <h3 class="opinion-title">{{ op.title }}</h3>
                      <el-tag type="success" size="small">已通過</el-tag>
                    </div>
                    <p class="opinion-content">{{ op.content }}</p>
                    <div class="opinion-meta">
                      <el-tag size="small">{{ op.category_name }}</el-tag>
                      <span class="stats">
                        <el-icon><View /></el-icon>
                        {{ op.view_count || 0 }}
                      </span>
                      <span class="stats">
                        <el-icon><ChatDotRound /></el-icon>
                        {{ op.comment_count || 0 }}
                      </span>
                      <span class="stats">
                        <el-icon><Star /></el-icon>
                        {{ op.upvotes || 0 }}
                      </span>
                      <span class="date">{{ formatDate(op.created_at) }}</span>
                    </div>
                  </div>

                  <!-- 分頁 -->
                  <div class="pagination" v-if="myOpinionsTotal > myOpinionsPageSize">
                    <el-pagination
                      v-model:current-page="myOpinionsCurrentPage"
                      :page-size="myOpinionsPageSize"
                      :total="myOpinionsTotal"
                      layout="total, prev, pager, next"
                      @current-change="handleMyOpinionsPageChange"
                    />
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="審核中" name="pending">
              <div v-loading="myOpinionsLoading">
                <el-empty
                  v-if="!myOpinionsLoading && pendingOpinions.length === 0"
                  description="目前沒有審核中的意見"
                />

                <div v-else class="opinion-list">
                  <div
                    v-for="op in pendingOpinions"
                    :key="op.id"
                    class="opinion-item"
                    @click="$router.push(`/opinions/${op.id}`)"
                  >
                    <div class="opinion-header">
                      <h3 class="opinion-title">{{ op.title }}</h3>
                      <el-tag type="warning" size="small">審核中</el-tag>
                    </div>
                    <p class="opinion-content">{{ op.content }}</p>
                    <div class="opinion-meta">
                      <el-tag size="small">{{ op.category_name }}</el-tag>
                      <span class="date">{{ formatDate(op.created_at) }}</span>
                    </div>
                  </div>

                  <!-- 分頁 -->
                  <div class="pagination" v-if="myOpinionsTotal > myOpinionsPageSize">
                    <el-pagination
                      v-model:current-page="myOpinionsCurrentPage"
                      :page-size="myOpinionsPageSize"
                      :total="myOpinionsTotal"
                      layout="total, prev, pager, next"
                      @current-change="handleMyOpinionsPageChange"
                    />
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        <el-card>
          <template #header>
            <div class="card-header">
              <span>收藏意見</span>
            </div>
          </template>
          <div v-loading="bookmarksLoading">
            <el-empty
              v-if="!bookmarksLoading && bookmarks.length === 0"
              description="目前尚未收藏任何意見"
            />

            <div v-else class="bookmark-list">
              <div
                v-for="op in bookmarks"
                :key="op.id"
                class="bookmark-item"
                @click="$router.push(`/opinions/${op.id}`)"
              >
                <h3 class="bookmark-title">
                  {{ op.title }}
                </h3>
                <p class="bookmark-content">
                  {{ op.content }}
                </p>
                <div class="bookmark-meta">
                  <el-tag size="small">{{ op.category_name }}</el-tag>
                  <span class="author">
                    <el-icon><UserFilled /></el-icon>
                    {{ op.username || '匿名' }}
                  </span>
                  <span class="date">
                    {{ formatDate(op.created_at) }}
                  </span>
                </div>
              </div>

              <!-- 分頁 -->
              <div class="pagination" v-if="bookmarksTotal > pageSize">
                <el-pagination
                  v-model:current-page="currentPage"
                  :page-size="pageSize"
                  :total="bookmarksTotal"
                  layout="total, prev, pager, next"
                  @current-change="handlePageChange"
                />
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
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const opinionStore = useOpinionStore()

const bookmarks = computed(() => opinionStore.bookmarkedOpinions)
const bookmarksLoading = computed(() => opinionStore.bookmarkedLoading)
const bookmarksTotal = computed(() => opinionStore.bookmarkedTotal)

// 我的意見相關
const myOpinionsLoading = computed(() => opinionStore.myOpinionsLoading)
const myOpinionsTotal = computed(() => opinionStore.myOpinionsTotal)
const activeTab = ref('approved')
const myOpinionsCurrentPage = ref(1)
const myOpinionsPageSize = ref(10)

// 根據當前標籤頁過濾意見
const approvedOpinions = computed(() =>
  opinionStore.myOpinions.filter(op => op.status === 'approved')
)

const pendingOpinions = computed(() =>
  opinionStore.myOpinions.filter(op => op.status === 'pending')
)

// 分頁控制
const currentPage = ref(1)
const pageSize = ref(5)

const user = computed(() => userStore.user)

const fetchMyOpinions = async () => {
  try {
    const status = activeTab.value === 'approved' ? 'approved' : 'pending'
    await opinionStore.fetchMyOpinions(
      myOpinionsCurrentPage.value,
      myOpinionsPageSize.value,
      status
    )
  } catch (e) {
    console.error('載入我的意見失敗', e)
    ElMessage.error('載入我的意見失敗')
  }
}

const handleTabChange = (tabName) => {
  activeTab.value = tabName
  myOpinionsCurrentPage.value = 1
  fetchMyOpinions()
}

const handleMyOpinionsPageChange = (page) => {
  myOpinionsCurrentPage.value = page
  fetchMyOpinions()
}

const fetchBookmarks = async () => {
  try {
    await opinionStore.fetchBookmarkedOpinions(currentPage.value, pageSize.value)
  } catch (e) {
    console.error('載入收藏意見失敗', e)
    ElMessage.error('載入收藏意見失敗')
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchBookmarks()
}

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

onMounted(async () => {
  try {
    await userStore.getProfile()
  } catch (e) {
    console.error('載入個人資料失敗', e)
  }

  if (userStore.isLoggedIn) {
    await fetchMyOpinions()
    await fetchBookmarks()
  }
})
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

.bookmark-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bookmark-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.bookmark-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.opinion-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.opinion-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.opinion-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.opinion-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.opinion-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  flex: 1;
  color: #303133;
}

.opinion-content {
  margin: 10px 0;
  color: #606266;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.opinion-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 15px;
  color: #909399;
  font-size: 14px;
}

.opinion-meta .stats {
  display: flex;
  align-items: center;
  gap: 4px;
}

.opinion-meta .date {
  margin-left: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
