import type { RouteLocationRaw } from 'vue-router'

/**
 * Composable for path generation (French-only version).
 * Kept for backward compatibility - paths no longer need language prefix.
 */
export function useLocalePath() {
  /**
   * Return path as-is (no language prefix needed).
   */
  function localePath(path: string): string {
    // Handle root path
    if (path === '/' || path === '') {
      return '/'
    }
    // Ensure path starts with /
    return path.startsWith('/') ? path : `/${path}`
  }

  /**
   * Build a route object for router-link :to prop.
   */
  function localeRoute(to: { name: string; params?: Record<string, string>; query?: Record<string, string> }): RouteLocationRaw {
    return {
      name: to.name,
      params: to.params,
      query: to.query,
    }
  }

  return {
    localePath,
    localeRoute,
  }
}
