<template>
  <div class="opinion-create-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><EditPen /></el-icon>
          <span>提交新意見</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="標題" prop="title">
          <el-input
            v-model="form.title"
            placeholder="請輸入意見標題（3-200字符）"
            maxlength="200"
            show-word-limit
            clearable
          />
        </el-form-item>

        <el-form-item label="分類" prop="category_id">
          <el-select v-model="form.category_id" placeholder="請選擇分類" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="詳細內容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="請詳細描述您的意見或建議..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="位置">
          <el-input
            v-model="form.region"
            placeholder="請輸入相關位置（選填）"
            clearable
          >
            <template #prefix>
              <el-icon><Location /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="標籤">
          <el-input
            v-model="tagInput"
            placeholder="輸入標籤後按 Enter（選填）"
            @keyup.enter="handleAddTag"
          >
            <template #prefix>
              <el-icon><PriceTag /></el-icon>
            </template>
          </el-input>
          <div v-if="form.tags.length > 0" class="tags-display">
            <el-tag
              v-for="tag in form.tags"
              :key="tag"
              closable
              @close="handleRemoveTag(tag)"
              style="margin-right: 10px; margin-top: 10px"
            >
              {{ tag }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item>
          <el-alert
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px"
          >
            <template #title>
              <div>提交須知</div>
            </template>
            <ul style="margin: 0; padding-left: 20px">
              <li>請確保您的意見內容真實、準確</li>
              <li>禁止發布違法、不實或不當內容</li>
              <li>管理員將在 1-3 個工作日內審核您的意見</li>
              <li>審核通過後，您的意見將公開顯示</li>
            </ul>
          </el-alert>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit" size="large">
            <el-icon><Promotion /></el-icon>
            提交意見
          </el-button>
          <el-button @click="handleReset" size="large">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
          <el-button @click="$router.back()" size="large">
            <el-icon><Close /></el-icon>
            取消
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOpinionStore } from '../../store/opinion'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const opinionStore = useOpinionStore()

const formRef = ref(null)
const loading = ref(false)
const tagInput = ref('')

const categories = computed(() => opinionStore.categories)

const form = reactive({
  title: '',
  content: '',
  category_id: null,
  region: '',
  tags: []
})

const rules = {
  title: [
    { required: true, message: '請輸入標題', trigger: 'blur' },
    { min: 3, max: 200, message: '標題長度應在 3-200 之間', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '請輸入內容', trigger: 'blur' },
    { min: 10, max: 2000, message: '內容長度應在 10-2000 之間', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '請選擇分類', trigger: 'change' }
  ]
}

const handleAddTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !form.tags.includes(tag)) {
    if (form.tags.length >= 5) {
      ElMessage.warning('最多只能添加 5 個標籤')
      return
    }
    form.tags.push(tag)
    tagInput.value = ''
  }
}

const handleRemoveTag = (tag) => {
  const index = form.tags.indexOf(tag)
  if (index > -1) {
    form.tags.splice(index, 1)
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.tags = []
  tagInput.value = ''
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await ElMessageBox.confirm(
          '確認提交此意見？提交後將進入審核流程。',
          '確認提交',
          {
            confirmButtonText: '確認',
            cancelButtonText: '取消',
            type: 'info'
          }
        )

        loading.value = true

        const submitData = {
          title: form.title,
          content: form.content,
          category_id: form.category_id,
          status: 'pending'  // 提交後進入待審核狀態
        }

        if (form.region) submitData.region = form.region
        if (form.tags.length > 0) submitData.tags = form.tags

        await opinionStore.createOpinion(submitData)

        ElMessage.success('意見提交成功！等待管理員審核')
        router.push('/opinions')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.detail || '提交失敗，請稍後再試')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(async () => {
  // Fetch categories if not loaded
  if (categories.value.length === 0) {
    try {
      await opinionStore.fetchCategories()
    } catch (error) {
      ElMessage.error('載入分類失敗')
    }
  }
})
</script>

<style scoped>
.opinion-create-container {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
}

.tags-display {
  margin-top: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
}
</style>
