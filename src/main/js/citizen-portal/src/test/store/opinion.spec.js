import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useOpinionStore } from '../../store/opinion'

// Mock API
vi.mock('../../api', () => ({
  opinionAPI: {
    getList: vi.fn(() => Promise.resolve({ items: [], total: 0 })),
    getById: vi.fn(() => Promise.resolve({ id: 1, title: 'Test Opinion' })),
    getBookmarkStatus: vi.fn(() => Promise.resolve({ is_collected: false })),
    getVoteStatus: vi.fn(() => Promise.resolve({ vote_type: null })),
    getMyOpinions: vi.fn(() => Promise.resolve({ items: [], total: 0 })),
    vote: vi.fn(() => Promise.resolve({})),
    bookmark: vi.fn(() => Promise.resolve({})),
    unbookmark: vi.fn(() => Promise.resolve({}))
  },
  categoryAPI: {
    getList: vi.fn(() => Promise.resolve({ categories: [] }))
  }
}))

describe('Opinion Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useOpinionStore()
  })

  describe('State Initialization', () => {
    it('should initialize with default state', () => {
      expect(store.opinions).toEqual([])
      expect(store.currentOpinion).toBeNull()
      expect(store.total).toBe(0)
      expect(store.loading).toBe(false)
      expect(store.myOpinions).toEqual([])
      expect(store.myOpinionsTotal).toBe(0)
    })
  })

  describe('fetchOpinions', () => {
    it('should set loading state correctly', async () => {
      expect(store.loading).toBe(false)

      const promise = store.fetchOpinions()
      expect(store.loading).toBe(true)

      await promise
      expect(store.loading).toBe(false)
    })

    it('should fetch opinions successfully', async () => {
      const { opinionAPI } = await import('../../api')
      const mockData = {
        items: [
          { id: 1, title: 'Opinion 1' },
          { id: 2, title: 'Opinion 2' }
        ],
        total: 2
      }
      opinionAPI.getList.mockResolvedValueOnce(mockData)

      await store.fetchOpinions()

      expect(store.opinions).toEqual(mockData.items)
      expect(store.total).toBe(2)
    })
  })

  describe('fetchMyOpinions', () => {
    it('should fetch user opinions with status filter', async () => {
      const { opinionAPI } = await import('../../api')
      const mockData = {
        items: [{ id: 1, title: 'My Opinion', status: 'approved' }],
        total: 1
      }
      opinionAPI.getMyOpinions.mockResolvedValueOnce(mockData)

      await store.fetchMyOpinions(1, 10, 'approved')

      expect(store.myOpinions).toEqual(mockData.items)
      expect(store.myOpinionsTotal).toBe(1)
      expect(opinionAPI.getMyOpinions).toHaveBeenCalledWith({
        page: 1,
        page_size: 10,
        status: 'approved'
      })
    })
  })

  describe('Vote Toggle', () => {
    it('should update bookmark status', async () => {
      const { opinionAPI } = await import('../../api')
      store.currentOpinion = { id: 1, title: 'Test', is_bookmarked: false }

      await store.bookmarkOpinion(1)

      expect(store.currentOpinion.is_bookmarked).toBe(true)
      expect(opinionAPI.bookmark).toHaveBeenCalledWith(1)
    })

    it('should remove bookmark status', async () => {
      const { opinionAPI } = await import('../../api')
      store.currentOpinion = { id: 1, title: 'Test', is_bookmarked: true }

      await store.unbookmarkOpinion(1)

      expect(store.currentOpinion.is_bookmarked).toBe(false)
      expect(opinionAPI.unbookmark).toHaveBeenCalledWith(1)
    })
  })

  describe('fetchOpinionById', () => {
    it('should fetch opinion with vote and bookmark status', async () => {
      const { opinionAPI } = await import('../../api')

      opinionAPI.getById.mockResolvedValueOnce({
        id: 1,
        title: 'Test Opinion',
        upvotes: 5,
        downvotes: 2
      })
      opinionAPI.getBookmarkStatus.mockResolvedValueOnce({ is_collected: true })
      opinionAPI.getVoteStatus.mockResolvedValueOnce({ vote_type: 'like' })

      await store.fetchOpinionById(1)

      expect(store.currentOpinion).toEqual({
        id: 1,
        title: 'Test Opinion',
        upvotes: 5,
        downvotes: 2,
        is_bookmarked: true,
        user_vote: 'like'
      })
    })
  })
})
