import axios from 'axios'
import { getToken, clearAuth } from '@/stores/auth'

const http = axios.create({
  baseURL: '/api',
  timeout: 20000
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err?.response?.status
    if (status === 401) {
      clearAuth()
      // 让路由守卫把用户送回登录页
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default http