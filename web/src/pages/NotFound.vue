<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Mountain } from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4">
    <div class="text-center">
      <Mountain class="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
      <h1 class="text-4xl font-bold text-slate-900 dark:text-white mb-2">404</h1>
      <p class="text-xl text-slate-500 dark:text-slate-400 mb-6">Page not found</p>
      <p class="text-slate-500 dark:text-slate-400 mb-8">
        Looks like you've wandered off the trail.
      </p>
      <RouterLink
        to="/"
        class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Return to Base Camp
      </RouterLink>
    </div>
  </div>
</template>
