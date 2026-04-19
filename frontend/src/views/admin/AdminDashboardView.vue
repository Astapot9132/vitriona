<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <AppLayout role="admin">
    <div class="space-y-6 p-6">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">Админка</h1>
        <p class="mt-1 text-sm text-muted-foreground">{{ auth.user?.email }}</p>
      </div>

      <div class="grid gap-4 md:grid-cols-3">
        <RouterLink class="card-base block p-5 hover:bg-muted/30" to="/admin/offers">
          <div class="text-sm font-medium">Офферы</div>
          <div class="mt-1 text-xs text-muted-foreground">Просмотр и синхронизация</div>
        </RouterLink>
        <RouterLink class="card-base block p-5 hover:bg-muted/30" to="/admin/users">
          <div class="text-sm font-medium">Пользователи</div>
          <div class="mt-1 text-xs text-muted-foreground">Бан и impersonate</div>
        </RouterLink>
        <RouterLink class="card-base block p-5 hover:bg-muted/30" to="/admin/admins">
          <div class="text-sm font-medium">Админы</div>
          <div class="mt-1 text-xs text-muted-foreground">Список разрешённых email</div>
        </RouterLink>
      </div>
    </div>
  </AppLayout>
</template>
