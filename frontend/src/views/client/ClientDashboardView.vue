<script setup>
import { ref } from 'vue'

import AppLayout from '@/components/AppLayout.vue'
import { COUNTRIES } from '@/lib/countries'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const country = ref(auth.user?.affise_country || '')
const copied = ref(false)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

async function copyPassword() {
  if (!auth.user?.affise_password) return
  await navigator.clipboard.writeText(auth.user.affise_password)
  copied.value = true
  window.setTimeout(() => { copied.value = false }, 2000)
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

      <div v-if="auth.user?.affise_password" class="card-base space-y-4 p-5">
        <h2 class="text-sm font-medium">Данные для Affise</h2>
        <div class="space-y-1">
          <label class="text-xs text-muted-foreground">Пароль</label>
          <div class="flex items-center gap-2">
            <input :value="auth.user.affise_password" readonly class="input-base flex-1 font-mono" />
            <button type="button" class="btn-outline" @click="copyPassword">
              {{ copied ? 'Скопировано' : 'Копировать' }}
            </button>
          </div>
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
