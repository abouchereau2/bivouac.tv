<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { setLocale, type SupportedLocale, SUPPORTED_LOCALES } from '@/i18n'

const route = useRoute()
const { locale } = useI18n()

// Sync locale with route param
watch(
  () => route.params.lang,
  (lang) => {
    if (lang && SUPPORTED_LOCALES.includes(lang as SupportedLocale)) {
      setLocale(lang as SupportedLocale)
    }
  },
  { immediate: true }
)

// Update HTML lang attribute
watch(
  locale,
  (newLocale) => {
    document.documentElement.lang = newLocale
  },
  { immediate: true }
)
</script>

<template>
  <RouterView />
</template>
