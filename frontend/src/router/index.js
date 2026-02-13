import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Documents from '@/views/Documents.vue'
import QA from '@/views/QA.vue'
import History from '@/views/History.vue'
import { getToken } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/register', component: Register },

    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', redirect: '/qa' },
        { path: 'documents', component: Documents },
        { path: 'qa', component: QA },
        { path: 'history', component: History }
      ]
    },

    { path: '/:pathMatch(.*)*', redirect: '/qa' }
  ]
})

// 简单前端路由守卫：没 token 就去登录
router.beforeEach((to) => {
  const publicPaths = ['/login', '/register']
  if (publicPaths.includes(to.path)) return true
  const token = getToken()
  if (!token) return '/login'
  return true
})

export default router