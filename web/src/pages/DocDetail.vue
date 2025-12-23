<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDocumentariesStore } from '@/stores/documentaries'
import { useAuthStore } from '@/stores/auth'
import {
  Star, Clock, Calendar, Play, ExternalLink,
  Bookmark, BookmarkCheck, MapPin
} from 'lucide-vue-next'

const props = defineProps<{ slug: string }>()

const docStore = useDocumentariesStore()
const authStore = useAuthStore()

const doc = computed(() => docStore.currentDocumentary)

const formatDuration = computed(() => {
  if (!doc.value) return ''
  const hours = Math.floor(doc.value.duration_minutes / 60)
  const minutes = doc.value.duration_minutes % 60
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
})

async function toggleWatchlist() {
  if (!doc.value || !authStore.isAuthenticated) return
  await docStore.toggleWatchlist(doc.value.slug, doc.value.is_in_watchlist)
}

onMounted(() => {
  docStore.fetchDocumentary(props.slug)
})
</script>

<template>
  <div v-if="docStore.loading" class="flex items-center justify-center min-h-[50vh]">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>

  <div v-else-if="doc">
    <!-- Backdrop -->
    <div class="relative h-[40vh] md:h-[50vh] bg-slate-900">
      <img
        v-if="doc.backdrop"
        :src="doc.backdrop"
        :alt="doc.title"
        class="w-full h-full object-cover opacity-50"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent"></div>
    </div>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-32 relative z-10 pb-16">
      <div class="flex flex-col md:flex-row gap-8">
        <!-- Poster -->
        <div class="flex-shrink-0">
          <div class="w-48 md:w-64 aspect-[2/3] bg-slate-700 rounded-lg overflow-hidden shadow-xl">
            <img
              v-if="doc.poster"
              :src="doc.poster"
              :alt="doc.title"
              class="w-full h-full object-cover"
            />
          </div>
        </div>

        <!-- Info -->
        <div class="flex-1">
          <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">
            {{ doc.title }}
          </h1>

          <p v-if="doc.original_title && doc.original_title !== doc.title" class="text-slate-400 mb-4">
            {{ doc.original_title }}
          </p>

          <!-- Meta -->
          <div class="flex flex-wrap items-center gap-4 text-slate-300 mb-6">
            <span class="flex items-center gap-1">
              <Calendar class="w-4 h-4" />
              {{ doc.year }}
            </span>
            <span class="flex items-center gap-1">
              <Clock class="w-4 h-4" />
              {{ formatDuration }}
            </span>
            <span v-if="doc.average_rating" class="flex items-center gap-1">
              <Star class="w-4 h-4 text-yellow-500 fill-yellow-500" />
              {{ doc.average_rating }} ({{ doc.review_count }} reviews)
            </span>
            <span v-if="doc.imdb_rating" class="flex items-center gap-1 text-yellow-400">
              IMDb {{ doc.imdb_rating }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap gap-3 mb-6">
            <a
              v-if="doc.trailer_url"
              :href="doc.trailer_url"
              target="_blank"
              class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Play class="w-4 h-4" />
              Watch Trailer
            </a>

            <button
              v-if="authStore.isAuthenticated"
              @click="toggleWatchlist"
              class="inline-flex items-center gap-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
            >
              <BookmarkCheck v-if="doc.is_in_watchlist" class="w-4 h-4" />
              <Bookmark v-else class="w-4 h-4" />
              {{ doc.is_in_watchlist ? 'In Watchlist' : 'Add to Watchlist' }}
            </button>
          </div>

          <!-- Synopsis -->
          <div class="prose prose-invert max-w-none mb-8">
            <p class="text-slate-300 leading-relaxed">{{ doc.synopsis }}</p>
          </div>

          <!-- Tags -->
          <div class="flex flex-wrap gap-2 mb-6">
            <RouterLink
              v-for="sport in doc.sports"
              :key="sport.id"
              :to="`/browse?sport=${sport.slug}`"
              class="px-3 py-1 bg-blue-600/20 text-blue-400 rounded-full text-sm hover:bg-blue-600/30"
            >
              {{ sport.name }}
            </RouterLink>
            <RouterLink
              v-for="theme in doc.themes"
              :key="theme.id"
              :to="`/browse?theme=${theme.slug}`"
              class="px-3 py-1 bg-slate-600/50 text-slate-300 rounded-full text-sm hover:bg-slate-600/70"
            >
              {{ theme.name }}
            </RouterLink>
          </div>

          <!-- Regions -->
          <div v-if="doc.regions.length" class="flex items-center gap-2 text-slate-400 mb-6">
            <MapPin class="w-4 h-4" />
            <span v-for="(region, i) in doc.regions" :key="region.id">
              {{ region.name }}<span v-if="i < doc.regions.length - 1">, </span>
            </span>
          </div>

          <!-- Directors -->
          <div v-if="doc.directors.length" class="text-slate-400 mb-6">
            <span class="text-slate-500">Directed by: </span>
            <span v-for="(director, i) in doc.directors" :key="director.id">
              {{ director.name }}<span v-if="i < doc.directors.length - 1">, </span>
            </span>
          </div>
        </div>
      </div>

      <!-- Where to Watch -->
      <section v-if="doc.availabilities.length" class="mt-12">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6">Where to Watch</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <a
            v-for="availability in doc.availabilities"
            :key="availability.id"
            :href="availability.url"
            target="_blank"
            class="flex items-center gap-4 p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-500 transition-colors"
          >
            <img
              v-if="availability.platform.logo"
              :src="availability.platform.logo"
              :alt="availability.platform.name"
              class="w-12 h-12 object-contain rounded"
            />
            <div class="flex-1">
              <p class="font-medium text-slate-900 dark:text-white">
                {{ availability.platform.name }}
              </p>
              <p class="text-sm text-slate-500">
                {{ availability.is_free ? 'Free' : 'Subscription' }}
              </p>
            </div>
            <ExternalLink class="w-5 h-5 text-slate-400" />
          </a>
        </div>
      </section>
    </div>
  </div>
</template>
