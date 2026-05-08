import { http } from './inventario'
import { refresh } from './inventario' // tu endpoint
import { useAuthStore } from '@/stores/authStore'
import router from '@/router/router'

let isRefreshing = false
let failedQueue: any[] = []

console.log("INTERCEPTOR ACTIVO")

function processQueue(error: any, token: any = null) {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 🔴 Ignorar si no es 401
    if (error.response?.status !== 401) {
      return Promise.reject(error)
    }

    // 🔴 NO intentar refresh en estos endpoints
    if (
      originalRequest.url?.includes('/auth/verify') ||
      originalRequest.url?.includes('/auth/refresh') ||
      originalRequest.url?.includes('/auth/login')
    ) {
      return Promise.reject(error)
    }

    // 🔴 Si no hay cookies → no tiene sentido refrescar
    if (!document.cookie.includes('refresh_token')) {
      return Promise.reject(error)
    }

    // 🔴 Evitar loop infinito
    if (originalRequest._retry) {
      const auth = useAuthStore()
      auth.usuario = null
      auth.isAuthenticated = false
      router.push('/')
      return Promise.reject(error)
    }

    originalRequest._retry = true

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then(() => http(originalRequest))
        .catch(err => Promise.reject(err))
    }

    isRefreshing = true

    try {
      await refresh()

      processQueue(null)

      return http(originalRequest)

    } catch (err) {
      processQueue(err, null)

      const auth = useAuthStore()
      auth.usuario = null
      auth.isAuthenticated = false

      router.push('/')

      return Promise.reject(err)
    } finally {
      isRefreshing = false
    }
  }
)