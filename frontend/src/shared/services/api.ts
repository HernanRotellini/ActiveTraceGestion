import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ApiError, type ApiErrorResponse } from '@/shared/types/api'
import { readSession, writeSession, clearSession } from '@/shared/services/session'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token!)
    }
  })
  failedQueue = []
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const session = readSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (!originalRequest) {
      return Promise.reject(error)
    }

    if (error.response?.status === 403) {
      if (window.location.pathname !== '/403') {
        window.location.href = '/403'
      }
      return Promise.reject(new ApiError('Acceso denegado', 403, 'forbidden'))
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      const session = readSession()
      if (!session?.refresh_token) {
        clearSession()
        window.location.href = '/login'
        return Promise.reject(new ApiError('No autorizado', 401, 'unauthorized'))
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(api(originalRequest))
            },
            reject,
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: session.refresh_token },
        )

        const { access_token, refresh_token } = response.data
        writeSession({
          ...session,
          access_token,
          refresh_token,
        })

        processQueue(null, access_token)
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        clearSession()
        window.location.href = '/login'
        return Promise.reject(new ApiError('Sesión expirada', 401, 'session_expired'))
      } finally {
        isRefreshing = false
      }
    }

    if (error.response) {
      const { status, data } = error.response
      const message =
        data?.detail ?? data?.message ?? 'Error del servidor'
      return Promise.reject(new ApiError(message, status, data?.code))
    }

    if (error.code === 'ERR_NETWORK') {
      return Promise.reject(
        new ApiError('Error de conexión. Verifique su red.', 0, 'network_error'),
      )
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject(
        new ApiError('La solicitud tardó demasiado. Intente nuevamente.', 0, 'timeout'),
      )
    }

    return Promise.reject(new ApiError('Error inesperado', 0, 'unknown'))
  },
)

export default api
