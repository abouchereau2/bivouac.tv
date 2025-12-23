<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Star, Clock, Bookmark, BookmarkCheck } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useDocumentariesStore } from '@/stores/documentaries'
import type { DocumentaryListItem } from '@/types'

const props = defineProps<{
  documentary: DocumentaryListItem
}>()

const authStore = useAuthStore()
const docStore = useDocumentariesStore()

const formatDuration = computed(() => {
  const hours = Math.floor(props.documentary.duration_minutes / 60)
  const minutes = props.documentary.duration_minutes % 60
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
})

async function toggleWatchlist() {
  if (!authStore.isAuthenticated) return
  await docStore.toggleWatchlist(
    props.documentary.slug,
    props.documentary.is_in_watchlist
  )
}
</script>

<template>
  <div class="group relative">
    <RouterLink :to="`/doc/${documentary.slug}`" class="block">
      <!-- Poster -->
      <div class="aspect-[2/3] bg-slate-200 dark:bg-slate-700 rounded-lg overflow-hidden mb-3">
        <img
          v-if="documentary.poster"
          :src="documentary.poster"
          :alt="documentary.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-slate-400"
        >
          <span class="text-4xl">🎬</span>
        </div>
      </div>

      <!-- Info -->
      <h3 class="font-semibold text-slate-900 dark:text-white line-clamp-2 group-hover:text-blue-600 transition-colors">
        {{ documentary.title }}
      </h3>

      <div class="flex items-center gap-2 mt-1 text-sm text-slate-500 dark:text-slate-400">
        <span>{{ documentary.year }}</span>
        <span class="flex items-center gap-1">
          <Clock class="w-3 h-3" />
          {{ formatDuration }}
        </span>
      </div>

      <!-- Rating -->
      <div v-if="documentary.average_rating" class="flex items-center gap-1 mt-1">
        <Star class="w-4 h-4 text-yellow-500 fill-yellow-500" />
        <span class="text-sm font-medium text-slate-700 dark:text-slate-300">
          {{ documentary.average_rating }}
        </span>
        <span class="text-sm text-slate-500 dark:text-slate-400">
          ({{ documentary.review_count }})
        </span>
      </div>

      <!-- Sports tags -->
      <div v-if="documentary.sports.length" class="flex flex-wrap gap-1 mt-2">
        <span
          v-for="sport in documentary.sports.slice(0, 2)"
          :key="sport.id"
          class="text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full"
        >
          {{ sport.name }}
        </span>
      </div>
    </RouterLink>

    <!-- Watchlist button -->
    <button
      v-if="authStore.isAuthenticated"
      @click.prevent="toggleWatchlist"
      class="absolute top-2 right-2 p-2 bg-black/50 backdrop-blur rounded-full text-white hover:bg-black/70 transition-colors"
      :title="documentary.is_in_watchlist ? 'Remove from watchlist' : 'Add to watchlist'"
    >
      <BookmarkCheck v-if="documentary.is_in_watchlist" class="w-4 h-4" />
      <Bookmark v-else class="w-4 h-4" />
    </button>
  </div>
</template>
