<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/AppLayout.vue'
import PinCodeInput from '@/components/PinCodeInput.vue'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const step = ref('email')
const email = ref('')
const pin = ref('')
const error = ref('')
const cooldown = ref(0)
let timerId = null

function startCooldown(seconds = 60) {
  window.clearInterval(timerId)
  cooldown.value = seconds
  timerId = window.setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      window.clearInterval(timerId)
      cooldown.value = 0
    }
  }, 1000)
}

async function sendPin() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/admin/login/send-pin', { email: email.value })
    if (data.redirect) {
      await auth.bootstrap(true)
      router.push('/admin/dashboard')
      return false
    }
    startCooldown()
    return true
  } catch (err) {
    const retry = err.response?.headers?.['retry-after']
    if (retry) startCooldown(Number(retry))
    error.value = err.response?.data?.detail || 'Ошибка при отправке кода.'
    return false
  } finally {
    loading.value = false
  }
}

async function submitEmail() {
  const ok = await sendPin()
  if (ok) step.value = 'pin'
}

async function submitPin() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/admin/login/verify-pin', { email: email.value, pin: pin.value })
    await auth.bootstrap(true)
    router.push(data.redirect === '/admin' ? '/admin/dashboard' : data.redirect)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка проверки кода.'
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
        <h1 class="text-2xl font-semibold tracking-tight">Vitriona Admin</h1>
      </div>

      <div class="card-base p-6">
        <form v-if="step === 'email'" class="space-y-4" @submit.prevent="submitEmail">
          <div>
            <h2 class="text-lg font-semibold">Вход для администратора</h2>
            <p class="mt-1 text-sm text-muted-foreground">Введите email</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">Email</label>
            <input v-model="email" type="email" class="input-base" placeholder="admin@example.com" :disabled="loading" required />
          </div>
          <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
          <button type="submit" class="btn-primary w-full" :disabled="loading || cooldown > 0">
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
