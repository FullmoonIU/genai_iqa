import http from './http'

// 你 FastAPI 可以按这个接口实现：
// POST /auth/login { username, password } -> { token, user }
// POST /auth/register { username, password } -> { ok: true }
export function loginApi(payload) {
  return http.post('/auth/login', payload)
}

export function registerApi(payload) {
  return http.post('/auth/register', payload)
}