<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/lib/api'
import { formatDateTime } from '@/lib/format'

type AdminOffer = {
  id: number
  external_id: string | number
  title: string
  status: string
  countries?: string[] | null
  epc?: number | null
  synced_at?: string | null
  url?: string | null
  preview_url?: string | null
  description_lang?: Record<string, string> | null
  raw_data?: unknown
}

type AdminOffersResponse = {
  offers: {
    data: AdminOffer[]
    meta: {
      total?: number
    }
  }
  filters: Record<string, string>
  categories: string[]
  countries: string[]
}

const data = ref<AdminOffersResponse>({
  offers: { data: [], meta: {} },
  filters: {},
  categories: [],
  countries: [],
})
const filters = reactive({ search: '', category: '', status: '', country: '', sort: 'id', dir: 'desc', page: 1 })
const syncing = ref(false)
const selectedOffer = ref<AdminOffer | null>(null)

async function load(): Promise<void> {
  const { data: response } = await api.get<AdminOffersResponse>('/admin/offers', { params: filters })
  data.value = response
}

async function syncOffers(): Promise<void> {
  syncing.value = true
  try {
    await api.post('/admin/offers/sync')
    await load()
  } finally {
    syncing.value = false
  }
}

async function openOffer(item: AdminOffer): Promise<void> {
  const { data: response } = await api.get<AdminOffer>(`/admin/offers/${item.id}`)
  selectedOffer.value = response
}

onMounted(load)
</script>

<template>
  <AppLayout role="admin">
    <div>
      <div class="flex items-center justify-between border-b border-border px-6 py-4">
        <div>
          <h1 class="text-xl font-semibold">Офферы</h1>
          <p class="mt-0.5 text-sm text-muted-foreground">Всего: {{ data.offers.meta.total || 0 }}</p>
        </div>
        <button type="button" class="btn-primary" :disabled="syncing" @click="syncOffers">
          {{ syncing ? 'Синхронизация...' : 'Синхронизировать' }}
        </button>
      </div>

      <div class="flex flex-wrap gap-3 px-6 py-4">
        <input v-model="filters.search" class="input-base w-72" placeholder="Поиск" @keyup.enter="load" />
        <select v-model="filters.category" class="input-base w-56" @change="load">
          <option value="">Все категории</option>
          <option v-for="item in data.categories" :key="item" :value="item">{{ item }}</option>
        </select>
        <select v-model="filters.status" class="input-base w-40" @change="load">
          <option value="">Все статусы</option>
          <option value="active">active</option>
          <option value="paused">paused</option>
          <option value="inactive">inactive</option>
        </select>
        <select v-model="filters.country" class="input-base w-40" @change="load">
          <option value="">Все ГЕО</option>
          <option v-for="item in data.countries" :key="item" :value="item">{{ item }}</option>
        </select>
        <button type="button" class="btn-outline" @click="load">Найти</button>
      </div>

      <div class="px-6 pb-6">
        <div class="overflow-hidden rounded-lg border border-border">
          <table class="w-full text-sm">
            <thead class="bg-muted/40">
              <tr class="border-b border-border">
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">ID</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">Оффер</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">Статус</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">ГЕО</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">EPC</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">Sync</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="offer in data.offers.data" :key="offer.id" class="cursor-pointer border-b border-border last:border-0 hover:bg-muted/30" @click="openOffer(offer)">
                <td class="px-4 py-3 text-muted-foreground">{{ offer.external_id }}</td>
                <td class="px-4 py-3 font-medium">{{ offer.title }}</td>
                <td class="px-4 py-3">
                  <span class="rounded px-2 py-0.5 text-xs font-medium" :class="offer.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ offer.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-muted-foreground">{{ (offer.countries || []).slice(0, 4).join(', ') || '—' }}</td>
                <td class="px-4 py-3 text-muted-foreground">{{ offer.epc || 0 }}</td>
                <td class="px-4 py-3 text-muted-foreground">{{ formatDateTime(offer.synced_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="selectedOffer" class="fixed inset-0 z-40 bg-black/30" @click="selectedOffer = null" />
      <div v-if="selectedOffer" class="fixed right-0 top-0 z-50 flex h-full w-full max-w-2xl flex-col border-l border-border bg-background shadow-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-border px-6 py-4">
          <div>
            <div class="text-xs font-mono text-muted-foreground">#{{ selectedOffer.external_id }}</div>
            <h2 class="mt-1 text-lg font-semibold">{{ selectedOffer.title }}</h2>
          </div>
          <button type="button" class="btn-ghost text-xl" @click="selectedOffer = null">×</button>
        </div>
        <div class="flex-1 space-y-5 overflow-y-auto px-6 py-5">
          <div>
            <div class="mb-2 text-[11px] font-bold uppercase tracking-widest text-muted-foreground/60">Ссылки</div>
            <div class="space-y-2 text-sm">
              <a v-if="selectedOffer.url" :href="selectedOffer.url" class="block text-primary hover:underline" target="_blank" rel="noreferrer">{{ selectedOffer.url }}</a>
              <a v-if="selectedOffer.preview_url" :href="selectedOffer.preview_url" class="block text-primary hover:underline" target="_blank" rel="noreferrer">{{ selectedOffer.preview_url }}</a>
            </div>
          </div>
          <div v-if="selectedOffer.description_lang">
            <div class="mb-2 text-[11px] font-bold uppercase tracking-widest text-muted-foreground/60">Описание</div>
            <div v-for="(text, lang) in selectedOffer.description_lang" :key="lang" class="mb-3">
              <div class="mb-1 text-xs uppercase text-muted-foreground">{{ lang }}</div>
              <div class="text-sm leading-relaxed" v-html="text" />
            </div>
          </div>
          <pre class="overflow-x-auto rounded-lg bg-muted p-3 text-xs text-muted-foreground">{{ JSON.stringify(selectedOffer.raw_data, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
