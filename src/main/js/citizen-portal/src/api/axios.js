import axios from 'axios'
import { Capacitor } from '@capacitor/core'

// 在移動應用中使用 WSL2 IP，在網頁中使用 Vite 代理
const getBaseURL = () => {
  if (Capacitor.isNativePlatform()) {
    const platform = Capacitor.getPlatform()

    // Android 平台：優先使用 10.0.2.2（模擬器透過 SSH 隧道）
    if (platform === 'android') {
      // 開發階段：使用模擬器 + SSH 隧道
      // 需要先在主機上執行：ssh -L 8443:140.123.105.199:8443 se_city@140.123.105.199
      return 'https://10.0.2.2:8443/'

      // 真實裝置部署時，改用下面這行：
      // return 'https://140.123.105.199:8443/'
    }

    // iOS 或其他平台：直接訪問遠端伺服器
    return 'https://140.123.105.199:8443/'
  }
  // 網頁瀏覽器：使用 Vite 代理（避免 CORS 和證書問題）
  // Vite dev server 會將 /api/* 請求代理到 https://140.123.105.199:8443/*
  return '/api'
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
