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
          <el-menu-item index="/history">
            <el-icon><List /></el-icon>
            <span>操作紀錄</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header>
          <div class="header-content">
            <h2>意見管理</h2>
            <div class="user-info">
              <span>{{ userStore.userInfo?.username || '管理員' }}</span>
              <el-button type="danger" size="small" @click="handleLogout">
                登出
              </el-button>
            </div>
          </div>
        </el-header>

        <el-main>
          <!-- 篩選條件 -->
          <el-card class="filter-card" shadow="never">
            <el-form :inline="true">
              <el-form-item label="狀態">
                <el-select v-model="filterStatus" placeholder="全部" @change="fetchOpinions">
                  <el-option label="全部" value="" />
                  <el-option label="草稿" value="draft" />
                  <el-option label="待審核" value="pending" />
                  <el-option label="已核准" value="approved" />
                  <el-option label="已拒絕" value="rejected" />
                  <el-option label="已解決" value="resolved" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="fetchOpinions">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 意見列表 -->
          <el-card class="table-card" shadow="never">
            <el-table
              v-loading="loading"
              :data="opinions"
              style="width: 100%"
              @row-click="handleRowClick"
            >
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="標題" min-width="200" />
              <el-table-column prop="username" label="發表者" width="120" />
              <el-table-column prop="status" label="狀態" width="100">
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusType(row.status)"
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="upvotes" label="贊同數" width="80" />
              <el-table-column prop="downvotes" label="反對數" width="80" />
              <el-table-column prop="comment_count" label="留言數" width="90" />
              <el-table-column prop="created_at" label="建立時間" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="280" fixed="right">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="primary"
                    @click.stop="handleView(row.id)"
                  >
                    查看
                  </el-button>
                  <el-button
                    v-if="row.status === 'pending'"
                    size="small"
                    type="success"
                    @click.stop="handleApprove(row.id)"
                  >
                    核准
                  </el-button>
                  <el-button
                    v-if="row.status === 'pending'"
                    size="small"
                    type="danger"
                    @click.stop="handleReject(row.id)"
                  >
                    拒絕
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分頁 -->
            <div class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="fetchOpinions"
                @current-change="fetchOpinions"
              />
            </div>
          </el-card>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Document, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import { opinionAPI } from '../../api'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const opinions = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')

const fetchOpinions = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }

    const data = await opinionAPI.getOpinions(params)
    opinions.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('Failed to fetch opinions:', error)
    ElMessage.error('載入失敗')
  } finally {
    loading.value = false
  }
}

const handleView = (id) => {
  router.push(`/opinions/${id}`)
}

const handleRowClick = (row) => {
  handleView(row.id)
}

const handleApprove = async (id) => {
  try {
    await ElMessageBox.confirm('確定要核准這個意見嗎？', '確認', {
      confirmButtonText: '確定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await opinionAPI.approveOpinion(id)
    ElMessage.success('核准成功！')
    fetchOpinions()
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
  fetchOpinions()
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

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-table {
  cursor: pointer;
}
</style>
