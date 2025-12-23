<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDocumentariesStore } from '@/stores/documentaries'
import { useLocalePath } from '@/composables/useLocalePath'
import { Search, Play, Star, Mountain } from 'lucide-vue-next'
import DocCard from '@/components/docs/DocCard.vue'

const { t } = useI18n()
const { localePath } = useLocalePath()
const docStore = useDocumentariesStore()

onMounted(async () => {
  await Promise.all([
    docStore.fetchFeatured(),
    docStore.fetchTopRated(),
    docStore.fetchRecent(),
  ])
})
</script>

<template>
  <div>
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-24">
      <div class="absolute inset-0 bg-[url('/mountain-bg.jpg')] bg-cover bg-center opacity-20"></div>
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="flex justify-center mb-6">
          <Mountain class="w-16 h-16 text-blue-400" />
        </div>
        <h1 class="text-4xl md:text-6xl font-bold mb-6">
          {{ t('home.heroTitle1') }}<br>
          <span class="text-blue-400">{{ t('home.heroTitle2') }}</span>
        </h1>
        <p class="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
          {{ t('home.heroSubtitle') }}
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <RouterLink
            :to="localePath('/browse')"
            class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            <Search class="w-5 h-5" />
            {{ t('home.browseDocs') }}
          </RouterLink>
          <RouterLink
            :to="localePath('/browse') + '?is_free=true'"
            class="inline-flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors font-semibold backdrop-blur"
          >
            <Play class="w-5 h-5" />
            {{ t('home.watchFree') }}
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Featured Section -->
    <section class="py-16 bg-white dark:bg-slate-900" v-if="docStore.featured.length">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Star class="w-6 h-6 text-yellow-500" />
            {{ t('home.featured') }}
          </h2>
          <RouterLink
            :to="localePath('/browse') + '?is_featured=true'"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            {{ t('common.viewAll') }}
          </RouterLink>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <DocCard
            v-for="doc in docStore.featured"
            :key="doc.id"
            :documentary="doc"
          />
        </div>
      </div>
    </section>

    <!-- Top Rated Section -->
    <section class="py-16 bg-slate-50 dark:bg-slate-800" v-if="docStore.topRated.length">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">
            {{ t('home.topRated') }}
          </h2>
          <RouterLink
            :to="localePath('/browse') + '?ordering=-average_rating'"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            {{ t('common.viewAll') }}
          </RouterLink>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <DocCard
            v-for="doc in docStore.topRated"
            :key="doc.id"
            :documentary="doc"
          />
        </div>
      </div>
    </section>

    <!-- Recently Added Section -->
    <section class="py-16 bg-white dark:bg-slate-900" v-if="docStore.recent.length">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">
            {{ t('home.recentlyAdded') }}
          </h2>
          <RouterLink
            :to="localePath('/browse') + '?ordering=-created_at'"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            {{ t('common.viewAll') }}
          </RouterLink>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <DocCard
            v-for="doc in docStore.recent"
            :key="doc.id"
            :documentary="doc"
          />
        </div>
      </div>
    </section>

    <!-- Sports Categories -->
    <section class="py-16 bg-slate-50 dark:bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8 text-center">
          {{ t('home.browseBySport') }}
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <RouterLink
            v-for="sport in docStore.sports.slice(0, 8)"
            :key="sport.id"
            :to="localePath('/browse') + `?sport=${sport.slug}`"
            class="p-6 bg-white dark:bg-slate-700 rounded-xl shadow-sm hover:shadow-md transition-shadow text-center"
          >
            <span class="text-lg font-semibold text-slate-900 dark:text-white">
              {{ sport.name }}
            </span>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-blue-600 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl font-bold mb-4">{{ t('home.submitCta') }}</h2>
        <p class="text-blue-100 mb-8 max-w-2xl mx-auto">
          {{ t('home.submitCtaDescription') }}
        </p>
        <RouterLink
          :to="localePath('/submit')"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-semibold"
        >
          {{ t('home.submitButton') }}
        </RouterLink>
      </div>
    </section>
  </div>
</template>
