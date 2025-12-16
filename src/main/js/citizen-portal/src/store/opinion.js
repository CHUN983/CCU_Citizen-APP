import { defineStore } from 'pinia'
import { opinionAPI, categoryAPI } from '../api'
import { useUserStore } from './user'
import { processOpinionMediaUrls, processOpinionsMediaUrls } from '../utils/mediaUrl'

const userStore = useUserStore()

export const useOpinionStore = defineStore('opinion', {
  state: () => ({
    opinions: [],
    currentOpinion: null,
    categories: [],
    total: 0,
    loading: false,

    bookmarkedOpinions: [],
    bookmarkedTotal: 0,
    bookmarkedLoading: false
  }),

  actions: {
    async fetchOpinions(params = {}) {
      this.loading = true
      try {
        const data = await opinionAPI.getList(params)
        this.opinions = data.items || []
        this.total = data.total || 0

        return data
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchOpinionById(id) {
      console.log(" 阿維?")
      this.loading = true
      try {
          const bookmarkPromise = userStore.isLoggedIn
            ? opinionAPI.getBookmarkStatus(id)
            : Promise.resolve({ is_collected: false })

          const votePromise = userStore.isLoggedIn
            ? opinionAPI.getVoteStatus(id)
            : Promise.resolve({ vote_type: null })

          const [ opinionData, collectStatus, voteStatus ] = await Promise.all([
            opinionAPI.getById(id),
            bookmarkPromise,
            votePromise
          ])

          // 處理媒體 URL（Android/iOS 需要完整 URL）
          console.log("before media url processing:", opinionData)
          const processedOpinion = processOpinionMediaUrls(opinionData)
          console.log("after media url processing:", processedOpinion)

          // 把 like/support 數量和用戶投票狀態合併進 currentOpinion
          this.currentOpinion = {
            ...processedOpinion,
            is_bookmarked: collectStatus.is_collected ?? false,
            user_vote: voteStatus.vote_type // 'like', 'support', or null
          }

          return this.currentOpinion
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchBookmarkedOpinions(page = 1, pageSize = 5) {
      this.bookmarkedLoading = true
      try {
        const params = {
          page,
          page_size: pageSize
        }
        const data = await opinionAPI.getBookmarked(params)
        this.bookmarkedOpinions = processOpinionsMediaUrls(data.items || [])
        this.bookmarkedTotal = data.total || 0
        return data
      } catch (error) {
        throw error
      } finally {
        this.bookmarkedLoading = false
      }
    },

    async fetchMyOpinions(page = 1, pageSize = 10, status = null) {
      this.myOpinionsLoading = true
      try {
        const params = {
          page,
          page_size: pageSize
        }
        if (status) {
          params.status = status
        }
        const data = await opinionAPI.getMyOpinions(params)
        // 處理媒體 URL（Android/iOS 需要完整 URL）
        this.myOpinions = processOpinionsMediaUrls(data.items || [])
        this.myOpinionsTotal = data.total || 0
        return data
      } catch (error) {
        throw error
      } finally {
        this.myOpinionsLoading = false
      }
    },

    async createOpinion(opinionData) {
      try {
        const data = await opinionAPI.create(opinionData)
        return data
      } catch (error) {
        throw error
      }
    },

    async voteOpinion(id, voteType) {
      try {
        const data = await opinionAPI.vote(id, voteType)
        // Update local state
        if (this.currentOpinion && this.currentOpinion.opinion_id === id) {
          await this.fetchOpinionById(id)
        }
        return this.currentOpinion
      } catch (error) {
        throw error
      }
    },

    async bookmarkOpinion(id) {
      try {
        const data = await opinionAPI.bookmark(id)
        if (this.currentOpinion && this.currentOpinion.id === id) {
          this.currentOpinion = {
            ...this.currentOpinion,
            is_bookmarked: true
          }
        }
        return data
      } catch (error) {
        throw error
      }
    },

    async unbookmarkOpinion(id) {
      try {
        const data = await opinionAPI.unbookmark(id)
        if (this.currentOpinion && this.currentOpinion.id === id) {
          this.currentOpinion = {
            ...this.currentOpinion,
            is_bookmarked: false
          }
        }
        return data
      } catch (error) {
        throw error
      }
    },

    async fetchCategories() {
      try {
        const data = await categoryAPI.getList()
        this.categories = data.categories || []
        return data
      } catch (error) {
        throw error
      }
    }
  }
})
