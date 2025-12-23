<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDocumentariesStore } from '@/stores/documentaries'
import { useLocalePath } from '@/composables/useLocalePath'
import { Search, Play, Star, Mountain, Clock, Info } from 'lucide-vue-next'
import DocCard from '@/components/docs/DocCard.vue'
import DocSlider from '@/components/docs/DocSlider.vue'

const { t } = useI18n()
const { localePath } = useLocalePath()
const docStore = useDocumentariesStore()

const hero = computed(() => docStore.heroDocumentary)

const hasHeroBackdrop = computed(() => !!hero.value?.backdrop)

const heroBackdropImage = computed(() => {
  if (!hero.value) return null
  return hero.value.backdrop || hero.value.poster
})

const formatDuration = computed(() => {
  if (!hero.value) return ''
  const hours = Math.floor(hero.value.duration_minutes / 60)
  const minutes = hero.value.duration_minutes % 60
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
})

// Themed collections config
const themedSections = [
  { key: 'survival', slug: 'survival' },
  { key: 'environment', slug: 'environment' },
  { key: 'expedition', slug: 'expedition' },
]

onMounted(async () => {
  // Fetch taxonomy first so we can access themes
  await docStore.fetchTaxonomy()

  await Promise.all([
    docStore.fetchHero(),
    docStore.fetchFeatured(),
    docStore.fetchTopRated(),
    docStore.fetchRecent(),
    docStore.fetchPopular(),
    // Fetch themed collections
    ...themedSections.map((section) => docStore.fetchByTheme(section.slug)),
  ])
})
</script>

<template>
  <div>
    <!-- Hero Section - JustWatch Style Full Bleed -->
    <section class="relative min-h-[70vh] md:min-h-[80vh] bg-slate-900 text-white overflow-hidden">
      <!-- Backdrop Image -->
      <div class="absolute inset-0">
        <img
          v-if="heroBackdropImage"
          :src="heroBackdropImage"
          :alt="hero?.title"
          class="w-full h-full object-cover"
          :class="[
            hasHeroBackdrop ? 'opacity-60' : 'opacity-40 blur-xl scale-105'
          ]"
        />
        <!-- Fallback gradient when no hero documentary -->
        <div
          v-else
          class="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900/50 to-slate-900"
        />
      </div>

      <!-- Gradient Overlays -->
      <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent"></div>
      <div class="absolute inset-0 bg-gradient-to-r from-slate-900/90 via-slate-900/50 to-transparent"></div>

      <!-- Content -->
      <div class="relative h-full min-h-[70vh] md:min-h-[80vh] flex items-end">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 md:pb-24 w-full">
          <!-- When we have a hero documentary -->
          <div v-if="hero" class="max-w-2xl">
              <!-- Sports Tags -->
              <div class="flex flex-wrap gap-2 mb-4">
                <span
                  v-for="sport in hero.sports.slice(0, 3)"
                  :key="sport.id"
                  class="px-3 py-1 bg-blue-500/90 text-white text-sm font-medium rounded-full backdrop-blur-sm"
                >
                  {{ sport.name }}
                </span>
              </div>

              <!-- Title -->
              <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 leading-tight tracking-tight">
                {{ hero.title }}
              </h1>

              <!-- Meta info -->
              <div class="flex items-center gap-4 text-slate-300 mb-5">
                <span class="text-lg font-medium">{{ hero.year }}</span>
                <span class="w-1 h-1 rounded-full bg-slate-400"></span>
                <span class="flex items-center gap-1.5">
                  <Clock class="w-4 h-4" />
                  {{ formatDuration }}
                </span>
                <span v-if="hero.average_rating" class="flex items-center gap-1.5">
                  <span class="w-1 h-1 rounded-full bg-slate-400"></span>
                  <Star class="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  {{ hero.average_rating.toFixed(1) }}
                </span>
              </div>

              <!-- Synopsis -->
              <p class="text-slate-200 mb-8 line-clamp-3 text-lg leading-relaxed max-w-xl">
                {{ hero.synopsis }}
              </p>

              <!-- CTA Buttons -->
              <div class="flex flex-col sm:flex-row gap-3">
                <RouterLink
                  :to="localePath(`/doc/${hero.slug}`)"
                  class="inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-white text-slate-900 rounded-lg hover:bg-slate-100 transition-all font-semibold shadow-xl hover:shadow-2xl hover:scale-[1.02]"
                >
                  <Info class="w-5 h-5" />
                  {{ t('home.moreInfo') }}
                </RouterLink>
                <RouterLink
                  :to="localePath('/browse')"
                  class="inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all font-semibold backdrop-blur-md border border-white/20"
                >
                  <Search class="w-5 h-5" />
                  {{ t('home.browseDocs') }}
                </RouterLink>
              </div>
            </div>

          <!-- Fallback when no hero documentary -->
          <div v-else class="text-center w-full">
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
        </div>
      </div>
    </section>

    <!-- Brand Statement -->
    <section class="py-12 md:py-16 bg-slate-900 border-t border-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="flex items-center justify-center gap-3 mb-4">
          <Mountain class="w-10 h-10 text-blue-400" />
          <span class="text-2xl font-bold text-white">Bivouac.tv</span>
        </div>
        <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-3">
          {{ t('home.heroTitle1') }}<br>
          <span class="text-blue-400">{{ t('home.heroTitle2') }}</span>
        </h2>
        <p class="text-slate-400 text-sm md:text-base max-w-md mx-auto">
          {{ t('home.heroSubtitle') }}
        </p>
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

    <!-- Recently Added Section (index 0 = blue/dark) -->
    <section class="py-12 bg-white dark:bg-slate-900" v-if="docStore.recent.length">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <DocSlider
          :title="t('home.recentlyAdded')"
          :documentaries="docStore.recent"
          :view-all-link="localePath('/browse') + '?ordering=-created_at'"
        />
      </div>
    </section>

    <!-- Popular Section (index 1 = grey) -->
    <section class="py-12 bg-slate-50 dark:bg-slate-800" v-if="docStore.popular.length">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <DocSlider
          :title="t('home.popular')"
          :documentaries="docStore.popular"
          :view-all-link="localePath('/browse')"
        />
      </div>
    </section>

    <!-- Themed Sliders (index 2, 3, 4... alternating from blue) -->
    <template v-for="(section, index) in themedSections" :key="section.key">
      <section
        v-if="docStore.themedCollections[section.slug]?.length"
        class="py-12"
        :class="index % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-slate-50 dark:bg-slate-800'"
      >
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <DocSlider
            :title="t(`home.themes.${section.key}`)"
            :documentaries="docStore.themedCollections[section.slug] ?? []"
            :view-all-link="localePath('/browse') + `?theme=${section.slug}`"
          />
        </div>
      </section>
    </template>

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
