<script setup lang="ts">
import type { ComponentPublicInstance } from 'vue'
import { nextTick, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  disabled?: boolean
  modelValue?: string
}>(), {
  disabled: false,
  modelValue: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  complete: [value: string]
}>()

const digits = ref<string[]>(Array.from({ length: 6 }, (_, index) => props.modelValue[index] || ''))
const refs = ref<Array<HTMLInputElement | null>>([])

function setInputRef(index: number, element: Element | ComponentPublicInstance | null): void {
  refs.value[index] = element instanceof HTMLInputElement ? element : null
}

watch(
  () => props.modelValue,
  (value) => {
    digits.value = Array.from({ length: 6 }, (_, index) => value[index] || '')
  },
)

onMounted(() => {
  refs.value[0]?.focus()
})

function updateValue(): void {
  const pin = digits.value.join('')
  emit('update:modelValue', pin)
  if (pin.length === 6 && !digits.value.includes('')) {
    emit('complete', pin)
  }
}

function handleChange(index: number, event: Event): void {
  const value = (event.target as HTMLInputElement).value
  const digit = value.replace(/\D/g, '').slice(-1)
  digits.value[index] = digit
  updateValue()
  if (digit && index < 5) {
    nextTick(() => refs.value[index + 1]?.focus())
  }
}

function handleKeyDown(index: number, event: KeyboardEvent): void {
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    refs.value[index - 1]?.focus()
  }
  if (event.key === 'ArrowLeft' && index > 0) {
    refs.value[index - 1]?.focus()
  }
  if (event.key === 'ArrowRight' && index < 5) {
    refs.value[index + 1]?.focus()
  }
}

function handlePaste(event: ClipboardEvent): void {
  event.preventDefault()
  const pasted = event.clipboardData?.getData('text').replace(/\D/g, '').slice(0, 6) || ''
  if (!pasted) return
  digits.value = Array.from({ length: 6 }, (_, index) => pasted[index] || '')
  updateValue()
  const focusIndex = Math.min(pasted.length, 5)
  refs.value[focusIndex]?.focus()
}
</script>

<template>
  <div class="flex justify-center gap-2">
    <input
      v-for="(_, index) in digits"
      :key="index"
      :ref="(element) => setInputRef(index, element)"
      :value="digits[index]"
      type="text"
      inputmode="numeric"
      maxlength="1"
      :disabled="disabled"
      class="h-12 w-10 rounded-md border border-input bg-background text-center text-lg font-semibold text-foreground"
      @input="handleChange(index, $event)"
      @keydown="handleKeyDown(index, $event)"
      @paste="handlePaste"
    />
  </div>
</template>
