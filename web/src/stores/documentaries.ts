import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentariesApi, taxonomyApi } from '@/services/api'
import type {
  Documentary,
  DocumentaryFilters,
  DocumentaryListItem,
  HeroDocumentary,
  Platform,
  Region,
  Sport,
  Theme,
} from '@/types'

export const useDocumentariesStore = defineStore('documentaries', () => {
  // State
  const documentaries = ref<DocumentaryListItem[]>([])
  const currentDocumentary = ref<Documentary | null>(null)
  const heroDocumentary = ref<HeroDocumentary | null>(null)
  const featured = ref<DocumentaryListItem[]>([])
  const topRated = ref<DocumentaryListItem[]>([])
  const recent = ref<DocumentaryListItem[]>([])
  const popular = ref<DocumentaryListItem[]>([])
  const themedCollections = ref<Record<string, DocumentaryListItem[]>>({})

  // Taxonomy
  const sports = ref<Sport[]>([])
  const themes = ref<Theme[]>([])
  const regions = ref<Region[]>([])
  const platforms = ref<Platform[]>([])

  // Pagination
  const totalCount = ref(0)
  const currentPage = ref(1)
  const hasNext = ref(false)
  const hasPrevious = ref(false)
  const currentFilters = ref<DocumentaryFilters>({})

  // Loading states
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchDocumentaries(filters?: DocumentaryFilters) {
    loading.value = true
    error.value = null
    currentPage.value = 1
    currentFilters.value = filters || {}

    try {
      const { data } = await documentariesApi.list(filters)
      documentaries.value = data.results
      totalCount.value = data.count
      hasNext.value = !!data.next
      hasPrevious.value = !!data.previous
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch documentaries'
    } finally {
      loading.value = false
    }
  }

  async function loadMoreDocumentaries() {
    if (!hasNext.value || loadingMore.value) return

    loadingMore.value = true
    error.value = null
    currentPage.value++

    try {
      const { data } = await documentariesApi.list({
        ...currentFilters.value,
        page: currentPage.value,
      })
      documentaries.value = [...documentaries.value, ...data.results]
      hasNext.value = !!data.next
      hasPrevious.value = !!data.previous
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load more documentaries'
      currentPage.value--
    } finally {
      loadingMore.value = false
    }
  }

  async function fetchDocumentary(slug: string) {
    loading.value = true
    error.value = null

    try {
      const { data } = await documentariesApi.get(slug)
      currentDocumentary.value = data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch documentary'
    } finally {
      loading.value = false
    }
  }

  async function fetchFeatured() {
    try {
      const { data } = await documentariesApi.featured()
      featured.value = data
    } catch {
      // Silently fail for featured
    }
  }

  async function fetchTopRated() {
    try {
      const { data } = await documentariesApi.topRated()
      topRated.value = data
    } catch {
      // Silently fail for top rated
    }
  }

  async function fetchRecent() {
    try {
      const { data } = await documentariesApi.recent()
      recent.value = data
    } catch {
      // Silently fail for recent
    }
  }

  async function fetchPopular() {
    try {
      const { data } = await documentariesApi.popular()
      popular.value = data
    } catch {
      // Silently fail for popular
    }
  }

  async function fetchByTheme(themeSlug: string) {
    try {
      const { data } = await documentariesApi.byTheme(themeSlug)
      themedCollections.value[themeSlug] = data
    } catch {
      // Silently fail for themed collection
    }
  }

  async function fetchBySport(sportSlug: string) {
    try {
      const { data } = await documentariesApi.bySport(sportSlug)
      themedCollections.value[`sport-${sportSlug}`] = data
    } catch {
      // Silently fail for sport collection
    }
  }

  async function fetchHero() {
    try {
      const { data } = await documentariesApi.hero()
      heroDocumentary.value = data
    } catch {
      // Silently fail for hero
    }
  }

  async function fetchTaxonomy() {
    try {
      const [sportsRes, themesRes, regionsRes, platformsRes] = await Promise.all([
        taxonomyApi.sports(),
        taxonomyApi.themes(),
        taxonomyApi.regions(),
        taxonomyApi.platforms(),
      ])
      sports.value = sportsRes.data
      themes.value = themesRes.data
      regions.value = regionsRes.data
      platforms.value = platformsRes.data
    } catch {
      // Silently fail for taxonomy
    }
  }

  async function toggleWatchlist(slug: string, isInWatchlist: boolean) {
    try {
      if (isInWatchlist) {
        await documentariesApi.removeFromWatchlist(slug)
      } else {
        await documentariesApi.addToWatchlist(slug)
      }

      // Update local state
      const updateItem = (item: DocumentaryListItem) => {
        if (item.slug === slug) {
          item.is_in_watchlist = !isInWatchlist
        }
        return item
      }

      documentaries.value = documentaries.value.map(updateItem)
      featured.value = featured.value.map(updateItem)
      topRated.value = topRated.value.map(updateItem)
      recent.value = recent.value.map(updateItem)
      popular.value = popular.value.map(updateItem)
      for (const key of Object.keys(themedCollections.value)) {
        const collection = themedCollections.value[key]
        if (collection) {
          themedCollections.value[key] = collection.map(updateItem)
        }
      }

      if (currentDocumentary.value?.slug === slug) {
        currentDocumentary.value.is_in_watchlist = !isInWatchlist
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update watchlist'
      throw err
    }
  }

  async function toggleWatched(slug: string, isWatched: boolean) {
    try {
      if (isWatched) {
        await documentariesApi.removeFromWatched(slug)
      } else {
        await documentariesApi.markAsWatched(slug)
      }

      // Update local state
      const updateItem = (item: DocumentaryListItem) => {
        if (item.slug === slug) {
          item.is_watched = !isWatched
        }
        return item
      }

      documentaries.value = documentaries.value.map(updateItem)
      featured.value = featured.value.map(updateItem)
      topRated.value = topRated.value.map(updateItem)
      recent.value = recent.value.map(updateItem)
      popular.value = popular.value.map(updateItem)
      for (const key of Object.keys(themedCollections.value)) {
        const collection = themedCollections.value[key]
        if (collection) {
          themedCollections.value[key] = collection.map(updateItem)
        }
      }

      if (currentDocumentary.value?.slug === slug) {
        currentDocumentary.value.is_watched = !isWatched
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update watched status'
      throw err
    }
  }

  async function toggleFavorite(slug: string, isFavorited: boolean) {
    try {
      if (isFavorited) {
        await documentariesApi.removeFromFavorites(slug)
      } else {
        await documentariesApi.addToFavorites(slug)
      }

      // Update local state
      const updateItem = (item: DocumentaryListItem) => {
        if (item.slug === slug) {
          item.is_favorited = !isFavorited
        }
        return item
      }

      documentaries.value = documentaries.value.map(updateItem)
      featured.value = featured.value.map(updateItem)
      topRated.value = topRated.value.map(updateItem)
      recent.value = recent.value.map(updateItem)
      popular.value = popular.value.map(updateItem)
      for (const key of Object.keys(themedCollections.value)) {
        const collection = themedCollections.value[key]
        if (collection) {
          themedCollections.value[key] = collection.map(updateItem)
        }
      }

      if (currentDocumentary.value?.slug === slug) {
        currentDocumentary.value.is_favorited = !isFavorited
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update favorites'
      throw err
    }
  }

  return {
    // State
    documentaries,
    currentDocumentary,
    heroDocumentary,
    featured,
    topRated,
    recent,
    popular,
    themedCollections,
    sports,
    themes,
    regions,
    platforms,
    totalCount,
    hasNext,
    hasPrevious,
    loading,
    loadingMore,
    error,

    // Actions
    fetchDocumentaries,
    loadMoreDocumentaries,
    fetchDocumentary,
    fetchFeatured,
    fetchTopRated,
    fetchRecent,
    fetchPopular,
    fetchByTheme,
    fetchBySport,
    fetchHero,
    fetchTaxonomy,
    toggleWatchlist,
    toggleWatched,
    toggleFavorite,
  }
})
