import http from './http'

// POST /qa/ask { question, top_k } -> { answer, citations: [...] }
export function askQuestion(payload) {
  return http.post('/qa/ask', payload)
}