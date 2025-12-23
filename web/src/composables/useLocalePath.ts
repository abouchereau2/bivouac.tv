import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

/**
 * Composable to generate localized paths with the current language prefix.
 */
export function useLocalePath() {
  const route = useRoute()

  const currentLang = computed(() => (route.params.lang as string) || 'en')

  /**
   * Build a localized path with the current language prefix.
   * @param path - The path without language prefix (e.g., '/browse')
   * @returns The localized path (e.g., '/en/browse')
   */
  function localePath(path: string): string {
    // Handle root path
    if (path === '/' || path === '') {
      return `/${currentLang.value}`
    }
    // Ensure path starts with /
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    return `/${currentLang.value}${normalizedPath}`
  }

  /**
   * Build a localized route object for router-link :to prop.
   * @param to - Route name and optional params
   * @returns The route object with lang param
   */
  function localeRoute(to: { name: string; params?: Record<string, string>; query?: Record<string, string> }): RouteLocationRaw {
    return {
      name: to.name,
      params: { lang: currentLang.value, ...to.params },
      query: to.query,
    }
  }

  return {
    currentLang,
    localePath,
    localeRoute,
  }
}
