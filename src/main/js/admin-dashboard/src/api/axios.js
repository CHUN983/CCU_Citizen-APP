import axios from 'axios'
import { ElMessage } from 'element-plus'

// 創建 axios 實例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 請求攔截器
request.interceptors.request.use(
  config => {
    // 從 localStorage 獲取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 響應攔截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error)

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          ElMessage.error('登入已過期，請重新登入')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('沒有權限執行此操作')
          break
        case 404:
          ElMessage.error('請求的資源不存在')
          break
        case 500:
          ElMessage.error('伺服器錯誤')
          break
        default:
          ElMessage.error(data.detail || '操作失敗')
      }
    } else {
      ElMessage.error('網路連線失敗')
    }

    return Promise.reject(error)
  }
)

export default request
