<script setup>
import { onMounted } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  timeout: {
    type: Number,
    default: 2200,
  },
})

const emit = defineEmits(['done'])

onMounted(() => {
  window.setTimeout(() => emit('done'), props.timeout)
})
</script>

<template>
  <div class="fixed left-1/2 top-4 z-50 -translate-x-1/2 rounded-md bg-foreground px-4 py-2 text-sm text-background shadow-lg">
    {{ message }}
  </div>
</template>
