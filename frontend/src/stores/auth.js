import { defineStore } from 'pinia'

import { api } from '@/lib/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAdmin: false,
    impersonating: false,
    csrfToken: null,
    bootstrapped: false,
  }),
  actions: {
    async bootstrap(force = false) {
      if (this.bootstrapped && !force) {
        return
      }
      try {
        const { data } = await api.get('/meta/bootstrap')
        const auth = data.auth || {}
        this.user = auth.user || null
        this.isAdmin = Boolean(auth.is_admin)
        this.impersonating = Boolean(auth.impersonating)
        this.csrfToken = auth.csrf_token || null
      } catch {
        this.user = null
        this.isAdmin = false
        this.impersonating = false
        this.csrfToken = null
      } finally {
        this.bootstrapped = true
      }
    },
    async fetchCsrf(force = false) {
      if (this.csrfToken && !force) {
        return this.csrfToken
      }
      const { data } = await api.get('/auth/csrf')
      this.csrfToken = data.csrf_token
      return this.csrfToken
    },
    clearAuth() {
      this.user = null
      this.isAdmin = false
      this.impersonating = false
      this.csrfToken = null
      this.bootstrapped = true
    },
  },
})
