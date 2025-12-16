import { defineStore } from 'pinia'
import { notificationAPI } from '../api'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
    pollingInterval: null
  }),

  getters: {
    unreadNotifications: (state) => {
      return state.notifications.filter(n => !n.is_read)
    },

    hasUnread: (state) => {
      return state.unreadCount > 0
    }
  },

  actions: {
    async fetchNotifications(unreadOnly = false) {
      this.loading = true
      try {
        const params = unreadOnly ? { unread_only: true } : {}
        const data = await notificationAPI.getList(params)
        // 確保 notifications 始終是數組
        this.notifications = Array.isArray(data) ? data : []
        this.unreadCount = this.notifications.filter(n => !n.is_read).length
        return data
      } catch (error) {
        console.error('Failed to fetch notifications:', error)
        // 發生錯誤時，確保 notifications 是空數組
        this.notifications = []
        this.unreadCount = 0
        // 不要 throw error，避免中斷應用
      } finally {
        this.loading = false
      }
    },

    async markAsRead(notificationId) {
      try {
        await notificationAPI.markAsRead(notificationId)

        // Update local state
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification) {
          notification.is_read = true
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }

        return true
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
        throw error
      }
    },

    async markAllAsRead() {
      try {
        // Mark all unread notifications as read
        const unreadNotifications = this.notifications.filter(n => !n.is_read)

        await Promise.all(
          unreadNotifications.map(n => notificationAPI.markAsRead(n.id))
        )

        // Update local state
        this.notifications.forEach(n => {
          n.is_read = true
        })
        this.unreadCount = 0

        return true
      } catch (error) {
        console.error('Failed to mark all as read:', error)
        throw error
      }
    },

    startPolling(intervalMs = 30000) {
      // Poll for new notifications every 30 seconds
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
      }

      this.pollingInterval = setInterval(() => {
        this.fetchNotifications()
      }, intervalMs)
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },

    clearNotifications() {
      this.notifications = []
      this.unreadCount = 0
      this.stopPolling()
    }
  }
})
