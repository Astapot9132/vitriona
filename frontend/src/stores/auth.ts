import { defineStore } from 'pinia'

import { api } from '@/lib/api'

export interface AuthUser {
  id: number
  name: string
  email: string
  affise_country: string | null
  affise_id: number | null
  is_onboarded: boolean
}

interface BootstrapAuthPayload {
  user: AuthUser | null
  is_admin: boolean
  impersonating: boolean
  csrf_token: string | null
}

interface BootstrapResponse {
  auth?: Partial<BootstrapAuthPayload>
}

interface CsrfResponse {
  csrf_token: string | null
}

interface AuthState {
  user: AuthUser | null
  isAdmin: boolean
  impersonating: boolean
  csrfToken: string | null
  bootstrapped: boolean
}

function getDefaultState(): AuthState {
  return {
    user: null,
    isAdmin: false,
    impersonating: false,
    csrfToken: null,
    bootstrapped: false,
  }
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => getDefaultState(),
  actions: {
    async bootstrap(force = false): Promise<void> {
      if (this.bootstrapped && !force) {
        return
      }
      try {
        const { data } = await api.get<BootstrapResponse>('/meta/bootstrap')
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
    async fetchCsrf(force = false): Promise<string | null> {
      if (this.csrfToken && !force) {
        return this.csrfToken
      }
      const { data } = await api.get<CsrfResponse>('/auth/csrf')
      this.csrfToken = data.csrf_token || null
      return this.csrfToken
    },
    clearAuth(): void {
      this.user = null
      this.isAdmin = false
      this.impersonating = false
      this.csrfToken = null
      this.bootstrapped = true
    },
  },
})
