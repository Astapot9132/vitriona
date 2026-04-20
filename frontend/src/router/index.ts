import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'
import AdminAdminsView from '@/views/admin/AdminAdminsView.vue'
import AdminDashboardView from '@/views/admin/AdminDashboardView.vue'
import AdminLoginView from '@/views/admin/AdminLoginView.vue'
import AdminOffersView from '@/views/admin/AdminOffersView.vue'
import AdminUsersView from '@/views/admin/AdminUsersView.vue'
import ClientDashboardView from '@/views/client/ClientDashboardView.vue'
import ClientLoginView from '@/views/client/ClientLoginView.vue'
import ClientOffersView from '@/views/client/ClientOffersView.vue'
import ClientOnboardingView from '@/views/client/ClientOnboardingView.vue'
import ShowcaseEditView from '@/views/client/ShowcaseEditView.vue'
import ShowcasesView from '@/views/client/ShowcasesView.vue'
import PrototypesView from '@/views/prototypes/PrototypesView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', component: HomeView },
  { path: '/client', component: ClientLoginView, meta: { guest: 'client' } },
  { path: '/onboarding', component: ClientOnboardingView, meta: { auth: true } },
  { path: '/dashboard', component: ClientDashboardView, meta: { auth: true, onboarded: true } },
  { path: '/offers', component: ClientOffersView, meta: { auth: true, onboarded: true } },
  { path: '/showcases', component: ShowcasesView, meta: { auth: true, onboarded: true } },
  { path: '/showcases/:id/edit', component: ShowcaseEditView, meta: { auth: true, onboarded: true } },
  { path: '/admin', component: AdminLoginView, meta: { guest: 'admin' } },
  { path: '/admin/dashboard', component: AdminDashboardView, meta: { admin: true } },
  { path: '/admin/offers', component: AdminOffersView, meta: { admin: true } },
  { path: '/admin/users', component: AdminUsersView, meta: { admin: true } },
  { path: '/admin/admins', component: AdminAdminsView, meta: { admin: true } },
  { path: '/prototypes', component: PrototypesView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.bootstrap()

  if (to.meta.admin) {
    if (!auth.user || !auth.isAdmin) {
      return '/admin'
    }
    return true
  }

  if (to.meta.auth) {
    if (!auth.user) {
      return '/client'
    }
    if (to.meta.onboarded && !auth.user.is_onboarded) {
      return '/onboarding'
    }
    if (to.path === '/onboarding' && auth.user.is_onboarded) {
      return '/dashboard'
    }
    return true
  }

  if (to.meta.guest === 'client' && auth.user) {
    return auth.user.is_onboarded ? '/dashboard' : '/onboarding'
  }

  if (to.meta.guest === 'admin' && auth.user && auth.isAdmin) {
    return '/admin/dashboard'
  }

  return true
})

export default router
