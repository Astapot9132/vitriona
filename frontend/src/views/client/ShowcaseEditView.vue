<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppLayout from '@/components/AppLayout.vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { api } from '@/lib/api'
import buildPreviewHtml, { PREVIEW_CSS } from '@/lib/showcases/buildPreviewHtml'
import type { PreviewMode, PreviewResult } from '@/lib/showcases/buildPreviewHtml'
import { DEFAULT_CONFIG, DEFAULT_OFFER_DESCRIPTION, DEFAULT_OFFER_POINT, DESIGN_VARIANTS } from '@/lib/showcases/constructorDefaults'
import type { ShowcaseConfig, ShowcaseOffer } from '@/lib/showcases/constructorDefaults'

type ShowcaseRecord = {
  id: number
  name: string
  config: Partial<ShowcaseConfig>
}

type ShowcaseDomain = {
  id: number
  webmaster_domain: string
}

type ShowcaseResponse = {
  showcase: ShowcaseRecord
  offers?: ShowcaseOffer[]
  domains?: ShowcaseDomain[]
  systemDomains?: string[]
  previewUrl?: string | null
}

type SaveShowcaseResponse = {
  previewUrl?: string | null
}

const route = useRoute()
const showcase = ref<ShowcaseRecord | null>(null)
const offers = ref<ShowcaseOffer[]>([])
const domains = ref<ShowcaseDomain[]>([])
const systemDomains = ref<string[]>([])
const previewUrl = ref('')
const saving = ref(false)
const toast = ref('')
const previewMode = ref<PreviewMode>('mobile')
const config = reactive<ShowcaseConfig>(structuredClone(DEFAULT_CONFIG) as ShowcaseConfig)
const search = ref('')

const preview = computed<PreviewResult>(() => (
  buildPreviewHtml(config, offers.value, previewMode.value) as PreviewResult
))
const previewMarkup = computed(() => `<style>${PREVIEW_CSS}</style>${preview.value.html}`)

const filteredOffers = computed<ShowcaseOffer[]>(() => {
  if (!search.value) return offers.value
  return offers.value.filter((item) => (
    String(item.external_id).includes(search.value)
      || item.title.toLowerCase().includes(search.value.toLowerCase())
  ))
})

const selectedOffers = computed<ShowcaseOffer[]>(() => {
  const ids = config.selectedOfferIds || []
  return offers.value.filter((offer) => ids.includes(offer.id))
})

function mergeConfig(savedConfig?: Partial<ShowcaseConfig> | null): void {
  Object.assign(config, structuredClone(DEFAULT_CONFIG))
  if (savedConfig && typeof savedConfig === 'object') {
    Object.assign(config, savedConfig)
  }
  if ((!savedConfig || !savedConfig.selectedOfferIds?.length) && offers.value.length) {
    const firstThree = offers.value.slice(0, 3)
    config.selectedOfferIds = firstThree.map((item) => item.id)
    config.showcaseOrder = firstThree.map((item) => item.id)
    config.offerDisplayDescriptions = {}
    config.offerPoints = {}
    firstThree.forEach((item, index) => {
      config.offerDisplayDescriptions[item.id] = DEFAULT_OFFER_DESCRIPTION
      if (index === 0) {
        config.offerPoints[item.id] = [DEFAULT_OFFER_POINT]
      }
    })
  }
}

function toggleOffer(offerId: number): void {
  if (config.selectedOfferIds.includes(offerId)) {
    config.selectedOfferIds = config.selectedOfferIds.filter((item) => item !== offerId)
    config.showcaseOrder = config.showcaseOrder.filter((item) => item !== offerId)
  } else {
    config.selectedOfferIds = [...config.selectedOfferIds, offerId]
    config.showcaseOrder = [...config.showcaseOrder, offerId]
  }
}

function toggleAccent(offerId: number): void {
  if (config.accentedOfferIds.includes(offerId)) {
    config.accentedOfferIds = config.accentedOfferIds.filter((item) => item !== offerId)
  } else {
    config.accentedOfferIds = [...config.accentedOfferIds, offerId]
  }
}

function updateOfferDisplayName(offerId: number, value: string): void {
  config.offerDisplayNames = {
    ...config.offerDisplayNames,
    [offerId]: value,
  }
}

function updateOfferDescription(offerId: number, value: string): void {
  config.offerDisplayDescriptions = {
    ...config.offerDisplayDescriptions,
    [offerId]: value,
  }
}

function updateOfferCtaText(offerId: number, value: string): void {
  config.offerCtaTexts = {
    ...config.offerCtaTexts,
    [offerId]: value,
  }
}

function updateOfferPoints(offerId: number, value: string[]): void {
  config.offerPoints = {
    ...config.offerPoints,
    [offerId]: value,
  }
}

function addLandingPoint(): void {
  if (config.landingPoints.length < 3) {
    config.landingPoints = [...config.landingPoints, '']
  }
}

function addOfferPoint(offerId: number): void {
  const current = config.offerPoints[offerId] || []
  if (current.length < 3) {
    updateOfferPoints(offerId, [...current, ''])
  }
}

function onOfferDisplayNameInput(offerId: number, event: Event): void {
  updateOfferDisplayName(offerId, (event.target as HTMLInputElement).value)
}

function onOfferDescriptionInput(offerId: number, event: Event): void {
  updateOfferDescription(offerId, (event.target as HTMLTextAreaElement).value)
}

function onOfferCtaTextInput(offerId: number, event: Event): void {
  updateOfferCtaText(offerId, (event.target as HTMLInputElement).value)
}

function onOfferPointInput(offerId: number, index: number, event: Event): void {
  const current = config.offerPoints[offerId] || []
  updateOfferPoints(
    offerId,
    current.map((item, idx) => (idx === index ? (event.target as HTMLInputElement).value : item)),
  )
}

function removeOfferPoint(offerId: number, index: number): void {
  const current = config.offerPoints[offerId] || []
  updateOfferPoints(offerId, current.filter((_, idx) => idx !== index))
}

async function load(): Promise<void> {
  const { data } = await api.get<ShowcaseResponse>(`/showcases/${route.params.id}`)
  showcase.value = data.showcase
  offers.value = data.offers || []
  domains.value = data.domains || []
  systemDomains.value = data.systemDomains || []
  previewUrl.value = data.previewUrl || ''
  mergeConfig(data.showcase.config)
}

async function save(): Promise<void> {
  saving.value = true
  try {
    const { data } = await api.put<SaveShowcaseResponse>(`/showcases/${route.params.id}`, { config })
    previewUrl.value = data.previewUrl || previewUrl.value
    toast.value = 'Витрина сохранена'
  } finally {
    saving.value = false
  }
}

async function openPreview(): Promise<void> {
  await save()
  window.open(previewUrl.value || `/storage/landings/${route.params.id}/index.html`, '_blank')
}

onMounted(load)
</script>

<template>
  <AppLayout role="client">
    <ToastMessage v-if="toast" :message="toast" @done="toast = ''" />

    <div v-if="showcase" class="flex h-[calc(100vh-3.5rem)]">
      <div class="w-[520px] shrink-0 overflow-y-auto border-r border-border">
        <div class="flex items-center justify-between border-b border-border px-4 py-3">
          <div>
            <h1 class="text-sm font-semibold">{{ showcase.name }}</h1>
            <p class="text-xs text-muted-foreground">Конструктор витрины</p>
          </div>
          <button type="button" class="btn-primary" :disabled="saving" @click="save">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>

        <div class="space-y-6 p-4">
          <section class="space-y-3">
            <h2 class="text-sm font-medium">Дизайн</h2>
            <input v-model="config.title" class="input-base" placeholder="Заголовок лендинга" />
            <textarea v-model="config.description" class="textarea-base" rows="3" placeholder="Описание лендинга" />
            <textarea v-model="config.legalInfo" class="textarea-base" rows="4" placeholder="Юридическая информация" />
            <select v-model="config.designVariant" class="input-base">
              <option v-for="item in DESIGN_VARIANTS" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
            <label class="flex items-center gap-2 text-sm">
              <input v-model="config.offersTwoColDesktop" type="checkbox" />
              Карточки в два ряда на десктопе
            </label>
          </section>

          <section class="space-y-3">
            <div class="flex items-center justify-between">
              <h2 class="text-sm font-medium">Пойнты лендинга</h2>
              <button type="button" class="btn-outline" @click="addLandingPoint">Добавить</button>
            </div>
            <div v-for="(point, index) in config.landingPoints" :key="index" class="flex gap-2">
              <input v-model="config.landingPoints[index]" class="input-base" :placeholder="`Пойнт ${index + 1}`" />
              <button type="button" class="btn-outline" @click="config.landingPoints.splice(index, 1)">Удалить</button>
            </div>
          </section>

          <section class="space-y-3">
            <h2 class="text-sm font-medium">Аналитика и домен</h2>
            <select v-model="config.domainType" class="input-base">
              <option value="system">Системный домен</option>
              <option value="custom">Свой домен</option>
            </select>
            <select v-if="config.domainType === 'system'" v-model="config.systemDomain" class="input-base">
              <option v-for="item in systemDomains" :key="item" :value="item">{{ item }}</option>
            </select>
            <select v-else v-model="config.customDomain" class="input-base">
              <option value="">— выберите домен —</option>
              <option v-for="item in domains" :key="item.id" :value="item.webmaster_domain">{{ item.webmaster_domain }}</option>
            </select>
            <input v-model="config.trackingLink" class="input-base" placeholder="Трекинговый домен" />
          </section>

          <section class="space-y-3">
            <h2 class="text-sm font-medium">Офферы</h2>
            <input v-model="search" class="input-base" placeholder="Поиск по ID или названию" />
            <div class="max-h-72 overflow-y-auto rounded-lg border border-border">
              <label
                v-for="offer in filteredOffers"
                :key="offer.id"
                class="flex items-center gap-3 border-b border-border px-3 py-2 last:border-0 hover:bg-muted/30"
              >
                <input :checked="config.selectedOfferIds.includes(offer.id)" type="checkbox" @change="toggleOffer(offer.id)" />
                <div class="min-w-0 flex-1">
                  <div class="truncate text-sm font-medium">{{ offer.title }}</div>
                  <div class="text-xs text-muted-foreground">#{{ offer.external_id }} · EPC {{ offer.epc || 0 }}</div>
                </div>
              </label>
            </div>
          </section>

          <section v-if="selectedOffers.length" class="space-y-4">
            <h2 class="text-sm font-medium">Настройки выбранных офферов</h2>
            <div v-for="offer in selectedOffers" :key="offer.id" class="rounded-lg border border-border p-3">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium">{{ offer.title }}</div>
                  <div class="text-xs text-muted-foreground">#{{ offer.external_id }}</div>
                </div>
                <label class="flex items-center gap-2 text-xs">
                  <input :checked="config.accentedOfferIds.includes(offer.id)" type="checkbox" @change="toggleAccent(offer.id)" />
                  Акцент
                </label>
              </div>
              <div class="space-y-2">
                <input
                  :value="config.offerDisplayNames?.[offer.id] || ''"
                  class="input-base"
                  placeholder="Отображаемое название"
                  @input="onOfferDisplayNameInput(offer.id, $event)"
                />
                <textarea
                  :value="config.offerDisplayDescriptions?.[offer.id] || ''"
                  class="textarea-base"
                  rows="2"
                  placeholder="Описание"
                  @input="onOfferDescriptionInput(offer.id, $event)"
                />
                <input
                  :value="config.offerCtaTexts?.[offer.id] || ''"
                  class="input-base"
                  placeholder="Текст кнопки"
                  @input="onOfferCtaTextInput(offer.id, $event)"
                />
                <div class="space-y-2">
                  <div
                    v-for="(point, index) in config.offerPoints?.[offer.id] || []"
                    :key="index"
                    class="flex gap-2"
                  >
                    <input
                      :value="point"
                      class="input-base"
                      :placeholder="`Пойнт ${index + 1}`"
                      @input="onOfferPointInput(offer.id, index, $event)"
                    />
                    <button
                      type="button"
                      class="btn-outline"
                      @click="removeOfferPoint(offer.id, index)"
                    >
                      Удалить
                    </button>
                  </div>
                  <button type="button" class="btn-outline" @click="addOfferPoint(offer.id)">Добавить пойнт</button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>

      <div class="flex flex-1 flex-col bg-muted/30">
        <div class="flex items-center justify-between border-b border-border bg-background px-4 py-2">
          <span class="text-sm font-medium">Превью</span>
          <div class="flex items-center gap-2">
            <button type="button" class="btn-outline" @click="previewMode = previewMode === 'mobile' ? 'desktop' : 'mobile'">
              {{ previewMode === 'mobile' ? 'Моб.' : 'Десктоп' }}
            </button>
            <button type="button" class="btn-outline" @click="openPreview">Смотреть результат</button>
          </div>
        </div>

        <div class="flex flex-1 items-start justify-center overflow-auto p-6">
          <div :class="preview.containerClass" v-html="previewMarkup" />
        </div>
      </div>
    </div>
  </AppLayout>
</template>
