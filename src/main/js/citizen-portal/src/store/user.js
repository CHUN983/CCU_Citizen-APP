import { defineStore } from 'pinia'
import { authAPI } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    username: (state) => state.user?.username || '',
    userId: (state) => state.user?.user_id || null,
    role: (state) => state.user?.role || 'citizen'
  },

  actions: {
    async login(credentials) {
      try {
        const data = await authAPI.login(credentials)
        this.token = data.access_token
        this.user = data.user

        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))

        return data
      } catch (error) {
        throw error
      }
    },

    async register(userData) {
      try {
        const data = await authAPI.register(userData)
        // Auto login after registration
        this.token = data.access_token
        this.user = data.user

        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))

        return data
      } catch (error) {
        throw error
      }
    },

    async getProfile() {
      try {
        const data = await authAPI.getProfile()
        this.user = data
        localStorage.setItem('user', JSON.stringify(data))
        return data
      } catch (error) {
        throw error
      }
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
