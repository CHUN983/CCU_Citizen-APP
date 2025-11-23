import { defineStore } from 'pinia'
import { adminDashboardAPI } from '../api'

export const useDashBoardStore = defineStore('dashboard', {
  state: () => ({
    stats: null
  }),

    actions: {
    // 獲取統計數據
        async fetchStats() {
            try {
                const data = await adminDashboardAPI.getStats()
                this.stats = data
                return data
            } catch (error) {
                throw error
            }
        }
    }
})