import { defineStore } from 'pinia'
import { opinionAPI, categoryAPI } from '../api'

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
      this.loading = true
      try {
          const [voteStats, opinionData, collectStatus] = await Promise.all([
            opinionAPI.getVotes(id),
            opinionAPI.getById(id),
            opinionAPI.getBookmarkStatus(id)
          ])

          // 把 like/support 數量合併進 currentOpinion
          this.currentOpinion = {
            ...opinionData,
            upvotes: voteStats.like_count ?? 0,
            downvotes: voteStats.support_count ?? 0,
            is_bookmarked: collectStatus.is_collected ?? false
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
        this.bookmarkedOpinions = data.items || []
        this.bookmarkedTotal = data.total || 0
        return data
      } catch (error) {
        throw error
      } finally {
        this.bookmarkedLoading = false
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
