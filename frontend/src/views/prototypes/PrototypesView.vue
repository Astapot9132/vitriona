<script setup>
const prototypes = [
  { slug: 'admin', name: 'Админка' },
  { slug: 'constructor', name: 'Конструктор витрин' },
  { slug: 'showcase-list', name: 'Список витрин' },
]
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-6 text-2xl font-semibold tracking-tight">Прототипы</h1>
    <div class="grid gap-4 sm:grid-cols-3">
      <a
        v-for="item in prototypes"
        :key="item.slug"
        class="card-base block p-5 transition-colors hover:bg-muted/40"
        :href="`/prototypes/${item.slug}/index.html`"
        target="_blank"
        rel="noreferrer"
      >
        <div class="text-sm font-medium">{{ item.name }}</div>
        <div class="mt-1 text-xs text-muted-foreground">{{ item.slug }}</div>
      </a>
    </div>
  </div>
</template>
