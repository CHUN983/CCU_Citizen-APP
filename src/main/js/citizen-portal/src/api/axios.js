import axios from 'axios'
import { Capacitor } from '@capacitor/core'

// 在移動應用中使用 WSL2 IP，在網頁中使用相對路徑
const getBaseURL = () => {
  if (Capacitor.isNativePlatform()) {
    // Android 模擬器訪問 WSL2 上的後端或是python api開啟的port
    return 'https://10.0.2.2:8000'
  }
  return 'http://140.123.105.199:8080/'
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

export default instance
