import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/test',
    name: 'SimpleTest',
    component: () => import('../views/SimpleTest.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home/index.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/opinions',
    name: 'OpinionList',
    component: () => import('../views/Opinions/List.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/opinions/:id',
    name: 'OpinionDetail',
    component: () => import('../views/Opinions/Detail.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/opinions/create',
    name: 'OpinionCreate',
    component: () => import('../views/Opinions/Create.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile/index.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
})

export default router
