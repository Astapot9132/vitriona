<script setup>
import { onMounted, reactive, ref } from 'vue'

import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/lib/api'
import { formatDateTime } from '@/lib/format'

const loading = ref(false)
const syncing = ref(false)
const selectedOffer = ref(null)
const syncMessage = ref(null)
const data = ref({ offers: { data: [], meta: {} }, filters: {}, categories: [], countries: [], synced_at: null, has_api_key: false })
const filters = reactive({ search: '', category: '', country: '', page: 1 })

async function load() {
  loading.value = true
  const { data: response } = await api.get('/offers', { params: filters })
  data.value = response
  filters.search = response.filters.search || ''
  filters.category = response.filters.category || ''
  filters.country = response.filters.country || ''
  loading.value = false
}

async function syncOffers() {
  syncing.value = true
  syncMessage.value = null
  try {
    const { data: response } = await api.post('/offers/sync')
    syncMessage.value = { type: 'success', text: response.message }
    await load()
  } catch (err) {
    syncMessage.value = { type: 'error', text: err.response?.data?.detail || 'Ошибка синхронизации' }
  } finally {
    syncing.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppLayout role="client">
    <div>
      <div class="flex items-center justify-between border-b border-border px-6 py-4">
        <div>
          <h1 class="text-xl font-semibold">Офферы</h1>
          <p class="mt-0.5 text-sm text-muted-foreground">
            Всего: {{ data.offers.meta.total || 0 }}
            <span v-if="data.synced_at" class="ml-3">Обновлено: {{ formatDateTime(data.synced_at) }}</span>
          </p>
        </div>
        <button v-if="data.has_api_key" type="button" class="btn-primary" :disabled="syncing" @click="syncOffers">
          {{ syncing ? 'Синхронизация...' : 'Обновить из Affise' }}
        </button>
      </div>

      <div v-if="syncMessage" class="mx-6 mt-4 rounded-lg border px-4 py-3 text-sm" :class="syncMessage.type === 'success' ? 'border-green-200 bg-green-50 text-green-800' : 'border-red-200 bg-red-50 text-red-800'">
        {{ syncMessage.text }}
      </div>

      <div v-if="!data.has_api_key" class="mx-6 mt-4 rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-800">
        API-ключ Affise не найден. Обратитесь в поддержку.
      </div>

      <div class="flex flex-wrap gap-3 px-6 py-4">
        <input v-model="filters.search" class="input-base w-72" placeholder="Поиск по названию или ID" @keyup.enter="load" />
        <select v-model="filters.category" class="input-base w-56" @change="load">
          <option value="">Все категории</option>
          <option v-for="item in data.categories" :key="item" :value="item">{{ item }}</option>
        </select>
        <select v-model="filters.country" class="input-base w-44" @change="load">
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
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">ГЕО</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">Выплата</th>
                <th class="px-4 py-3 text-left font-medium text-muted-foreground">EPC</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="offer in data.offers.data" :key="offer.id" class="cursor-pointer border-b border-border last:border-0 hover:bg-muted/30" @click="selectedOffer = offer">
                <td class="px-4 py-3 text-muted-foreground">{{ offer.external_id }}</td>
                <td class="px-4 py-3 font-medium">{{ offer.title }}</td>
                <td class="px-4 py-3 text-muted-foreground">{{ (offer.countries || []).slice(0, 4).join(', ') || '—' }}</td>
                <td class="px-4 py-3 text-muted-foreground">
                  {{ offer.payments?.[0]?.revenue ? `$${offer.payments[0].revenue}` : '—' }}
                </td>
                <td class="px-4 py-3 text-muted-foreground">{{ offer.epc || 0 }}</td>
              </tr>
              <tr v-if="!data.offers.data.length && !loading">
                <td colspan="5" class="px-4 py-10 text-center text-sm text-muted-foreground">Офферы не найдены</td>
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
          <div v-if="selectedOffer.link">
            <div class="mb-2 text-[11px] font-bold uppercase tracking-widest text-primary/70">Ваша трекинговая ссылка</div>
            <code class="block rounded-md border border-border bg-muted px-3 py-2 text-sm">{{ selectedOffer.link }}</code>
          </div>
          <div v-if="selectedOffer.description_lang">
            <div class="mb-2 text-[11px] font-bold uppercase tracking-widest text-muted-foreground/60">Описание</div>
            <div v-for="(text, lang) in selectedOffer.description_lang" :key="lang" class="mb-3">
              <div class="mb-1 text-xs uppercase text-muted-foreground">{{ lang }}</div>
              <div class="text-sm leading-relaxed" v-html="text" />
            </div>
          </div>
          <div v-if="selectedOffer.landings?.length">
            <div class="mb-2 text-[11px] font-bold uppercase tracking-widest text-muted-foreground/60">Лендинги</div>
            <div class="space-y-2">
              <div v-for="(landing, index) in selectedOffer.landings" :key="index" class="rounded-md border border-border px-3 py-2">
                <div class="text-sm font-medium">{{ landing.title || `Лендинг ${index + 1}` }}</div>
                <div class="text-xs text-muted-foreground">{{ landing.url || landing.url_preview || landing.hash }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
