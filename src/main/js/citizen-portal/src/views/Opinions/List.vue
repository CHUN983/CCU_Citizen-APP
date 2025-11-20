<template>
  <div class="opinion-list-container">
    <el-row :gutter="20">
      <!-- Filter Sidebar -->
      <el-col :xs="24" :sm="24" :md="6">
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <el-icon><Filter /></el-icon>
              <span>篩選條件</span>
            </div>
          </template>

          <el-form :model="filters" label-position="top">
            <el-form-item label="關鍵字搜尋">
              <el-input
                v-model="filters.search"
                placeholder="搜尋標題或內容"
                clearable
                @clear="handleSearch"
              >
                <template #append>
                  <el-button :icon="Search" @click="handleSearch" />
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="分類">
              <el-select v-model="filters.category_id" placeholder="選擇分類" clearable @change="handleSearch">
                <el-option
                  v-for="category in categories"
                  :key="category.category_id"
                  :label="category.name"
                  :value="category.category_id"
                />
              </el-select>
            </el-form-item>

            <!-- <el-form-item label="狀態">
              <el-select v-model="filters.status" placeholder="選擇狀態" clearable @change="handleSearch">
                <el-option label="待審核" value="pending" />
                <el-option label="已通過" value="approved" />
                <el-option label="審核中" value="under_review" />
                <el-option label="處理中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已拒絕" value="rejected" />
              </el-select>
            </el-form-item> -->

            <el-form-item label="排序方式">
              <el-select v-model="filters.sort_by" placeholder="選擇排序" @change="handleSearch">
                <el-option label="最新發布" value="created_at" />
                <el-option label="最多投票" value="upvotes" />
                <el-option label="最多留言" value="comment_count" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSearch" style="width: 100%">
                <el-icon><Search /></el-icon>
                搜尋
              </el-button>
              <el-button @click="handleReset" style="width: 100%; margin-top: 10px">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Opinion List -->
      <el-col :xs="24" :sm="24" :md="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>意見列表 (共 {{ total }} 條)</span>
              <el-button v-if="isLoggedIn" type="primary" @click="$router.push('/opinions/create')">
                <el-icon><Plus /></el-icon>
                提交意見
              </el-button>
            </div>
          </template>

          <div v-loading="loading">
            <el-empty v-if="!loading && opinions.length === 0" description="暫無意見" />

            <div v-else class="opinions-container">
              <div
                v-for="opinion in opinions"
                :key="index"
                class="opinion-card"
                @click="$router.push(`/opinions/${opinion.id}`)"
              >
                <div class="opinion-main">
                  <h3>{{ opinion.title }}</h3>
                  <p class="content">{{ opinion.content }}</p>

                  <div class="opinion-meta">
                    <el-tag size="small">{{ opinion.category_name }}</el-tag>
                    <el-tag size="small" :type="getStatusType(opinion.status)">
                      {{ getStatusText(opinion.status) }}
                    </el-tag>
                    <span class="author">
                      <el-icon><User /></el-icon>
                      {{ opinion.author_name || '匿名' }}
                    </span>
                    <span class="date">
                      <el-icon><Clock /></el-icon>
                      {{ formatDate(opinion.created_at) }}
                    </span>
                  </div>

                  <div class="opinion-stats">
                    <span class="stat-item">
                      <el-icon color="#67c23a"><CaretTop /></el-icon>
                      {{ opinion.upvotes }}
                    </span>
                    <span class="stat-item">
                      <el-icon color="#f56c6c"><CaretBottom /></el-icon>
                      {{ opinion.downvotes }}
                    </span>
                    <span class="stat-item">
                      <el-icon><ChatDotRound /></el-icon>
                      {{ opinion.comment_count || 0 }} 留言
                    </span>
                  </div>
                </div>
              </div>

              <!-- Pagination -->
              <div class="pagination-container">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="total"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
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
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { useOpinionStore } from '../../store/opinion'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const opinionStore = useOpinionStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const loading = computed(() => opinionStore.loading)
const opinions = computed(() => opinionStore.opinions)
const categories = computed(() => opinionStore.categories)
const total = ref(0)

const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  search: '',
  category_id: null,
  status: 'approved',
  sort_by: 'created_at'
})

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

const fetchOpinions = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filters.search) params.search = filters.search
    if (filters.category_id !== null && filters.category_id !== undefined) {
      params.category_id = filters.category_id
    }
    if (filters.status) params.status = filters.status
    if (filters.sort_by) params.sort_by = filters.sort_by

    console.log('params:', params)

    const data = await opinionStore.fetchOpinions(params)
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error('載入意見列表失敗')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchOpinions()
}

const handleReset = () => {
  filters.search = ''
  filters.category_id = null
  filters.status = 'approved'
  filters.sort_by = 'created_at'
  handleSearch()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchOpinions()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchOpinions()
}

// Auto-refresh mechanism
let refreshInterval = null

onMounted(async () => {
  // Fetch categories
  try {
    await opinionStore.fetchCategories()
    console.log('categories:', categories.value)
  } catch (error) {
    console.error('Failed to fetch categories:', error)
    // Don't block rendering on error
  }

  // Fetch opinions
  try {
    await fetchOpinions()
    
  } catch (error) {
    console.error('Failed to fetch opinions:', error)
    // Don't block rendering on error
  }
  // Set up auto-refresh every 30 seconds
  refreshInterval = setInterval(() => {
    fetchOpinions()
  }, 30000) // 30 seconds
})

onUnmounted(() => {
  // Clean up interval on component unmount
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})
</script>

<style scoped>
.opinion-list-container {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  position: sticky;
  top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-weight: bold;
}

.opinions-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.opinion-card {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.opinion-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.opinion-main h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}

.content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 15px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.opinion-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  font-size: 14px;
  color: #909399;
}

.opinion-stats {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #606266;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .filter-card {
    position: static;
    margin-bottom: 20px;
  }

  .opinion-meta {
    font-size: 12px;
  }

  .pagination-container :deep(.el-pagination) {
    flex-wrap: wrap;
  }
}
</style>
