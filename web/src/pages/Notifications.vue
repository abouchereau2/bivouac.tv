<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotificationsStore } from '@/stores/notifications'
import { useLocalePath } from '@/composables/useLocalePath'
import { Bell, Trash2, ExternalLink, CheckCheck, Clock, CheckCircle } from 'lucide-vue-next'
import type { NotificationStatus, Notification } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || ''

const { t, te } = useI18n()
const { localePath } = useLocalePath()
const router = useRouter()
const notificationsStore = useNotificationsStore()

const loading = computed(() => notificationsStore.loading)
const notifications = computed(() => notificationsStore.notifications)
const activeTab = ref<'all' | NotificationStatus>('all')

function getNotificationTitle(notification: Notification) {
  const titleKey = `notifications.titles.${notification.notification_type}`
  if (te(titleKey)) {
    return t(titleKey, { title: notification.documentary_title || t('notifications.unknownDoc') })
  }
  return notification.title
}

function getNotificationStatus(type: string) {
  // Pending notifications (awaiting review)
  if (type.includes('_pending')) return 'pending'
  // Positive outcomes
  if (type.includes('approved') || type.includes('fixed')) return 'success'
  // Negative/neutral outcomes
  if (type.includes('rejected') || type.includes('dismissed')) return 'neutral'
  return 'default'
}

async function switchTab(tab: 'all' | NotificationStatus) {
  activeTab.value = tab
  if (tab === 'all') {
    await notificationsStore.fetchNotifications()
  } else {
    await notificationsStore.fetchNotifications(tab)
  }
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function handleNotificationClick(notification: Notification) {
  if (!notification.read) {
    await notificationsStore.markAsRead(notification.id)
  }
  if (notification.documentary_slug) {
    router.push(localePath(`/doc/${notification.documentary_slug}`))
  }
}

function getTypeLabel(type: string) {
  if (type.startsWith('submission_')) return t('notifications.typeLabels.submission')
  if (type.startsWith('link_suggestion_')) return t('notifications.typeLabels.linkSuggestion')
  if (type.startsWith('link_report_')) return t('notifications.typeLabels.linkReport')
  return ''
}

function getStatusLabel(type: string) {
  if (type.includes('_pending')) return t('notifications.statusLabels.pending')
  if (type.includes('approved') || type.includes('fixed')) return t('notifications.statusLabels.approved')
  if (type.includes('rejected') || type.includes('dismissed')) return t('notifications.statusLabels.rejected')
  return ''
}

function getPosterUrl(url: string | undefined) {
  if (!url) return ''
  // If it's already absolute, return as-is
  if (url.startsWith('http')) return url
  // Media files are served at root /media/, not under /api/
  // API_BASE is like '/api' or 'http://localhost:8000/api', we need the origin only
  const origin = API_BASE.replace(/\/api\/?$/, '')
  return `${origin}${url}`
}

// Default messages that we don't need to show (they're generic)
const DEFAULT_MESSAGES = [
  'Your documentary suggestion has been received and is awaiting moderation.',
  'Your documentary suggestion has been added to the database.',
  'Thank you for your suggestion.',
  'Your streaming link suggestion has been received and is awaiting moderation.',
  'The streaming link has been added.',
  'Your link report has been received and is awaiting moderation.',
  'The broken link has been removed. Thank you for reporting!',
  'After review, the link appears to be working.',
]

function hasCustomMessage(notification: Notification) {
  if (!notification.message) return false
  // Only show if it's not a default message (i.e., admin added custom notes)
  return !DEFAULT_MESSAGES.includes(notification.message)
}

onMounted(() => {
  notificationsStore.fetchNotifications()
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-3">
        <Bell class="w-8 h-8 text-blue-600" />
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">{{ t('notifications.title') }}</h1>
      </div>

      <button
        v-if="notificationsStore.hasUnread"
        @click="notificationsStore.markAllAsRead()"
        class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
      >
        <CheckCheck class="w-4 h-4" />
        {{ t('notifications.markAllRead') }}
      </button>
    </div>

    <!-- Status filter tabs -->
    <div class="flex gap-2 mb-6">
      <button
        @click="switchTab('all')"
        class="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors"
        :class="activeTab === 'all'
          ? 'bg-blue-600 text-white'
          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
      >
        {{ t('notifications.filterAll') }}
      </button>
      <button
        @click="switchTab('pending')"
        class="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors"
        :class="activeTab === 'pending'
          ? 'bg-amber-500 text-white'
          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
      >
        <Clock class="w-4 h-4" />
        {{ t('notifications.filterPending') }}
      </button>
      <button
        @click="switchTab('resolved')"
        class="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors"
        :class="activeTab === 'resolved'
          ? 'bg-green-600 text-white'
          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
      >
        <CheckCircle class="w-4 h-4" />
        {{ t('notifications.filterResolved') }}
      </button>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="notifications.length === 0" class="text-center py-12">
      <Bell class="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
      <h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">{{ t('notifications.empty') }}</h2>
      <p class="text-slate-500 dark:text-slate-400 mb-4">{{ t('notifications.emptyDescription') }}</p>
      <RouterLink :to="localePath('/browse')" class="text-blue-600 hover:text-blue-700 font-medium">
        {{ t('notifications.browseButton') }}
      </RouterLink>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden transition-all hover:border-slate-300 dark:hover:border-slate-600"
        :class="{ 'ring-2 ring-blue-500/50': !notification.read }"
      >
        <div class="flex">
          <!-- Poster thumbnail -->
          <div
            v-if="notification.documentary_poster"
            class="flex-shrink-0 w-16 sm:w-20 bg-slate-200 dark:bg-slate-700 cursor-pointer"
            @click="handleNotificationClick(notification)"
          >
            <img
              :src="getPosterUrl(notification.documentary_poster)"
              :alt="notification.documentary_title"
              class="w-full h-full object-cover"
            />
          </div>
          <div
            v-else
            class="flex-shrink-0 w-16 sm:w-20 bg-slate-200 dark:bg-slate-700 flex items-center justify-center"
          >
            <Bell class="w-6 h-6 text-slate-400 dark:text-slate-500" />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0 p-3 sm:p-4">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <!-- Type and status badges -->
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs font-medium text-slate-500 dark:text-slate-400">
                    {{ getTypeLabel(notification.notification_type) }}
                  </span>
                  <span
                    class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium"
                    :class="{
                      'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400': getNotificationStatus(notification.notification_type) === 'pending',
                      'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400': getNotificationStatus(notification.notification_type) === 'success',
                      'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400': getNotificationStatus(notification.notification_type) === 'neutral',
                    }"
                  >
                    {{ getStatusLabel(notification.notification_type) }}
                  </span>
                </div>

                <!-- Documentary title -->
                <h3
                  class="font-semibold text-slate-900 dark:text-white truncate cursor-pointer hover:text-blue-600 dark:hover:text-blue-400"
                  :class="{ 'text-slate-500 dark:text-slate-400 italic': !notification.documentary_title }"
                  @click="handleNotificationClick(notification)"
                >
                  {{ notification.documentary_title || t('notifications.unknownDoc') }}
                </h3>

                <!-- Admin notes (if any) -->
                <p
                  v-if="hasCustomMessage(notification)"
                  class="text-sm text-slate-600 dark:text-slate-300 mt-1 line-clamp-2"
                >
                  {{ notification.message }}
                </p>

                <!-- Timestamp -->
                <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
                  {{ formatDate(notification.created_at) }}
                </p>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-1 flex-shrink-0">
                <button
                  v-if="notification.documentary_slug"
                  @click="handleNotificationClick(notification)"
                  class="p-1.5 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded transition-colors"
                  :title="t('notifications.viewDoc')"
                >
                  <ExternalLink class="w-4 h-4" />
                </button>
                <button
                  @click="notificationsStore.dismissNotification(notification.id)"
                  class="p-1.5 text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded transition-colors"
                  :title="t('notifications.delete')"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
