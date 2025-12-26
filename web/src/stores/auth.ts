import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, adminApi } from '@/services/api'
import { useNotificationsStore } from '@/stores/notifications'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pendingReviewCount = ref(0)
  const isInitialized = ref(false)
  const initializePromise = ref<Promise<void> | null>(null)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => !!user.value?.is_staff)

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const { data } = await authApi.login(email, password)
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      await fetchUser()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Login failed'
      error.value = message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, password1: string, password2: string) {
    loading.value = true
    error.value = null

    try {
      await authApi.register(email, password1, password2)
      await login(email, password1)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Registration failed'
      error.value = message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    const notificationsStore = useNotificationsStore()
    try {
      await authApi.logout()
    } finally {
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      notificationsStore.reset()
      isInitialized.value = false
    }
  }

  async function fetchUser() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      user.value = null
      return
    }

    try {
      const { data } = await authApi.getUser()
      user.value = data

      // Initialize notifications for authenticated users
      const notificationsStore = useNotificationsStore()
      notificationsStore.initialize()

      // Fetch pending review count for admins
      if (data.is_staff) {
        await fetchPendingCount()
      }
    } catch {
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function fetchPendingCount() {
    if (!user.value?.is_staff) return
    try {
      const { data } = await adminApi.pendingCounts()
      pendingReviewCount.value = data.total
    } catch {
      // Silently fail - not critical
    }
  }

  async function initialize() {
    // Return existing promise if already initializing (prevents race conditions)
    if (initializePromise.value) {
      return initializePromise.value
    }
    // Skip if already initialized
    if (isInitialized.value) {
      return
    }

    initializePromise.value = fetchUser().finally(() => {
      isInitialized.value = true
      initializePromise.value = null
    })

    return initializePromise.value
  }

  async function updateProfile(data: { username?: string; bio?: string }) {
    loading.value = true
    error.value = null

    try {
      // Update username on user endpoint if provided
      if (data.username && data.username !== user.value?.username) {
        await authApi.updateUser({ username: data.username })
      }

      // Update bio on profile endpoint if provided
      if (data.bio !== undefined) {
        await authApi.updateProfile({ bio: data.bio })
      }

      // Refresh user data
      await fetchUser()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update profile'
      error.value = message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    pendingReviewCount,
    login,
    register,
    logout,
    fetchUser,
    fetchPendingCount,
    initialize,
    updateProfile,
  }
})
