<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { watchlistApi } from '@/services/api'
import { Bookmark } from 'lucide-vue-next'
import DocCard from '@/components/docs/DocCard.vue'
import type { WatchlistItem } from '@/types'

const watchlist = ref<WatchlistItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await watchlistApi.list()
    watchlist.value = data.results
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center gap-3 mb-8">
      <Bookmark class="w-8 h-8 text-blue-600" />
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">My Watchlist</h1>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="watchlist.length === 0" class="text-center py-12">
      <Bookmark class="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
      <h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">Your watchlist is empty</h2>
      <p class="text-slate-500 dark:text-slate-400 mb-4">Start adding documentaries you want to watch later.</p>
      <RouterLink to="/browse" class="text-blue-600 hover:text-blue-700 font-medium">
        Browse documentaries
      </RouterLink>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
      <DocCard
        v-for="item in watchlist"
        :key="item.id"
        :documentary="item.documentary"
      />
    </div>
  </div>
</template>
