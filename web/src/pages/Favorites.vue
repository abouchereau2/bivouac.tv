<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { favoritesApi } from '@/services/api'
import { useLocalePath } from '@/composables/useLocalePath'
import { Heart } from 'lucide-vue-next'
import DocCard from '@/components/docs/DocCard.vue'
import type { FavoriteItem } from '@/types'

const { t } = useI18n()
const { localePath } = useLocalePath()

const favorites = ref<FavoriteItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await favoritesApi.list()
    favorites.value = data.results
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center gap-3 mb-8">
      <Heart class="w-8 h-8 text-red-500" />
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">{{ t('favorites.title') }}</h1>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
    </div>

    <div v-else-if="favorites.length === 0" class="text-center py-12">
      <Heart class="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
      <h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">{{ t('favorites.empty') }}</h2>
      <p class="text-slate-500 dark:text-slate-400 mb-4">{{ t('favorites.emptyDescription') }}</p>
      <RouterLink :to="localePath('/browse')" class="text-red-500 hover:text-red-600 font-medium">
        {{ t('favorites.browseButton') }}
      </RouterLink>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
      <DocCard
        v-for="item in favorites"
        :key="item.id"
        :documentary="item.documentary"
      />
    </div>
  </div>
</template>
