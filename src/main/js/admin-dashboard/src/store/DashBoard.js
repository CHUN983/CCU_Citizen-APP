import { defineStore } from 'pinia'
import { adminDashboardAPI } from '../api'

export const useDashBoardStore = defineStore('dashboard', {
  state: () => ({
    stats: null,
    history: { items: [], total: 0, loading: false },
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
        },
    // 獲取操作歷史
        async fetchHistory(params) {
            this.history.loading = true
            try {
                const data = await adminDashboardAPI.getHistoryList(params)
                this.history.items = data.items || []
                this.history.total = data.total || 0
                return data
            } finally {
                this.history.loading = false
            }
            }
    }
})