import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'

let isRefreshing = false
let pendingRequests = []
let isConfigured = false

export function setupApi(pinia) {
  if (isConfigured) {
    return
  }
  isConfigured = true

  const authStore = useAuthStore(pinia)

  api.interceptors.request.use(async (config) => {
    const method = config.method ? config.method.toLowerCase() : null
    const needsCsrf = method && !['get', 'head', 'options'].includes(method)

    if (needsCsrf) {
      if (!authStore.csrfToken) {
        await authStore.fetchCsrf()
      }
      config.headers = config.headers || {}
      config.headers['X-CSRF-Token'] = authStore.csrfToken
    }

    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const { config, response } = error
      const status = response ? response.status : null
      if (status !== 401 || (config && config._retry) || (config && config._skipRefresh)) {
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
        await api.post('/auth/refresh', null, { _skipRefresh: true })
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
