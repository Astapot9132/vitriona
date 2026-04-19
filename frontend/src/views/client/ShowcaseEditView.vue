<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppLayout from '@/components/AppLayout.vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { api } from '@/lib/api'
import buildPreviewHtml, { PREVIEW_CSS } from '@/lib/showcases/buildPreviewHtml'
import { DEFAULT_CONFIG, DEFAULT_OFFER_DESCRIPTION, DEFAULT_OFFER_POINT, DESIGN_VARIANTS } from '@/lib/showcases/constructorDefaults'

const route = useRoute()
const showcase = ref(null)
const offers = ref([])
const domains = ref([])
const systemDomains = ref([])
const previewUrl = ref('')
const saving = ref(false)
const toast = ref('')
const previewMode = ref('mobile')
const config = reactive(structuredClone(DEFAULT_CONFIG))
const search = ref('')

const preview = computed(() => buildPreviewHtml(config, offers.value, previewMode.value))
const previewMarkup = computed(() => `<style>${PREVIEW_CSS}</style>${preview.value.html}`)

const filteredOffers = computed(() => {
  if (!search.value) return offers.value
  return offers.value.filter((item) => String(item.external_id).includes(search.value) || item.title.toLowerCase().includes(search.value.toLowerCase()))
})

const selectedOffers = computed(() => {
  const ids = config.selectedOfferIds || []
  return offers.value.filter((offer) => ids.includes(offer.id))
})

function mergeConfig(savedConfig) {
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

function toggleOffer(offerId) {
  if (config.selectedOfferIds.includes(offerId)) {
    config.selectedOfferIds = config.selectedOfferIds.filter((item) => item !== offerId)
    config.showcaseOrder = config.showcaseOrder.filter((item) => item !== offerId)
  } else {
    config.selectedOfferIds = [...config.selectedOfferIds, offerId]
    config.showcaseOrder = [...config.showcaseOrder, offerId]
  }
}

function toggleAccent(offerId) {
  if (config.accentedOfferIds.includes(offerId)) {
    config.accentedOfferIds = config.accentedOfferIds.filter((item) => item !== offerId)
  } else {
    config.accentedOfferIds = [...config.accentedOfferIds, offerId]
  }
}

function updateOfferField(target, offerId, value) {
  config[target] = {
    ...config[target],
    [offerId]: value,
  }
}

function addLandingPoint() {
  if (config.landingPoints.length < 3) {
    config.landingPoints = [...config.landingPoints, '']
  }
}

function addOfferPoint(offerId) {
  const current = config.offerPoints[offerId] || []
  if (current.length < 3) {
    updateOfferField('offerPoints', offerId, [...current, ''])
  }
}

async function load() {
  const { data } = await api.get(`/showcases/${route.params.id}`)
  showcase.value = data.showcase
  offers.value = data.offers || []
  domains.value = data.domains || []
  systemDomains.value = data.systemDomains || []
  previewUrl.value = data.previewUrl || ''
  mergeConfig(data.showcase.config)
}

async function save() {
  saving.value = true
  try {
    const { data } = await api.put(`/showcases/${route.params.id}`, { config })
    previewUrl.value = data.previewUrl || previewUrl.value
    toast.value = 'Витрина сохранена'
  } finally {
    saving.value = false
  }
}

async function openPreview() {
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
                  @input="updateOfferField('offerDisplayNames', offer.id, $event.target.value)"
                />
                <textarea
                  :value="config.offerDisplayDescriptions?.[offer.id] || ''"
                  class="textarea-base"
                  rows="2"
                  placeholder="Описание"
                  @input="updateOfferField('offerDisplayDescriptions', offer.id, $event.target.value)"
                />
                <input
                  :value="config.offerCtaTexts?.[offer.id] || ''"
                  class="input-base"
                  placeholder="Текст кнопки"
                  @input="updateOfferField('offerCtaTexts', offer.id, $event.target.value)"
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
                      @input="updateOfferField('offerPoints', offer.id, (config.offerPoints?.[offer.id] || []).map((item, idx) => idx === index ? $event.target.value : item))"
                    />
                    <button
                      type="button"
                      class="btn-outline"
                      @click="updateOfferField('offerPoints', offer.id, (config.offerPoints?.[offer.id] || []).filter((_, idx) => idx !== index))"
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
