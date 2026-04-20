import type { InternalAxiosRequestConfig } from 'axios'
import type { Pinia } from 'pinia'

import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

interface ApiRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
  _skipRefresh?: boolean
}

type PendingRequestResolver = (tokenUpdated: boolean) => void

let isRefreshing = false
let pendingRequests: PendingRequestResolver[] = []
let isConfigured = false

export function setupApi(pinia: Pinia): void {
  if (isConfigured) {
    return
  }
  isConfigured = true

  const authStore = useAuthStore(pinia)

  api.interceptors.request.use(async (config: ApiRequestConfig) => {
    const method = config.method ? config.method.toLowerCase() : null
    const needsCsrf = Boolean(method && !['get', 'head', 'options'].includes(method))

    if (needsCsrf) {
      if (!authStore.csrfToken) {
        await authStore.fetchCsrf()
      }
      config.headers['X-CSRF-Token'] = authStore.csrfToken
    }

    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const config = error.config as ApiRequestConfig | undefined
      const response = error.response
      const status = response ? response.status : null

      if (status !== 401 || (config && config._retry) || (config && config._skipRefresh) || !config) {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingRequests.push((tokenUpdated) => {
            if (tokenUpdated) {
              resolve(api(config))
              return
            }
            reject(error)
          })
        })
      }

      config._retry = true
      isRefreshing = true

      try {
        const refreshConfig: ApiRequestConfig = { _skipRefresh: true } as ApiRequestConfig
        await api.post('/auth/refresh', null, refreshConfig)
        await authStore.bootstrap(true)
        pendingRequests.forEach((cb) => cb(true))
        return api(config)
      } catch (refreshError) {
        pendingRequests.forEach((cb) => cb(false))
        authStore.clearAuth()
        throw refreshError
      } finally {
        pendingRequests = []
        isRefreshing = false
      }
    },
  )
}
