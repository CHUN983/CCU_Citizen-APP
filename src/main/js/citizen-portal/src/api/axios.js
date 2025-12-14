import axios from 'axios'
import { Capacitor } from '@capacitor/core'

// 在移動應用中使用 WSL2 IP，在網頁中使用相對路徑
const getBaseURL = () => {
  // 開發模式：檢測是否為 Android 模擬器
  const isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development'

  if (Capacitor.isNativePlatform()) {
    // Android 模擬器：使用 10.0.2.2 訪問主機的 SSH 隧道
    // 需要先在主機上執行：ssh -L 8443:140.123.105.199:8443 se_city@140.123.105.199
    if (isDevelopment) {
      return 'https://10.0.2.2:8443/'
    }
    // 生產模式：直接訪問遠端伺服器（真實手機 + VPN）
    return 'https://140.123.105.199:8443/'
  }
  // 網頁瀏覽器：直接訪問遠端伺服器
  return 'https://140.123.105.199:8443/'
}

const instance = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add token
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
instance.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      // Token expired or invalid
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
      return Promise.reject(error.response.data)
    }
    return Promise.reject(error)
  }
)

console.log('Axios baseURL:', instance.defaults.baseURL)
export default instance
