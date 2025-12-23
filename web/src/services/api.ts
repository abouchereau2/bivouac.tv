import axios from 'axios'
import type {
  AuthTokens,
  Documentary,
  DocumentaryFilters,
  DocumentaryListItem,
  PaginatedResponse,
  Platform,
  Region,
  Review,
  Sport,
  Submission,
  Theme,
  User,
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
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
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

  addToWatchlist: (slug: string) =>
    api.post(`/documentaries/${slug}/add_to_watchlist/`),

  removeFromWatchlist: (slug: string) =>
    api.delete(`/documentaries/${slug}/remove_from_watchlist/`),
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

export default api
