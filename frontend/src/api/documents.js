import http from './http'

// GET /documents -> [{id,name,type,status,created_at}]
export function listDocuments() {
  return http.get('/documents')
}

// POST /documents/upload (form-data: file)
export function uploadDocument(file) {
  const fd = new FormData()
  fd.append('file', file)
  return http.post('/documents/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// POST /documents/{id}/process
export function processDocument(id) {
  return http.post(`/documents/${id}/process`)
}

// DELETE /documents/{id}
export function deleteDocument(id) {
  return http.delete(`/documents/${id}`)
}