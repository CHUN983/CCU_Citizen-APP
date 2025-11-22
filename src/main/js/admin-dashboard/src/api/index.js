import request from './axios'

// 認證 API
export const authAPI = {
  // 登入
  login(data) {
    return request.post('/auth/login', data)
  },
  // 取得當前用戶
  getCurrentUser() {
    return request.get('/auth/me')
  }
}

// 意見 API
export const opinionAPI = {
  // 獲取意見列表
  getOpinions(params) {
    return request.get('/opinions', { params })
  },
  // 獲取意見詳情
  getOpinionDetail(id) {
    return request.get(`/opinions/${id}`)
  },
  // 核准意見
  approveOpinion(id) {
    return request.post(`/admin/opinions/${id}/approve`)
  },
  // 拒絕意見
  rejectOpinion(id, reason) {
    return request.post(`/admin/opinions/${id}/reject`, { reason })
  },
  // 合併意見
  mergeOpinion(id, targetId) {
    return request.post(`/admin/opinions/${id}/merge`, { target_id: targetId })
  },
  // 更新分類
  updateCategory(id, categoryId) {
    return request.put(`/admin/opinions/${id}/category`, { category_id: categoryId })
  }
}

// 留言 API
export const commentAPI = {
  // 刪除留言
  deleteComment(id) {
    return request.delete(`/admin/comments/${id}`)
  }
}

// 通知 API
export const notificationAPI = {
  // 獲取通知列表
  getNotifications(params) {
    return request.get('/notifications', { params })
  }
}
