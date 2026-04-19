<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  role: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    default: '',
  },
})

const auth = useAuthStore()
const router = useRouter()

const clientNav = [
  { href: '/dashboard', label: 'Главная' },
  { href: '/offers', label: 'Офферы' },
  { href: '/showcases', label: 'Витрины' },
]

const adminNav = [
  { href: '/admin/dashboard', label: 'Главная' },
  { href: '/admin/offers', label: 'Офферы' },
  { href: '/admin/admins', label: 'Админы' },
  { href: '/admin/users', label: 'Пользователи' },
]

const nav = computed(() => (props.role === 'admin' ? adminNav : clientNav))

async function logout() {
  const endpoint = props.role === 'admin' ? '/auth/admin/logout' : '/auth/client/logout'
  const { data } = await api.post(endpoint)
  auth.clearAuth()
  router.push(data.redirect)
}

async function leaveImpersonation() {
  const { data } = await api.post('/admin/impersonate/leave')
  await auth.bootstrap(true)
  router.push(data.redirect)
}
</script>

<template>
  <div class="min-h-screen bg-background text-foreground flex">
    <aside class="fixed inset-y-0 left-0 z-20 flex w-56 shrink-0 flex-col border-r border-border bg-background">
      <div class="flex items-center gap-3 border-b border-border px-4 py-4">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
          V
        </div>
        <span class="text-sm font-semibold">{{ role === 'admin' ? 'Vitriona Admin' : 'Vitriona' }}</span>
      </div>

      <nav class="flex-1 space-y-1 px-2 py-3">
        <RouterLink
          v-for="item in nav"
          :key="item.href"
          :to="item.href"
          class="block rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          active-class="bg-primary font-medium text-primary-foreground hover:bg-primary hover:text-primary-foreground"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="border-t border-border px-2 py-3">
        <div v-if="auth.user?.email" class="mb-1 truncate px-3 py-1.5 text-xs text-muted-foreground">
          {{ auth.user.email }}
        </div>
        <button type="button" class="btn-ghost w-full justify-start" @click="logout">
          Выйти
        </button>
      </div>
    </aside>

    <div class="ml-56 min-w-0 flex-1">
      <div
        v-if="auth.impersonating && role !== 'admin'"
        class="flex items-center justify-between bg-amber-500 px-4 py-2 text-sm text-white"
      >
        <span>Вы вошли как {{ auth.user?.email }}</span>
        <button type="button" class="font-medium underline" @click="leaveImpersonation">
          Вернуться в админку
        </button>
      </div>

      <slot />
    </div>
  </div>
</template>
