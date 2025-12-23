<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Mountain } from 'lucide-vue-next'
import { useLocalePath } from '@/composables/useLocalePath'

const { t } = useI18n()
const { localePath } = useLocalePath()
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4">
    <div class="text-center">
      <Mountain class="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
      <h1 class="text-4xl font-bold text-slate-900 dark:text-white mb-2">{{ t('notFound.code') }}</h1>
      <p class="text-xl text-slate-500 dark:text-slate-400 mb-6">{{ t('notFound.title') }}</p>
      <p class="text-slate-500 dark:text-slate-400 mb-8">
        {{ t('notFound.description') }}
      </p>
      <RouterLink
        :to="localePath('/')"
        class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        {{ t('notFound.homeButton') }}
      </RouterLink>
    </div>
  </div>
</template>
