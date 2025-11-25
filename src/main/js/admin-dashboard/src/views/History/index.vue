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

      <!-- 主內容 -->
      <el-container>
        <el-header>
          <div class="header-content">
            <h2>操作紀錄</h2>
            <div class="user-info">
              <span>{{ userInfo?.username || '管理員' }}</span>
              <el-button type="danger" size="small" @click="handleLogout">
                登出
              </el-button>
            </div>
          </div>
        </el-header>

        <el-main>
          <!-- ====== 原本的 History 查詢區塊 ====== -->
          <div class="history-container">
            <el-card class="filter-card" shadow="never">
              <template #header>
                <div class="card-header">操作歷史查詢</div>
              </template>

              <el-form :inline="true" :model="filters">
                <el-form-item label="意見 ID">
                  <el-input
                    v-model="filters.opinion_id"
                    placeholder="輸入意見ID"
                    clearable
                    style="width: 160px"
                  />
                </el-form-item>

                <el-form-item label="時間範圍">
                  <el-date-picker
                    v-model="filters.time_range"
                    type="datetimerange"
                    start-placeholder="開始時間"
                    end-placeholder="結束時間"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="handleSearch">搜尋</el-button>
                  <el-button @click="handleReset">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>

            <el-card class="table-card" shadow="never" style="margin-top: 15px">
              <el-table :data="items" v-loading="loading" style="width:100%">
                <el-table-column prop="id" label="紀錄ID" width="90" />
                <el-table-column prop="opinion_id" label="意見ID" width="90" />
                <el-table-column prop="opinion_title" label="意見標題" min-width="180" />

                <el-table-column prop="action" label="操作類型" width="120">
                  <template #default="{ row }">
                    <el-tag size="small">{{ actionText(row.action) }}</el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="username" label="操作者" width="120" />

                <el-table-column label="狀態變更" width="180">
                  <template #default="{ row }">
                    <span v-if="row.old_status || row.new_status">
                      {{ row.old_status || '-' }} → {{ row.new_status || '-' }}
                    </span>
                    <span v-else>-</span>
                  </template>
                </el-table-column>

                <el-table-column prop="changes" label="變更內容" min-width="220">
                  <template #default="{ row }">
                    <pre class="changes-pre">{{ prettyJSON(row.changes) }}</pre>
                  </template>
                </el-table-column>

                <el-table-column prop="created_at" label="時間" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>

              <div class="pagination">
                <el-pagination
                  v-model:current-page="page"
                  v-model:page-size="pageSize"
                  :total="total"
                  :page-sizes="[10,20,50,100]"
                  layout="total, sizes, prev, pager, next, jumper"
                  @current-change="fetchData"
                  @size-change="handleSizeChange"
                />
              </div>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useDashBoardStore } from '../../store/DashBoard'
import { ElMessage } from 'element-plus'

const store = useDashBoardStore()

const page = ref(1)
const pageSize = ref(20)

const filters = reactive({
  opinion_id: '',
  time_range: null
})

const items = computed(() => store.history.items)
const total = computed(() => store.history.total)
const loading = computed(() => store.history.loading)

const fetchData = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }

    if (filters.opinion_id) params.opinion_id = Number(filters.opinion_id)

    if (filters.time_range?.length === 2) {
      params.start_time = filters.time_range[0]
      params.end_time = filters.time_range[1]
    }

    await store.fetchHistory(params)
  } catch (e) {
    ElMessage.error('載入操作紀錄失敗')
  }
}

const handleSearch = () => {
  page.value = 1
  fetchData()
}

const handleReset = () => {
  filters.opinion_id = ''
  filters.time_range = null
  handleSearch()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  page.value = 1
  fetchData()
}

const formatDate = (d) => new Date(d).toLocaleString('zh-TW')

const prettyJSON = (obj) => {
  if (!obj) return '-'
  try { return JSON.stringify(obj, null, 2) } 
  catch { return String(obj) }
}

const actionText = (action) => {
  const map = {
    created: '建立',
    updated: '更新',
    approved: '核准',
    rejected: '拒絕',
    merged: '合併',
    status_changed: '狀態變更'
  }
  return map[action] || action
}

onMounted(fetchData)
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

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}
.history-container {
  padding: 10px;
}
.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}
.changes-pre {
  font-size: 12px;
  white-space: pre-wrap;
  margin: 0;
}
</style>
