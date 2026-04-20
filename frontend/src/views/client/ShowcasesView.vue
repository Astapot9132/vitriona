<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/AppLayout.vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { api } from '@/lib/api'

type Showcase = {
  id: number
  name?: string | null
  platform_main: string
  platform_sub: string | null
  url: string
}

type ShowcasesResponse = {
  showcases?: Showcase[]
}

type ShowcaseActionResponse = {
  message?: string
  redirect?: string
}

const router = useRouter()
const showcases = ref<Showcase[]>([])
const toast = ref('')
const createForm = reactive({ name: '', platform_main: '', platform_sub: '', url: '' })
const saving = ref(false)

async function load(): Promise<void> {
  const { data } = await api.get<ShowcasesResponse>('/showcases')
  showcases.value = data.showcases || []
}

async function createShowcase(): Promise<void> {
  saving.value = true
  try {
    const { data } = await api.post<ShowcaseActionResponse>('/showcases', createForm)
    if (data.redirect) {
      await router.push(data.redirect)
    }
  } finally {
    saving.value = false
  }
}

async function duplicateShowcase(item: Showcase): Promise<void> {
  const { data } = await api.post<ShowcaseActionResponse>(`/showcases/${item.id}/duplicate`)
  toast.value = data.message || ''
  await load()
}

async function deleteShowcase(item: Showcase): Promise<void> {
  if (!window.confirm('Удалить витрину?')) return
  const { data } = await api.delete<ShowcaseActionResponse>(`/showcases/${item.id}`)
  toast.value = data.message || ''
  await load()
}

onMounted(load)
</script>

<template>
  <AppLayout role="client">
    <ToastMessage v-if="toast" :message="toast" @done="toast = ''" />

    <div class="space-y-6 p-6">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold">Список созданных лендингов</h1>
      </div>

      <div class="card-base p-5">
        <div class="mb-4 text-sm font-medium">Создать новую витрину</div>
        <form class="grid gap-3 md:grid-cols-2" @submit.prevent="createShowcase">
          <input v-model="createForm.name" class="input-base" placeholder="Название" required />
          <input v-model="createForm.platform_main" class="input-base" placeholder="Площадка" required />
          <input v-model="createForm.platform_sub" class="input-base" placeholder="ID площадки" />
          <input v-model="createForm.url" class="input-base" placeholder="example.sync.link" required />
          <div class="md:col-span-2">
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>

      <div class="overflow-hidden rounded-lg border border-border">
        <table class="w-full text-sm">
          <thead class="bg-muted/40">
            <tr class="border-b border-border">
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">ID</th>
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Площадка</th>
              <th class="px-4 py-3 text-left font-medium text-muted-foreground">Адрес страницы</th>
              <th class="px-4 py-3 text-right font-medium text-muted-foreground"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in showcases" :key="item.id" class="border-b border-border last:border-0 hover:bg-muted/30">
              <td class="px-4 py-3 text-muted-foreground">{{ item.id }}</td>
              <td class="px-4 py-3">
                <div class="font-medium">{{ item.platform_main }}</div>
                <div v-if="item.platform_sub" class="text-xs text-muted-foreground">{{ item.platform_sub }}</div>
              </td>
              <td class="px-4 py-3">
                <a class="text-primary hover:underline" :href="`https://${item.url}`" target="_blank" rel="noreferrer">
                  {{ item.url }}
                </a>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-2">
                  <RouterLink class="btn-outline" :to="`/showcases/${item.id}/edit`">Редактировать</RouterLink>
                  <button type="button" class="btn-outline" @click="duplicateShowcase(item)">Копировать</button>
                  <button type="button" class="btn-outline text-destructive" @click="deleteShowcase(item)">Удалить</button>
                </div>
              </td>
            </tr>
            <tr v-if="!showcases.length">
              <td colspan="4" class="px-4 py-10 text-center text-muted-foreground">
                Витрин пока нет.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>
