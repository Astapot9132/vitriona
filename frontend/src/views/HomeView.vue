<script setup lang="ts">
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background">
    <div class="space-y-4 text-center">
      <h1 class="text-4xl font-bold tracking-tight">New Vitriona</h1>
      <p class="text-lg text-muted-foreground">FastAPI + Vue 3 + PostgreSQL</p>
      <div class="flex justify-center gap-2">
        <RouterLink class="btn-primary" to="/client">Клиентский вход</RouterLink>
        <RouterLink class="btn-outline" to="/admin">Админка</RouterLink>
      </div>
    </div>
  </div>
</template>
