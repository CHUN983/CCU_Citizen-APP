import axios from './axios'

// Auth APIs
export const authAPI = {
  login: (data) => axios.post('/auth/login', data),
  register: (data) => axios.post('/auth/register', data),
  getProfile: () => axios.get('/auth/me')
}

// Opinion APIs
export const opinionAPI = {
  getList: (params) => axios.get('/opinions', { params }),
  getById: (id) => axios.get(`/opinions/${id}`),
  create: (data) => axios.post('/opinions', data),
  update: (id, data) => axios.put(`/opinions/${id}`, data),
  delete: (id) => axios.delete(`/opinions/${id}`),
  vote: (id, voteType) => axios.post(`/opinions/${id}/vote`, { vote_type: voteType }),
  getVotes: (id) => axios.get(`/opinions/${id}/votes`),
  bookmark: (id) => axios.post(`/opinions/${id}/collect`),
  getBookmarkStatus: (id) => axios.get(`/opinions/${id}/collect`),
  getBookmarked: (params) => axios.get('/opinions/collect', { params }),
  unbookmark: (id) => axios.delete(`/opinions/${id}/collect`)
}

// Comment APIs
export const commentAPI = {
  getList: (opinionId, params) => axios.get(`/opinions/${opinionId}/comments`, { params }),
  create: (opinionId, data) => axios.post(`/opinions/${opinionId}/comments`, data),
  update: (opinionId, commentId, data) => axios.put(`/opinions/${opinionId}/comments/${commentId}`, data),
  delete: (opinionId, commentId) => axios.delete(`/opinions/${opinionId}/comments/${commentId}`)
}

// Category APIs
export const categoryAPI = {
  getList: () => axios.get('/categories')
}

// Notification APIs
export const notificationAPI = {
  getList: (params) => axios.get('/notifications', { params }),
  markAsRead: (id) => axios.post(`/notifications/${id}/read`)
}


//Media APIs
export const mediaAPI = {
  // 單檔上傳
  upload: async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const res = await axios.post('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res
  },

  // 多檔上傳
  uploadMultiple: async (files) => {
    const formData = new FormData()
    files.forEach(f => {
      formData.append('files', f)  // 後端的 File(...) key
    })

    const res = await axios.post('/media/upload-multiple', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    console.log('mediaAPI.uploadMultiple response:', res)
    return res
  }
}