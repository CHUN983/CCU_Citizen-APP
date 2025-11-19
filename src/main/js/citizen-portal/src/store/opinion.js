import { defineStore } from 'pinia'
import { opinionAPI, categoryAPI } from '../api'

export const useOpinionStore = defineStore('opinion', {
  state: () => ({
    opinions: [],
    currentOpinion: null,
    categories: [],
    total: 0,
    loading: false
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
          const [opinionData, voteStats] = await Promise.all([
            opinionAPI.getById(id),
            opinionAPI.getVotes(id)
          ])

          // 把 like/support 數量合併進 currentOpinion
          this.currentOpinion = {
            ...opinionData,
            upvotes: voteStats.like_count ?? 0,
            downvotes: voteStats.support_count ?? 0
          }

          return this.currentOpinion
      } catch (error) {
        throw error
      } finally {
        this.loading = false
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
        return data
      } catch (error) {
        throw error
      }
    },

    async unbookmarkOpinion(id) {
      try {
        const data = await opinionAPI.unbookmark(id)
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
