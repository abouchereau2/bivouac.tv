<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { Mountain, Search, User, LogOut, Plus, Shield, Bell, Check, ExternalLink } from 'lucide-vue-next'

const { t, te } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

// Notification helpers
function getNotificationTitle(notification: { notification_type: string; documentary_title?: string; title: string }) {
  const titleKey = `notifications.titles.${notification.notification_type}`
  if (te(titleKey)) {
    return t(titleKey, { title: notification.documentary_title || '' })
  }
  return notification.title
}

function getNotificationMessage(notification: { notification_type: string; message: string }) {
  const messageKey = `notifications.messages.${notification.notification_type}`
  if (te(messageKey)) {
    return t(messageKey)
  }
  return notification.message
}

function getNotificationIcon(type: string, status: string) {
  // Pending notifications (awaiting review)
  if (status === 'pending' || type.includes('_pending')) return 'pending'
  // Positive outcomes
  if (type.includes('approved') || type.includes('fixed')) return 'success'
  // Negative/neutral outcomes
  if (type.includes('rejected') || type.includes('dismissed')) return 'info'
  return 'default'
}

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return t('notifications.justNow')
  if (seconds < 3600) return t('notifications.minutesAgo', { count: Math.floor(seconds / 60) })
  if (seconds < 86400) return t('notifications.hoursAgo', { count: Math.floor(seconds / 3600) })
  return t('notifications.daysAgo', { count: Math.floor(seconds / 86400) })
}

async function handleNotificationClick(notification: { id: number; read: boolean; documentary_slug?: string }) {
  if (!notification.read) {
    await notificationsStore.markAsRead(notification.id)
  }
  if (notification.documentary_slug) {
    router.push(`/doc/${notification.documentary_slug}`)
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white">
          <Mountain class="w-8 h-8 text-blue-600" />
          <span>Bivouac.tv</span>
        </RouterLink>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-6">
          <RouterLink
            to="/browse"
            class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            {{ t('nav.browse') }}
          </RouterLink>
          <RouterLink
            to="/browse?is_free=true"
            class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            {{ t('nav.freeToWatch') }}
          </RouterLink>
        </nav>

        <!-- Right side -->
        <div class="flex items-center gap-4">
          <!-- Search -->
          <RouterLink
            to="/browse"
            class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <Search class="w-5 h-5" />
          </RouterLink>

          <!-- Authenticated user menu -->
          <template v-if="isAuthenticated">
            <RouterLink
              to="/submit"
              class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              :title="t('nav.submit')"
            >
              <Plus class="w-5 h-5" />
            </RouterLink>

            <!-- Notifications -->
            <div class="relative group">
              <button class="relative p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors">
                <Bell class="w-5 h-5" />
                <span
                  v-if="notificationsStore.unreadCount > 0"
                  class="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center min-w-4 h-4 px-1 text-xs font-medium text-white rounded-full"
                  :class="notificationsStore.hasPending ? 'bg-amber-500' : 'bg-red-500'"
                >
                  {{ notificationsStore.unreadCount > 9 ? '9+' : notificationsStore.unreadCount }}
                </span>
              </button>

              <!-- Notifications dropdown -->
              <div class="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all max-h-96 overflow-hidden flex flex-col">
                <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                  <h3 class="font-semibold text-slate-900 dark:text-white">{{ t('notifications.title') }}</h3>
                  <button
                    v-if="notificationsStore.hasUnread"
                    @click.stop="notificationsStore.markAllAsRead()"
                    class="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    <Check class="w-3 h-3" />
                    {{ t('notifications.markAllRead') }}
                  </button>
                </div>

                <div class="overflow-y-auto flex-1">
                  <div v-if="notificationsStore.notifications.length === 0" class="px-4 py-8 text-center text-slate-500 dark:text-slate-400">
                    <Bell class="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>{{ t('notifications.empty') }}</p>
                  </div>

                  <button
                    v-for="notification in notificationsStore.notifications.slice(0, 5)"
                    :key="notification.id"
                    @click="handleNotificationClick(notification)"
                    class="w-full text-left px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors border-b border-slate-100 dark:border-slate-700 last:border-b-0"
                    :class="{ 'bg-blue-50 dark:bg-blue-900/20': !notification.read }"
                  >
                    <div class="flex items-start gap-3">
                      <div
                        class="flex-shrink-0 w-2 h-2 mt-2 rounded-full"
                        :class="{
                          'bg-amber-500': getNotificationIcon(notification.notification_type, notification.status) === 'pending',
                          'bg-green-500': getNotificationIcon(notification.notification_type, notification.status) === 'success',
                          'bg-blue-500': getNotificationIcon(notification.notification_type, notification.status) === 'info',
                          'bg-slate-400': getNotificationIcon(notification.notification_type, notification.status) === 'default',
                        }"
                      />
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-slate-900 dark:text-white truncate">
                          {{ getNotificationTitle(notification) }}
                        </p>
                        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                          {{ getNotificationMessage(notification) }}
                        </p>
                        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
                          {{ formatTimeAgo(notification.created_at) }}
                        </p>
                      </div>
                      <ExternalLink v-if="notification.documentary_slug" class="w-4 h-4 text-slate-400 flex-shrink-0" />
                    </div>
                  </button>
                </div>

                <RouterLink
                  v-if="notificationsStore.notifications.length > 0"
                  to="/notifications"
                  class="block px-4 py-3 text-center text-sm text-blue-600 dark:text-blue-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 border-t border-slate-200 dark:border-slate-700"
                >
                  {{ t('notifications.viewAll') }}
                </RouterLink>
              </div>
            </div>

            <div class="relative group">
              <button class="flex items-center gap-2 p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors">
                <User class="w-5 h-5" />
                <span class="hidden sm:inline">{{ user?.username }}</span>
              </button>

              <!-- Dropdown -->
              <div class="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                <RouterLink
                  to="/profile"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-t-lg"
                >
                  {{ t('nav.profile') }}
                </RouterLink>
                <RouterLink
                  to="/watchlist"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                >
                  {{ t('nav.watchlist') }}
                </RouterLink>
                <RouterLink
                  to="/watched"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                >
                  {{ t('nav.watched') }}
                </RouterLink>
                <RouterLink
                  to="/favorites"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                >
                  {{ t('nav.favorites') }}
                </RouterLink>
                <RouterLink
                  v-if="authStore.isAdmin"
                  to="/admin"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
                >
                  <Shield class="w-4 h-4" />
                  {{ t('nav.admin') }}
                  <span
                    v-if="authStore.pendingReviewCount > 0"
                    class="ml-auto inline-flex items-center justify-center min-w-5 h-5 px-1.5 text-xs font-medium text-white bg-red-500 rounded-full"
                  >
                    {{ authStore.pendingReviewCount > 99 ? '99+' : authStore.pendingReviewCount }}
                  </span>
                </RouterLink>
                <button
                  @click="handleLogout"
                  class="w-full text-left px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-b-lg flex items-center gap-2"
                >
                  <LogOut class="w-4 h-4" />
                  {{ t('nav.logout') }}
                </button>
              </div>
            </div>
          </template>

          <!-- Guest menu -->
          <template v-else>
            <RouterLink
              to="/login"
              class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              {{ t('nav.login') }}
            </RouterLink>
            <RouterLink
              to="/register"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {{ t('nav.signup') }}
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
