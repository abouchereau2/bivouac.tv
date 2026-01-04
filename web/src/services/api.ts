import axios from 'axios'
import type {
  AuthTokens,
  Documentary,
  DocumentaryFilters,
  DocumentaryListItem,
  FavoriteItem,
  HeroDocumentary,
  LinkReport,
  LinkSuggestion,
  Notification,
  PaginatedResponse,
  Platform,
  Region,
  Review,
  Sport,
  Submission,
  Theme,
  User,
  WatchedItem,
  WatchlistItem,
} from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  // Add auth token
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  // French only
  config.headers['Accept-Language'] = 'fr'

  return config
})

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const { data } = await axios.post<AuthTokens>('/api/auth/token/refresh/', {
            refresh: refreshToken,
          })
          localStorage.setItem('access_token', data.access)
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)
        }
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post<AuthTokens>('/auth/login/', { email, password }),

  register: (email: string, password1: string, password2: string) =>
    api.post('/auth/registration/', { email, password1, password2 }),

  logout: () => api.post('/auth/logout/'),

  getUser: () => api.get<User>('/users/me/'),

  updateUser: (data: Partial<User>) => api.patch<User>('/users/me/', data),

  updateProfile: (data: { bio?: string }) =>
    api.patch<User['profile']>('/users/me/profile/', data),

  refreshToken: (refresh: string) =>
    api.post<AuthTokens>('/auth/token/refresh/', { refresh }),
}

// Documentaries API
export const documentariesApi = {
  list: (filters?: DocumentaryFilters) =>
    api.get<PaginatedResponse<DocumentaryListItem>>('/documentaries/', { params: filters }),

  get: (slug: string) => api.get<Documentary>(`/documentaries/${slug}/`),

  featured: () => api.get<DocumentaryListItem[]>('/documentaries/featured/'),

  topRated: () => api.get<DocumentaryListItem[]>('/documentaries/top_rated/'),

  recent: () => api.get<DocumentaryListItem[]>('/documentaries/recent/'),

  hero: () => api.get<HeroDocumentary | null>('/documentaries/hero/'),

  byTheme: (theme: string) =>
    api.get<DocumentaryListItem[]>('/documentaries/by_theme/', { params: { theme } }),

  bySport: (sport: string) =>
    api.get<DocumentaryListItem[]>('/documentaries/by_sport/', { params: { sport } }),

  popular: () => api.get<DocumentaryListItem[]>('/documentaries/popular/'),

  addToWatchlist: (slug: string) =>
    api.post(`/documentaries/${slug}/add_to_watchlist/`),

  removeFromWatchlist: (slug: string) =>
    api.delete(`/documentaries/${slug}/remove_from_watchlist/`),

  markAsWatched: (slug: string) =>
    api.post(`/documentaries/${slug}/mark_as_watched/`),

  removeFromWatched: (slug: string) =>
    api.delete(`/documentaries/${slug}/remove_from_watched/`),

  addToFavorites: (slug: string) =>
    api.post(`/documentaries/${slug}/add_to_favorites/`),

  removeFromFavorites: (slug: string) =>
    api.delete(`/documentaries/${slug}/remove_from_favorites/`),
}

// Taxonomy API
export const taxonomyApi = {
  sports: () => api.get<Sport[]>('/documentaries/sports/'),
  themes: () => api.get<Theme[]>('/documentaries/themes/'),
  regions: () => api.get<Region[]>('/documentaries/regions/'),
  platforms: () => api.get<Platform[]>('/documentaries/platforms/'),
}

// Watchlist API
export const watchlistApi = {
  list: () => api.get<PaginatedResponse<WatchlistItem>>('/documentaries/watchlist/'),
  add: (documentaryId: number) =>
    api.post('/documentaries/watchlist/', { documentary: documentaryId }),
  remove: (id: number) => api.delete(`/documentaries/watchlist/${id}/`),
}

// Watched API
export const watchedApi = {
  list: () => api.get<PaginatedResponse<WatchedItem>>('/documentaries/watched/'),
  add: (documentaryId: number) =>
    api.post('/documentaries/watched/', { documentary: documentaryId }),
  remove: (id: number) => api.delete(`/documentaries/watched/${id}/`),
}

// Favorites API
export const favoritesApi = {
  list: () => api.get<PaginatedResponse<FavoriteItem>>('/documentaries/favorites/'),
  add: (documentaryId: number) =>
    api.post('/documentaries/favorites/', { documentary: documentaryId }),
  remove: (id: number) => api.delete(`/documentaries/favorites/${id}/`),
}

// Reviews API
export const reviewsApi = {
  list: (documentarySlug?: string) =>
    api.get<PaginatedResponse<Review>>('/reviews/', {
      params: documentarySlug ? { documentary_slug: documentarySlug } : undefined,
    }),

  create: (data: { documentary: number; rating: number; content?: string }) =>
    api.post<Review>('/reviews/', data),

  update: (id: number, data: { rating: number; content?: string }) =>
    api.patch<Review>(`/reviews/${id}/`, data),

  delete: (id: number) => api.delete(`/reviews/${id}/`),
}

// Submissions API
export const submissionsApi = {
  list: () => api.get<PaginatedResponse<Submission>>('/submissions/'),

  create: (data: { title: string; year: number; url: string; notes?: string }) =>
    api.post<Submission>('/submissions/', data),

  get: (id: number) => api.get<Submission>(`/submissions/${id}/`),
}

// Link Suggestions API
export const linkSuggestionsApi = {
  list: () => api.get<PaginatedResponse<LinkSuggestion>>('/submissions/link-suggestions/'),

  create: (data: { documentary: number; platform: number; url: string; is_free: boolean; notes?: string }) =>
    api.post<LinkSuggestion>('/submissions/link-suggestions/', data),

  get: (id: number) => api.get<LinkSuggestion>(`/submissions/link-suggestions/${id}/`),
}

// Link Reports API
export const linkReportsApi = {
  list: () => api.get<PaginatedResponse<LinkReport>>('/submissions/link-reports/'),

  create: (data: { availability: number; reason: string; details?: string }) =>
    api.post<LinkReport>('/submissions/link-reports/', data),
}

// Notifications API
export const notificationsApi = {
  list: (params?: { read?: boolean; status?: 'pending' | 'resolved' }) =>
    api.get<PaginatedResponse<Notification>>('/notifications/', { params }),

  unreadCount: () => api.get<{ count: number }>('/notifications/unread_count/'),

  pendingCount: () => api.get<{ count: number }>('/notifications/pending_count/'),

  counts: () => api.get<{ unread: number; pending: number }>('/notifications/counts/'),

  markAsRead: (id: number) => api.post<Notification>(`/notifications/${id}/mark_as_read/`),

  markAllAsRead: () => api.post<{ updated: number }>('/notifications/mark_all_as_read/'),

  dismiss: (id: number) => api.delete(`/notifications/${id}/dismiss/`),
}

// Admin API (staff only)
export interface PendingCounts {
  submissions: number
  suggestions: number
  reports: number
  total: number
}

export const adminApi = {
  // Pending counts (lightweight)
  pendingCounts: () => api.get<PendingCounts>('/submissions/pending-counts/'),

  // Pending items
  pendingSubmissions: () => api.get<Submission[]>('/submissions/pending/'),
  pendingLinkSuggestions: () => api.get<LinkSuggestion[]>('/submissions/link-suggestions/pending/'),
  pendingLinkReports: () => api.get<LinkReport[]>('/submissions/link-reports/pending/'),

  // Submission actions
  approveSubmission: (id: number, notes?: string) =>
    api.post<Submission>(`/submissions/${id}/approve/`, { notes }),
  rejectSubmission: (id: number, notes?: string) =>
    api.post<Submission>(`/submissions/${id}/reject/`, { notes }),

  // Link suggestion actions
  approveLinkSuggestion: (id: number, notes?: string) =>
    api.post<LinkSuggestion>(`/submissions/link-suggestions/${id}/approve/`, { notes }),
  rejectLinkSuggestion: (id: number, notes?: string) =>
    api.post<LinkSuggestion>(`/submissions/link-suggestions/${id}/reject/`, { notes }),

  // Link report actions
  fixLinkReport: (id: number, notes?: string) =>
    api.post<LinkReport>(`/submissions/link-reports/${id}/fix/`, { notes }),
  dismissLinkReport: (id: number, notes?: string) =>
    api.post<LinkReport>(`/submissions/link-reports/${id}/dismiss/`, { notes }),
}

export default api
