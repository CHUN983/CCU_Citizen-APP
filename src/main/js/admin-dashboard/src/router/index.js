import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login/index.vue'),
    meta: { title: '登入' }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard/index.vue'),
    meta: { title: '儀表板', requireAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History/index.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/opinions',
    name: 'Opinions',
    component: () => import('../views/Opinions/index.vue'),
    meta: { title: '意見管理', requireAuth: true }
  },
  {
    path: '/opinions/:id',
    name: 'OpinionDetail',
    component: () => import('../views/Opinions/Detail.vue'),
    meta: { title: '意見詳情', requireAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守衛
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 設置頁面標題
  document.title = to.meta.title ? `${to.meta.title} - 市民參與管理後台` : '市民參與管理後台'

  // 檢查是否需要登入
  if (to.meta.requireAuth) {
    if (userStore.isLogin) {
      next()
    } else {
      next('/login')
    }
  } else {
    // 如果已登入，訪問登入頁時自動跳轉到首頁
    if (to.path === '/login' && userStore.isLogin) {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
