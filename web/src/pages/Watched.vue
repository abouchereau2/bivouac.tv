<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { watchedApi } from '@/services/api'
import { useLocalePath } from '@/composables/useLocalePath'
import { Eye } from 'lucide-vue-next'
import DocCard from '@/components/docs/DocCard.vue'
import type { WatchedItem } from '@/types'

const { t } = useI18n()
const { localePath } = useLocalePath()

const watched = ref<WatchedItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await watchedApi.list()
    watched.value = data.results
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center gap-3 mb-8">
      <Eye class="w-8 h-8 text-green-600" />
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">{{ t('watched.title') }}</h1>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>

    <div v-else-if="watched.length === 0" class="text-center py-12">
      <Eye class="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
      <h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">{{ t('watched.empty') }}</h2>
      <p class="text-slate-500 dark:text-slate-400 mb-4">{{ t('watched.emptyDescription') }}</p>
      <RouterLink :to="localePath('/browse')" class="text-green-600 hover:text-green-700 font-medium">
        {{ t('watched.browseButton') }}
      </RouterLink>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
      <DocCard
        v-for="item in watched"
        :key="item.id"
        :documentary="item.documentary"
      />
    </div>
  </div>
</template>
