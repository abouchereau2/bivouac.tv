<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import DocCard from './DocCard.vue'
import type { DocumentaryListItem } from '@/types'

const { t } = useI18n()

const props = defineProps<{
  title: string
  documentaries: DocumentaryListItem[]
  viewAllLink?: string
  icon?: unknown
}>()

const sliderRef = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)

const cardWidth = computed(() => {
  // Card width + gap (responsive)
  if (typeof window !== 'undefined') {
    if (window.innerWidth < 640) return 160 + 16 // mobile
    if (window.innerWidth < 1024) return 180 + 20 // tablet
    return 200 + 24 // desktop
  }
  return 200 + 24
})

function updateScrollButtons() {
  if (!sliderRef.value) return
  const { scrollLeft, scrollWidth, clientWidth } = sliderRef.value
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth - 10
}

function scroll(direction: 'left' | 'right') {
  if (!sliderRef.value) return
  const scrollAmount = cardWidth.value * 3
  sliderRef.value.scrollBy({
    left: direction === 'left' ? -scrollAmount : scrollAmount,
    behavior: 'smooth',
  })
}

onMounted(() => {
  if (sliderRef.value) {
    sliderRef.value.addEventListener('scroll', updateScrollButtons)
    window.addEventListener('resize', updateScrollButtons)
    updateScrollButtons()
  }
})

onUnmounted(() => {
  if (sliderRef.value) {
    sliderRef.value.removeEventListener('scroll', updateScrollButtons)
  }
  window.removeEventListener('resize', updateScrollButtons)
})
</script>

<template>
  <div class="relative group/slider">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
        <component :is="icon" v-if="icon" class="w-6 h-6" />
        {{ title }}
      </h2>
      <RouterLink
        v-if="viewAllLink"
        :to="viewAllLink"
        class="text-blue-600 hover:text-blue-700 font-medium text-sm md:text-base"
      >
        {{ t('common.viewAll') }}
      </RouterLink>
    </div>

    <!-- Slider container -->
    <div class="relative">
      <!-- Left scroll button -->
      <button
        v-show="canScrollLeft"
        @click="scroll('left')"
        class="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 md:w-12 md:h-12 bg-white/90 dark:bg-slate-800/90 backdrop-blur rounded-full shadow-lg flex items-center justify-center text-slate-700 dark:text-white hover:bg-white dark:hover:bg-slate-700 transition-all opacity-0 group-hover/slider:opacity-100 -translate-x-1/2"
        aria-label="Scroll left"
      >
        <ChevronLeft class="w-5 h-5 md:w-6 md:h-6" />
      </button>

      <!-- Scrollable content -->
      <div
        ref="sliderRef"
        class="flex gap-4 md:gap-5 lg:gap-6 overflow-x-auto scrollbar-hide scroll-smooth pb-2 -mx-4 px-4 md:-mx-6 md:px-6 lg:-mx-8 lg:px-8"
      >
        <div
          v-for="doc in documentaries"
          :key="doc.id"
          class="flex-shrink-0 w-[160px] sm:w-[180px] lg:w-[200px]"
        >
          <DocCard :documentary="doc" />
        </div>
      </div>

      <!-- Right scroll button -->
      <button
        v-show="canScrollRight"
        @click="scroll('right')"
        class="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 md:w-12 md:h-12 bg-white/90 dark:bg-slate-800/90 backdrop-blur rounded-full shadow-lg flex items-center justify-center text-slate-700 dark:text-white hover:bg-white dark:hover:bg-slate-700 transition-all opacity-0 group-hover/slider:opacity-100 translate-x-1/2"
        aria-label="Scroll right"
      >
        <ChevronRight class="w-5 h-5 md:w-6 md:h-6" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
