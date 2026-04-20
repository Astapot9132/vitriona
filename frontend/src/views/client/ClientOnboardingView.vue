<script setup lang="ts">
import type { AxiosError } from 'axios'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { COUNTRIES } from '@/lib/countries'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

type FieldType = 'multiselect' | 'select' | 'text'

type OnboardingFieldValue = string | string[]
type OnboardingFieldValues = Record<number, OnboardingFieldValue>

interface CustomField {
  id: number
  name: string
  field_type?: FieldType
  field_values?: Record<string, string>
}

interface OnboardingResponse {
  redirect?: string
  detected_country?: string | null
  custom_fields?: CustomField[]
}

interface RedirectResponse {
  redirect: string
}

interface ErrorResponse {
  detail?: string
  message?: string
}

const router = useRouter()
const auth = useAuthStore()
const detectedCountry = ref('')
const customFields = ref<CustomField[]>([])
const country = ref('')
const values = reactive<OnboardingFieldValues>({})
const loading = ref(false)
const apiError = ref('')

onMounted(async () => {
  const { data } = await api.get<OnboardingResponse>('/onboarding')
  if (data.redirect) {
    await router.push(data.redirect)
    return
  }
  detectedCountry.value = data.detected_country || ''
  country.value = data.detected_country || ''
  customFields.value = data.custom_fields || []
  for (const field of customFields.value) {
    values[field.id] = field.field_type === 'multiselect' ? [] : ''
  }
})

async function submit(): Promise<void> {
  loading.value = true
  apiError.value = ''
  try {
    const { data } = await api.post<RedirectResponse>('/onboarding', {
      country: country.value,
      custom_fields: values,
    })
    await auth.bootstrap(true)
    await router.push(data.redirect)
  } catch (err) {
    const apiErrorResponse = err as AxiosError<ErrorResponse>
    apiError.value = apiErrorResponse.response?.data?.detail || apiErrorResponse.response?.data?.message || 'Ошибка сохранения'
  } finally {
    loading.value = false
  }
}

function toggleMulti(fieldId: number, option: string): void {
  const current = Array.isArray(values[fieldId]) ? values[fieldId] : []
  if (current.includes(option)) {
    values[fieldId] = current.filter((item) => item !== option)
  } else {
    values[fieldId] = [...current, option]
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-4">
    <div class="mx-auto w-full max-w-md">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-lg font-bold text-primary-foreground">
          V
        </div>
        <h1 class="text-2xl font-semibold tracking-tight">Завершите регистрацию</h1>
        <p class="mt-1 text-sm text-muted-foreground">Заполните профиль для активации аккаунта</p>
      </div>

      <form class="card-base space-y-5 p-6" @submit.prevent="submit">
        <div class="space-y-2">
          <label class="text-sm font-medium">Страна</label>
          <select v-model="country" class="input-base">
            <option disabled value="">— выберите страну —</option>
            <option v-for="item in COUNTRIES" :key="item.code" :value="item.code">
              {{ item.name }} ({{ item.code }})
            </option>
          </select>
        </div>

        <div v-for="field in customFields" :key="field.id" class="space-y-2">
          <label class="text-sm font-medium">{{ field.name }}</label>
          <div v-if="field.field_type === 'multiselect'" class="grid gap-2 rounded-md border border-border p-3">
            <label
              v-for="(label, key) in field.field_values || {}"
              :key="key"
              class="flex items-center gap-2 text-sm"
            >
              <input
                type="checkbox"
                :checked="(values[field.id] || []).includes(key)"
                @change="toggleMulti(field.id, key)"
              />
              {{ label }}
            </label>
          </div>
          <select v-else-if="field.field_type === 'select'" v-model="values[field.id]" class="input-base">
            <option disabled value="">— выберите —</option>
            <option v-for="(label, key) in field.field_values || {}" :key="key" :value="key">
              {{ label }}
            </option>
          </select>
          <input v-else v-model="values[field.id]" type="text" class="input-base" :placeholder="field.name" />
        </div>

        <div v-if="apiError" class="rounded-md border border-destructive/20 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {{ apiError }}
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Создание аккаунта...' : 'Завершить регистрацию' }}
        </button>
      </form>
    </div>
  </div>
</template>
