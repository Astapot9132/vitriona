<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

type AdminUser = {
  id: number
  name: string | null
  email: string
  showcases_count: number
  is_banned: boolean
}

type AdminUsersResponse = {
  users?: AdminUser[]
}

type RedirectResponse = {
  redirect?: string
}

const router = useRouter()
const auth = useAuthStore()
const query = ref('')
const users = ref<AdminUser[]>([])

const filteredUsers = computed<AdminUser[]>(() => {
  if (!query.value) return users.value
  const lower = query.value.toLowerCase()
  return users.value.filter((item) => item.name?.toLowerCase().includes(lower) || item.email?.toLowerCase().includes(lower))
})

async function load(): Promise<void> {
  const { data } = await api.get<AdminUsersResponse>('/admin/users')
  users.value = data.users || []
}

async function toggleBan(user: AdminUser): Promise<void> {
  await api.post(`/admin/users/${user.id}/${user.is_banned ? 'unban' : 'ban'}`)
  await load()
}

async function impersonate(user: AdminUser): Promise<void> {
  const { data } = await api.post<RedirectResponse>(`/admin/users/${user.id}/impersonate`)
  await auth.bootstrap(true)
  if (data.redirect) {
    await router.push(data.redirect)
  }
}

onMounted(load)
</script>

<template>
  <AppLayout role="admin">
    <div class="space-y-4 p-6">
      <h1 class="text-2xl font-semibold tracking-tight">Пользователи</h1>
      <input v-model="query" class="input-base max-w-sm" placeholder="Поиск по имени или email" />

      <div class="overflow-hidden rounded-lg border border-border">
        <table class="w-full text-sm">
          <thead class="bg-muted/50">
            <tr class="border-b border-border">
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Имя</th>
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Email</th>
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Витрины</th>
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Статус</th>
              <th class="px-4 py-3"></th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id" class="border-b border-border last:border-0">
              <td class="px-4 py-3 font-medium">{{ user.name || '—' }}</td>
              <td class="px-4 py-3 text-muted-foreground">{{ user.email }}</td>
              <td class="px-4 py-3 text-muted-foreground">{{ user.showcases_count }}</td>
              <td class="px-4 py-3">
                <span :class="user.is_banned ? 'font-medium text-destructive' : 'font-medium text-green-600'">
                  {{ user.is_banned ? 'Бан' : 'Активен' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <button type="button" class="btn-outline" @click="toggleBan(user)">
                  {{ user.is_banned ? 'Снять бан' : 'Забанить' }}
                </button>
              </td>
              <td class="px-4 py-3">
                <button type="button" class="btn-outline" @click="impersonate(user)">Войти в кабинет</button>
              </td>
            </tr>
            <tr v-if="!filteredUsers.length">
              <td colspan="6" class="px-4 py-8 text-center text-muted-foreground">Нет пользователей</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>
