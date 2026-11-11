// All communication with the FastAPI backend lives in this one file.
// Production: set VITE_API_URL (e.g. https://your-api.onrender.com).
// Development: leave it empty; Vite proxies /api to the local backend.
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export const apiConfigured = !import.meta.env.PROD || Boolean(import.meta.env.VITE_API_URL)

function errorMessage(body, status) {
  if (body && typeof body.detail === 'string') return body.detail
  return `Request failed (HTTP ${status}).`
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, options)
  } catch {
    throw new Error('Cannot reach the server. Check your connection and the API URL setting.')
  }
  if (response.status === 204) return null
  let body = null
  try {
    body = await response.json()
  } catch {
    /* non-JSON response */
  }
  if (!response.ok) throw new Error(errorMessage(body, response.status))
  return body
}

export const getHealth = () => request('/api/health')
export const getStats = () => request('/api/stats')
export const getModelInfo = () => request('/api/model')
export const getDocument = (id) => request(`/api/documents/${id}`)
export const deleteDocument = (id) => request(`/api/documents/${id}`, { method: 'DELETE' })

export function listDocuments({ search = '', category = '', page = 1, pageSize = 15 } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize })
  if (search) params.set('search', search)
  if (category) params.set('category', category)
  return request(`/api/documents?${params}`)
}

// Uses XMLHttpRequest because fetch() cannot report upload progress.
export function uploadDocuments(files, onProgress) {
  return new Promise((resolve, reject) => {
    const form = new FormData()
    files.forEach((file) => form.append('files', file))
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE}/api/documents/upload`)
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress?.(Math.round((e.loaded / e.total) * 100))
    }
    xhr.onerror = () => reject(new Error('Cannot reach the server. Check your connection and the API URL setting.'))
    xhr.onload = () => {
      let body = null
      try {
        body = JSON.parse(xhr.responseText)
      } catch {
        /* ignore */
      }
      if (xhr.status >= 200 && xhr.status < 300) resolve(body)
      else reject(new Error(errorMessage(body, xhr.status)))
    }
    xhr.send(form)
  })
}
