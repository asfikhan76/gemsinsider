const API = ''

function getToken() {
  try {
    return JSON.parse(window.localStorage.getItem('gems-token')) ?? null
  } catch {
    return null
  }
}

export function setToken(token) {
  window.localStorage.setItem('gems-token', JSON.stringify(token))
}

export function clearToken() {
  window.localStorage.removeItem('gems-token')
}

async function apiRequest(url, method, body = null) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const options = { method, headers }
  if (body) options.body = JSON.stringify(body)

  try {
    const response = await fetch(`${API}${url}`, options)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || 'Request failed')
    }
    return data
  } catch (error) {
    console.error('API Error:', error.message)
    throw error
  }
}

export const authService = {
  register: (email, password, name) => apiRequest('/api/auth/register', 'POST', { email, password, name }),
  login: (email, password) => apiRequest('/api/auth/login', 'POST', { email, password }),
  me: () => apiRequest('/api/auth/me', 'GET'),
  logout: () => apiRequest('/api/auth/logout', 'POST'),
  updateProfile: (name) => apiRequest('/api/auth/profile', 'PUT', { name }),
}

export const orderService = {
  getAll: () => apiRequest('/api/orders', 'GET'),
  create: (items) => apiRequest('/api/orders', 'POST', { items }),
  updateStatus: (id, status) => apiRequest(`/api/orders/${id}`, 'PUT', { status }),
  remove: (id) => apiRequest(`/api/orders/${id}`, 'DELETE'),
}

export const contactService = {
  submit: (data) => apiRequest('/api/contact', 'POST', data),
}

export function getUserFromToken(token) {
  if (!token) return null
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const decoded = JSON.parse(atob(base64))
    return { uid: decoded.uid, email: decoded.email, name: decoded.name, role: decoded.role }
  } catch {
    return null
  }
}

export function checkAuth() {
  const token = getToken()
  return getUserFromToken(token)
}
