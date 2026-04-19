<script setup>
import { onMounted, ref } from 'vue'

import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/lib/api'

const admins = ref([])

onMounted(async () => {
  const { data } = await api.get('/admin/admins')
  admins.value = data.admins || []
})
</script>

<template>
  <AppLayout role="admin">
    <div class="space-y-4 p-6">
      <h1 class="text-2xl font-semibold tracking-tight">Админы</h1>

      <div class="overflow-hidden rounded-lg border border-border">
        <table class="w-full text-sm">
          <thead class="bg-muted/40">
            <tr class="border-b border-border">
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Имя</th>
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Email</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in admins" :key="item.email" class="border-b border-border last:border-0">
              <td class="px-4 py-3 font-medium">{{ item.name || '—' }}</td>
              <td class="px-4 py-3 text-muted-foreground">{{ item.email }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>
