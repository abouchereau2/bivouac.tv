// API Types for Bivouac.tv

export interface Sport {
  id: number
  name: string
  slug: string
  icon?: string
}

export interface Theme {
  id: number
  name: string
  slug: string
}

export interface Region {
  id: number
  name: string
  slug: string
}

export interface Person {
  id: number
  name: string
  slug: string
  photo?: string
}

export interface Platform {
  id: number
  name: string
  slug: string
  logo?: string
  website?: string
  is_free: boolean
}

export interface Availability {
  id: number
  platform: Platform
  url: string
  is_free: boolean
  available_from?: string
  available_until?: string
  country_codes: string[]
}

export interface DocumentaryListItem {
  id: number
  title: string
  slug: string
  year: number
  duration_minutes: number
  poster?: string
  sports: Sport[]
  average_rating?: number
  review_count: number
  is_in_watchlist: boolean
  is_watched: boolean
  is_favorited: boolean
}

export interface HeroDocumentary {
  id: number
  title: string
  slug: string
  year: number
  duration_minutes: number
  synopsis: string
  backdrop?: string
  poster?: string
  sports: Sport[]
  themes: Theme[]
  average_rating?: number
}

export interface Documentary extends DocumentaryListItem {
  original_title?: string
  synopsis: string
  backdrop?: string
  trailer_url?: string
  directors: Person[]
  themes: Theme[]
  regions: Region[]
  imdb_id?: string
  imdb_rating?: number
  tmdb_id?: string
  availabilities: Availability[]
  created_at: string
  updated_at: string
}

export interface User {
  id: number
  email: string
  username: string
  first_name?: string
  last_name?: string
  is_staff: boolean
  profile?: UserProfile
  date_joined: string
}

export interface UserProfile {
  avatar?: string
  bio?: string
  favorite_sports: string[]
  created_at: string
}

export interface Review {
  id: number
  user: {
    id: number
    username: string
    avatar?: string
  }
  documentary: number
  documentary_title: string
  documentary_slug: string
  rating: number
  content?: string
  created_at: string
  updated_at: string
}

export interface Submission {
  id: number
  submitted_by: {
    id: number
    username: string
    avatar?: string
  }
  title: string
  year: number
  url: string
  notes?: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

export interface LinkSuggestion {
  id: number
  documentary: number
  documentary_title: string
  documentary_slug: string
  platform: Platform
  url: string
  is_free: boolean
  notes?: string
  submitted_by: {
    id: number
    username: string
    avatar?: string
  }
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

export interface LinkReport {
  id: number
  availability: number
  documentary_title: string
  documentary_slug: string
  platform_name: string
  availability_url: string
  reason: 'broken' | 'geo_restricted' | 'paywall' | 'wrong_content' | 'other'
  details?: string
  reported_by: {
    id: number
    username: string
    avatar?: string
  }
  status: 'pending' | 'fixed' | 'dismissed'
  created_at: string
}

export interface WatchlistItem {
  id: number
  documentary: DocumentaryListItem
  added_at: string
}

export interface WatchedItem {
  id: number
  documentary: DocumentaryListItem
  watched_at: string
}

export interface FavoriteItem {
  id: number
  documentary: DocumentaryListItem
  added_at: string
}

export type NotificationType =
  | 'submission_pending'
  | 'submission_approved'
  | 'submission_rejected'
  | 'link_suggestion_pending'
  | 'link_suggestion_approved'
  | 'link_suggestion_rejected'
  | 'link_report_pending'
  | 'link_report_fixed'
  | 'link_report_dismissed'

export type NotificationStatus = 'pending' | 'resolved'

export interface Notification {
  id: number
  notification_type: NotificationType
  status: NotificationStatus
  title: string
  message: string
  read: boolean
  read_at?: string
  created_at: string
  documentary_title?: string
  documentary_slug?: string
  documentary_poster?: string
}

// API Response types
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface AuthTokens {
  access: string
  refresh: string
}

// Filter types
export interface DocumentaryFilters {
  search?: string
  sport?: string
  theme?: string
  region?: string
  platform?: string
  year_min?: number
  year_max?: number
  duration_min?: number
  duration_max?: number
  is_free?: boolean
  is_featured?: boolean
  ordering?: string
  page?: number
}
