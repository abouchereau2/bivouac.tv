<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDocumentariesStore } from '@/stores/documentaries'
import { useLocalizedName } from '@/composables/useLocalizedName'
import { Search, SlidersHorizontal, X, Loader2 } from 'lucide-vue-next'
import DocCard from '@/components/docs/DocCard.vue'
import type { DocumentaryFilters } from '@/types'

const { t } = useI18n()
const { getName } = useLocalizedName()
const route = useRoute()
const router = useRouter()
const docStore = useDocumentariesStore()

const showFilters = ref(false)
const searchQuery = ref('')
const filters = ref<DocumentaryFilters>({})
const loadMoreTrigger = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

function parseQueryParams() {
  const query = route.query
  filters.value = {
    search: query.search as string,
    sport: query.sport as string,
    theme: query.theme as string,
    region: query.region as string,
    platform: query.platform as string,
    year_min: query.year_min ? Number(query.year_min) : undefined,
    year_max: query.year_max ? Number(query.year_max) : undefined,
    duration_min: query.duration_min ? Number(query.duration_min) : undefined,
    duration_max: query.duration_max ? Number(query.duration_max) : undefined,
    is_free: query.is_free === 'true' ? true : undefined,
    is_featured: query.is_featured === 'true' ? true : undefined,
    ordering: (query.ordering as string) || '-year',
  }
  searchQuery.value = filters.value.search || ''
}

async function applyFilters() {
  const query: Record<string, string> = {}
  if (searchQuery.value) query.search = searchQuery.value
  if (filters.value.sport) query.sport = filters.value.sport
  if (filters.value.theme) query.theme = filters.value.theme
  if (filters.value.region) query.region = filters.value.region
  if (filters.value.platform) query.platform = filters.value.platform
  if (filters.value.year_min) query.year_min = String(filters.value.year_min)
  if (filters.value.year_max) query.year_max = String(filters.value.year_max)
  if (filters.value.duration_min) query.duration_min = String(filters.value.duration_min)
  if (filters.value.duration_max) query.duration_max = String(filters.value.duration_max)
  if (filters.value.is_free) query.is_free = 'true'
  if (filters.value.ordering) query.ordering = filters.value.ordering

  await router.push({ query })
}

function clearFilters() {
  searchQuery.value = ''
  filters.value = { ordering: '-year' }
  router.push({ query: {} })
}

function setupIntersectionObserver() {
  if (observer) observer.disconnect()

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting && docStore.hasNext && !docStore.loadingMore) {
        docStore.loadMoreDocumentaries()
      }
    },
    { rootMargin: '100px' }
  )

  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }
}

onMounted(() => {
  parseQueryParams()
  docStore.fetchDocumentaries(filters.value)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})

watch(() => route.query, () => {
  parseQueryParams()
  docStore.fetchDocumentaries(filters.value)
})

watch(
  () => [docStore.documentaries.length, loadMoreTrigger.value],
  () => {
    if (loadMoreTrigger.value) {
      setupIntersectionObserver()
    }
  }
)
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">
        {{ t('browse.title') }}
      </h1>

      <!-- Search -->
      <div class="flex gap-2">
        <div class="relative flex-1 md:w-80">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            v-model="searchQuery"
            @keyup.enter="applyFilters"
            type="text"
            :placeholder="t('browse.searchPlaceholder')"
            class="w-full pl-10 pr-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          @click="showFilters = !showFilters"
          class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700"
        >
          <SlidersHorizontal class="w-5 h-5 text-slate-600 dark:text-slate-300" />
        </button>
      </div>
    </div>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="bg-white dark:bg-slate-800 rounded-lg p-4 mb-8 border border-slate-200 dark:border-slate-700">
      <!-- Row 1: Category filters -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- Sport filter -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.sport') }}</label>
          <select
            v-model="filters.sport"
            class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
          >
            <option value="">{{ t('browse.filters.allSports') }}</option>
            <option v-for="sport in docStore.sports" :key="sport.id" :value="sport.slug">
              {{ getName(sport) }}
            </option>
          </select>
        </div>

        <!-- Theme filter -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.theme') }}</label>
          <select
            v-model="filters.theme"
            class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
          >
            <option value="">{{ t('browse.filters.allThemes') }}</option>
            <option v-for="theme in docStore.themes" :key="theme.id" :value="theme.slug">
              {{ getName(theme) }}
            </option>
          </select>
        </div>

        <!-- Region filter -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.region') }}</label>
          <select
            v-model="filters.region"
            class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
          >
            <option value="">{{ t('browse.filters.allRegions') }}</option>
            <option v-for="region in docStore.regions" :key="region.id" :value="region.slug">
              {{ getName(region) }}
            </option>
          </select>
        </div>

        <!-- Platform filter -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.platform') }}</label>
          <select
            v-model="filters.platform"
            class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
          >
            <option value="">{{ t('browse.filters.allPlatforms') }}</option>
            <option v-for="platform in docStore.platforms" :key="platform.id" :value="platform.slug">
              {{ platform.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Row 2: Year, Duration, Sort -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
        <!-- Year range -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.year') }}</label>
          <div class="flex gap-2">
            <input
              v-model.number="filters.year_min"
              type="number"
              :placeholder="t('browse.filters.from')"
              min="1900"
              max="2100"
              class="w-full px-2 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm"
            />
            <input
              v-model.number="filters.year_max"
              type="number"
              :placeholder="t('browse.filters.to')"
              min="1900"
              max="2100"
              class="w-full px-2 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm"
            />
          </div>
        </div>

        <!-- Duration range -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.duration') }}</label>
          <div class="flex gap-2">
            <input
              v-model.number="filters.duration_min"
              type="number"
              :placeholder="t('browse.filters.minDuration')"
              min="1"
              max="600"
              class="w-full px-2 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm"
            />
            <input
              v-model.number="filters.duration_max"
              type="number"
              :placeholder="t('browse.filters.maxDuration')"
              min="1"
              max="600"
              class="w-full px-2 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm"
            />
          </div>
        </div>

        <!-- Sort -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{{ t('browse.filters.sortBy') }}</label>
          <select
            v-model="filters.ordering"
            class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
          >
            <option value="-year">{{ t('browse.sort.newest') }}</option>
            <option value="year">{{ t('browse.sort.oldest') }}</option>
            <option value="-created_at">{{ t('browse.sort.recentlyAdded') }}</option>
            <option value="title">{{ t('browse.sort.titleAZ') }}</option>
            <option value="duration_minutes">{{ t('browse.sort.shortest') }}</option>
            <option value="-duration_minutes">{{ t('browse.sort.longest') }}</option>
          </select>
        </div>

        <!-- Free checkbox + spacer -->
        <div class="flex items-end">
          <label class="flex items-center gap-2 cursor-pointer pb-2">
            <input type="checkbox" v-model="filters.is_free" class="rounded" />
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('browse.filters.freeToWatch') }}</span>
          </label>
        </div>
      </div>

      <!-- Actions row -->
      <div class="flex items-center justify-end gap-4 mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
        <button
          @click="clearFilters"
          class="text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 flex items-center gap-1"
        >
          <X class="w-4 h-4" />
          {{ t('browse.filters.clearFilters') }}
        </button>

        <button
          @click="applyFilters"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {{ t('browse.filters.applyFilters') }}
        </button>
      </div>
    </div>

    <!-- Results -->
    <div v-if="docStore.loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
    </div>

    <div v-else-if="docStore.documentaries.length === 0" class="text-center py-12">
      <p class="text-slate-500 dark:text-slate-400">{{ t('browse.noResults') }}</p>
    </div>

    <div v-else>
      <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">
        {{ t('browse.resultsCount', { count: docStore.totalCount }) }}
      </p>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
        <DocCard
          v-for="doc in docStore.documentaries"
          :key="doc.id"
          :documentary="doc"
        />
      </div>

      <!-- Infinite scroll trigger -->
      <div
        ref="loadMoreTrigger"
        class="flex justify-center py-8"
      >
        <div v-if="docStore.loadingMore" class="flex items-center gap-2 text-slate-500">
          <Loader2 class="w-5 h-5 animate-spin" />
          <span>{{ t('browse.loadingMore') }}</span>
        </div>
        <p v-else-if="!docStore.hasNext && docStore.documentaries.length > 0" class="text-slate-400 text-sm">
          {{ t('browse.endOfResults') }}
        </p>
      </div>
    </div>
  </div>
</template>
