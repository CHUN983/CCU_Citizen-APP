import { defineStore } from 'pinia'
import { authAPI } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),

  getters: {
    isLogin: (state) => !!state.token
  },

  actions: {
    // 登入
    async login(loginData) {
      try {
        const data = await authAPI.login(loginData)
        this.token = data.access_token
        localStorage.setItem('token', data.access_token)
        return data
      } catch (error) {
        throw error
      }
    },

    // 獲取用戶資訊
    async getUserInfo() {
      try {
        const data = await authAPI.getCurrentUser()
        this.userInfo = data
        return data
      } catch (error) {
        throw error
      }
    },

    // 登出
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})
