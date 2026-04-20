<script setup>
import { ref } from 'vue'

import AppLayout from '@/components/AppLayout.vue'
import { COUNTRIES } from '@/lib/countries'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const country = ref(auth.user?.affise_country || '')
const copied = ref(false)
const revealLoading = ref(false)
const revealedPassword = ref('')
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const revealError = ref('')

async function copyPassword() {
  if (!revealedPassword.value) return
  await navigator.clipboard.writeText(revealedPassword.value)
  copied.value = true
  window.setTimeout(() => { copied.value = false }, 2000)
}

async function revealPassword() {
  revealLoading.value = true
  revealError.value = ''
  try {
    const { data } = await api.post('/dashboard/affise-password')
    revealedPassword.value = data.password || ''
  } catch (err) {
    revealError.value = err.response?.data?.detail || 'Не удалось получить пароль'
  } finally {
    revealLoading.value = false
  }
}

async function saveCountry() {
  saving.value = true
  error.value = ''
  try {
    await api.patch('/profile/country', { country: country.value })
    await auth.bootstrap(true)
    saved.value = true
    window.setTimeout(() => { saved.value = false }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppLayout role="client">
    <div class="max-w-xl space-y-6 p-6">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">Добро пожаловать</h1>
        <p class="mt-1 text-sm text-muted-foreground">Личный кабинет</p>
      </div>

      <div v-if="auth.user?.is_onboarded" class="card-base space-y-4 p-5">
        <h2 class="text-sm font-medium">Данные для Affise</h2>
        <div class="space-y-1">
          <label class="text-xs text-muted-foreground">Пароль</label>
          <div class="flex items-center gap-2">
            <input :value="revealedPassword || '••••••••••'" readonly class="input-base flex-1 font-mono" />
            <button type="button" class="btn-outline" :disabled="revealLoading" @click="revealPassword">
              {{ revealLoading ? 'Загрузка...' : revealedPassword ? 'Обновить' : 'Показать пароль' }}
            </button>
            <button type="button" class="btn-outline" :disabled="!revealedPassword" @click="copyPassword">
              {{ copied ? 'Скопировано' : 'Копировать' }}
            </button>
          </div>
          <p v-if="revealError" class="text-xs text-destructive">{{ revealError }}</p>
        </div>

        <div class="space-y-1">
          <label class="text-xs text-muted-foreground">Страна</label>
          <div class="flex items-center gap-2">
            <select v-model="country" class="input-base flex-1">
              <option value="">— выберите страну —</option>
              <option v-for="item in COUNTRIES" :key="item.code" :value="item.code">
                {{ item.name }} ({{ item.code }})
              </option>
            </select>
            <button type="button" class="btn-primary" :disabled="saving || !country" @click="saveCountry">
              {{ saved ? 'Сохранено' : saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
          <p v-if="error" class="text-xs text-destructive">{{ error }}</p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
