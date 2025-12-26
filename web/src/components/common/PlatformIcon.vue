<script setup lang="ts">
import { computed } from 'vue'
import { Tv } from 'lucide-vue-next'
import {
  siNetflix,
  siYoutube,
  siVimeo,
  siAppletv,
  siMax,
  siHbo,
  siParamountplus,
  siCrunchyroll,
  siDailymotion,
  siTubi,
  siPlex,
  siGoogletv,
  siItvx,
  siThemoviedatabase,
} from 'simple-icons'

const props = defineProps<{
  slug: string
  name: string
  logo?: string
  size?: number
}>()

// Map platform slugs to Simple Icons
const platformIconMap: Record<string, { svg: string; hex: string }> = {
  netflix: { svg: siNetflix.svg, hex: siNetflix.hex },
  youtube: { svg: siYoutube.svg, hex: siYoutube.hex },
  vimeo: { svg: siVimeo.svg, hex: siVimeo.hex },
  'apple-tv': { svg: siAppletv.svg, hex: siAppletv.hex },
  'apple-tv-plus': { svg: siAppletv.svg, hex: siAppletv.hex },
  appletv: { svg: siAppletv.svg, hex: siAppletv.hex },
  max: { svg: siMax.svg, hex: siMax.hex },
  hbo: { svg: siHbo.svg, hex: siHbo.hex },
  'hbo-max': { svg: siMax.svg, hex: siMax.hex },
  'paramount-plus': { svg: siParamountplus.svg, hex: siParamountplus.hex },
  paramountplus: { svg: siParamountplus.svg, hex: siParamountplus.hex },
  crunchyroll: { svg: siCrunchyroll.svg, hex: siCrunchyroll.hex },
  dailymotion: { svg: siDailymotion.svg, hex: siDailymotion.hex },
  tubi: { svg: siTubi.svg, hex: siTubi.hex },
  plex: { svg: siPlex.svg, hex: siPlex.hex },
  'google-tv': { svg: siGoogletv.svg, hex: siGoogletv.hex },
  itvx: { svg: siItvx.svg, hex: siItvx.hex },
  tmdb: { svg: siThemoviedatabase.svg, hex: siThemoviedatabase.hex },
}

const iconSize = computed(() => props.size ?? 24)

// Priority: 1) Platform logo from backend, 2) Simple Icons, 3) Generic TV icon
const hasBackendLogo = computed(() => !!props.logo)

const platformIcon = computed(() => {
  const normalizedSlug = props.slug.toLowerCase()
  return platformIconMap[normalizedSlug] || null
})

const iconStyle = computed(() => {
  if (!platformIcon.value) return {}
  return {
    width: `${iconSize.value}px`,
    height: `${iconSize.value}px`,
    color: `#${platformIcon.value.hex}`,
  }
})
</script>

<template>
  <!-- Priority 1: Backend logo -->
  <img
    v-if="hasBackendLogo"
    :src="logo"
    :alt="name"
    :width="iconSize"
    :height="iconSize"
    class="platform-logo"
  />
  <!-- Priority 2: Simple Icons -->
  <div
    v-else-if="platformIcon"
    class="platform-icon"
    :style="iconStyle"
    v-html="platformIcon.svg"
    :aria-label="name"
  />
  <!-- Priority 3: Generic TV icon -->
  <Tv
    v-else
    :size="iconSize"
    class="text-slate-400"
    :aria-label="name"
  />
</template>

<style scoped>
.platform-logo {
  object-fit: contain;
}

.platform-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.platform-icon :deep(svg) {
  width: 100%;
  height: 100%;
  fill: currentColor;
}
</style>
