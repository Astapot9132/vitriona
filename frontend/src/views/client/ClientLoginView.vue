<script setup lang="ts">
import type { AxiosError } from 'axios'
import { computed, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import PinCodeInput from '@/components/PinCodeInput.vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

type LoginStep = 'email' | 'pin'

interface RedirectResponse {
  redirect: string
}

interface ErrorResponse {
  detail?: string
  message?: string
}

const router = useRouter()
const auth = useAuthStore()

const step = ref<LoginStep>('email')
const email = ref('')
const pin = ref('')
const cooldown = ref(0)
const loading = ref(false)
const error = ref('')
const banned = ref(false)
const retryAvailableAt = ref<number | null>(null)
let timerId: number | null = null

onUnmounted(() => {
  if (timerId !== null) {
    window.clearInterval(timerId)
    timerId = null
  }
})

function startCooldown(seconds = 60): void {
  if (timerId !== null) {
    window.clearInterval(timerId)
  }
  cooldown.value = seconds
  timerId = window.setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      if (timerId !== null) {
        window.clearInterval(timerId)
      }
      cooldown.value = 0
      retryAvailableAt.value = null
      timerId = null
    }
  }, 1000)
}

function applyRetryCooldown(seconds: number): void {
  retryAvailableAt.value = Date.now() + seconds * 1000
  startCooldown(seconds)
}

const retryAtLabel = computed(() => {
  if (!retryAvailableAt.value) return ''
  return new Date(retryAvailableAt.value).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
})

async function sendPin(): Promise<boolean> {
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/client/send-pin', { email: email.value })
    applyRetryCooldown(60)
    return true
  } catch (err) {
    const apiError = err as AxiosError<ErrorResponse>
    if (apiError.response?.status === 403) {
      banned.value = true
    }
    const retryAfter = Number(apiError.response?.headers?.['retry-after'] || 0)
    if (retryAfter > 0) {
      applyRetryCooldown(retryAfter)
      error.value = ''
      return false
    }
    error.value = apiError.response?.data?.detail || apiError.response?.data?.message || 'Ошибка при отправке кода.'
    return false
  } finally {
    loading.value = false
  }
}

async function submitEmail(): Promise<void> {
  const ok = await sendPin()
  if (ok) {
    step.value = 'pin'
  }
}

async function submitPin(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post<RedirectResponse>('/auth/client/verify-pin', {
      email: email.value,
      pin: pin.value,
    })
    await auth.bootstrap(true)
    await router.push(data.redirect)
  } catch (err) {
    const apiError = err as AxiosError<ErrorResponse>
    error.value = apiError.response?.data?.detail || apiError.response?.data?.message || 'Ошибка проверки кода.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-secondary p-4">
    <div class="w-full max-w-sm space-y-6">
      <div class="space-y-2 text-center">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-xl font-bold text-primary-foreground">
          V
        </div>
        <h1 class="text-2xl font-semibold tracking-tight">Vitriona</h1>
      </div>

      <div class="card-base p-6">
        <form v-if="step === 'email'" class="space-y-4" @submit.prevent="submitEmail">
          <div>
            <h2 class="text-lg font-semibold">Вход в аккаунт</h2>
            <p class="mt-1 text-sm text-muted-foreground">Введите email и мы вышлем PIN-код для входа</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">Email</label>
            <input v-model="email" type="email" class="input-base" placeholder="you@example.com" :disabled="loading || banned" required />
          </div>
          <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
          <p v-if="cooldown > 0 && retryAtLabel" class="text-sm text-muted-foreground">
            Следующий код можно запросить в {{ retryAtLabel }}
          </p>
          <button type="submit" class="btn-primary w-full" :disabled="loading || cooldown > 0 || banned">
            {{ loading ? 'Отправляем...' : cooldown > 0 ? `Подождите (${cooldown}с)` : 'Продолжить' }}
          </button>
        </form>

        <form v-else class="space-y-4" @submit.prevent="submitPin">
          <div>
            <h2 class="text-lg font-semibold">Введите PIN-код</h2>
            <p class="mt-1 text-sm text-muted-foreground">Код отправлен на <span class="font-medium text-foreground">{{ email }}</span></p>
          </div>
          <PinCodeInput v-model="pin" :disabled="loading" />
          <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
          <p v-if="cooldown > 0 && retryAtLabel" class="text-sm text-muted-foreground">
            Следующий код можно запросить в {{ retryAtLabel }}
          </p>
          <button type="submit" class="btn-primary w-full" :disabled="loading || pin.length < 6">
            {{ loading ? 'Проверяем...' : 'Войти' }}
          </button>
          <button type="button" class="btn-ghost w-full text-muted-foreground" :disabled="loading || cooldown > 0" @click="sendPin">
            {{ cooldown > 0 ? `Отправить повторно через ${cooldown}с` : 'Отправить код заново' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
