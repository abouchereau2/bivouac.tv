<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { Mountain, Search, User, LogOut, Plus, Bookmark, Eye, Globe } from 'lucide-vue-next'
import { setLocale, SUPPORTED_LOCALES, type SupportedLocale } from '@/i18n'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

// Get current language from route
const currentLang = computed(() => (route.params.lang as string) || 'en')

// Build localized route
function localePath(path: string) {
  return `/${currentLang.value}${path}`
}

// Switch language
function switchLanguage(lang: SupportedLocale) {
  if (lang === locale.value) return

  setLocale(lang)

  // Update current route with new language
  const newPath = route.fullPath.replace(`/${currentLang.value}`, `/${lang}`)
  router.push(newPath)
}

async function handleLogout() {
  await authStore.logout()
  router.push(localePath('/'))
}
</script>

<template>
  <header class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <RouterLink :to="localePath('/')" class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white">
          <Mountain class="w-8 h-8 text-blue-600" />
          <span>Bivouac.tv</span>
        </RouterLink>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-6">
          <RouterLink
            :to="localePath('/browse')"
            class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            {{ t('nav.browse') }}
          </RouterLink>
          <RouterLink
            :to="localePath('/browse') + '?is_free=true'"
            class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            {{ t('nav.freeToWatch') }}
          </RouterLink>
        </nav>

        <!-- Right side -->
        <div class="flex items-center gap-4">
          <!-- Language Switcher -->
          <div class="relative group">
            <button class="flex items-center gap-1 p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors">
              <Globe class="w-5 h-5" />
              <span class="text-sm font-medium uppercase">{{ locale }}</span>
            </button>
            <div class="absolute right-0 mt-2 w-32 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
              <button
                v-for="lang in SUPPORTED_LOCALES"
                :key="lang"
                @click="switchLanguage(lang)"
                class="w-full text-left px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 first:rounded-t-lg last:rounded-b-lg"
                :class="{ 'bg-slate-100 dark:bg-slate-700': locale === lang }"
              >
                {{ t(`languages.${lang}`) }}
              </button>
            </div>
          </div>

          <!-- Search -->
          <RouterLink
            :to="localePath('/browse')"
            class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            <Search class="w-5 h-5" />
          </RouterLink>

          <!-- Authenticated user menu -->
          <template v-if="isAuthenticated">
            <RouterLink
              :to="localePath('/watched')"
              class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              :title="t('nav.watched')"
            >
              <Eye class="w-5 h-5" />
            </RouterLink>

            <RouterLink
              :to="localePath('/watchlist')"
              class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              :title="t('nav.watchlist')"
            >
              <Bookmark class="w-5 h-5" />
            </RouterLink>

            <RouterLink
              :to="localePath('/submit')"
              class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              :title="t('nav.submit')"
            >
              <Plus class="w-5 h-5" />
            </RouterLink>

            <div class="relative group">
              <button class="flex items-center gap-2 p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors">
                <User class="w-5 h-5" />
                <span class="hidden sm:inline">{{ user?.username }}</span>
              </button>

              <!-- Dropdown -->
              <div class="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                <RouterLink
                  :to="localePath('/profile')"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-t-lg"
                >
                  {{ t('nav.profile') }}
                </RouterLink>
                <RouterLink
                  :to="localePath('/watchlist')"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                >
                  {{ t('nav.watchlist') }}
                </RouterLink>
                <RouterLink
                  :to="localePath('/watched')"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                >
                  {{ t('nav.watched') }}
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
              :to="localePath('/login')"
              class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              {{ t('nav.login') }}
            </RouterLink>
            <RouterLink
              :to="localePath('/register')"
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
