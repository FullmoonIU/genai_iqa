import http from './http'

// GET /history -> [{id, question, answer, created_at}]
export function listHistory() {
  return http.get('/history')
}