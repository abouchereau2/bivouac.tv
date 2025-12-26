import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsApi } from '@/services/api'
import type { Notification, NotificationStatus } from '@/types'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const pendingCount = ref(0)
  const loading = ref(false)
  const isInitialized = ref(false)
  const currentStatusFilter = ref<NotificationStatus | undefined>(undefined)

  const hasUnread = computed(() => unreadCount.value > 0)
  const hasPending = computed(() => pendingCount.value > 0)

  async function fetchNotifications(status?: NotificationStatus) {
    loading.value = true
    currentStatusFilter.value = status
    try {
      const { data } = await notificationsApi.list(status ? { status } : undefined)
      notifications.value = data.results
    } catch {
      // Silently fail - not critical
    } finally {
      loading.value = false
      isInitialized.value = true
    }
  }

  async function fetchUnreadCount() {
    try {
      const { data } = await notificationsApi.unreadCount()
      unreadCount.value = data.count
    } catch {
      // Silently fail - not critical
    }
  }

  async function fetchPendingCount() {
    try {
      const { data } = await notificationsApi.pendingCount()
      pendingCount.value = data.count
    } catch {
      // Silently fail - not critical
    }
  }

  async function markAsRead(notificationId: number) {
    try {
      const { data } = await notificationsApi.markAsRead(notificationId)
      // Update the notification in the list
      const index = notifications.value.findIndex((n) => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index] = data
      }
      // Decrement unread count if it was unread
      if (!notifications.value[index]?.read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch {
      // Silently fail
    }
  }

  async function markAllAsRead() {
    try {
      await notificationsApi.markAllAsRead()
      // Update all notifications locally
      notifications.value = notifications.value.map((n) => ({
        ...n,
        read: true,
        read_at: new Date().toISOString(),
      }))
      unreadCount.value = 0
    } catch {
      // Silently fail
    }
  }

  async function dismissNotification(notificationId: number) {
    try {
      await notificationsApi.dismiss(notificationId)
      // Remove from list
      notifications.value = notifications.value.filter((n) => n.id !== notificationId)
      // Update unread count if it was unread
      const wasUnread = notifications.value.find((n) => n.id === notificationId)?.read === false
      if (wasUnread) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch {
      // Silently fail
    }
  }

  async function initialize() {
    if (isInitialized.value) return
    await Promise.all([fetchNotifications(), fetchUnreadCount(), fetchPendingCount()])
  }

  function reset() {
    notifications.value = []
    unreadCount.value = 0
    pendingCount.value = 0
    isInitialized.value = false
    currentStatusFilter.value = undefined
  }

  return {
    notifications,
    unreadCount,
    pendingCount,
    loading,
    isInitialized,
    currentStatusFilter,
    hasUnread,
    hasPending,
    fetchNotifications,
    fetchUnreadCount,
    fetchPendingCount,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    initialize,
    reset,
  }
})
