<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Mountain, Search, User, LogOut, Plus, Bookmark } from 'lucide-vue-next'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

async function handleLogout() {
  await authStore.logout()
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
            Browse
          </RouterLink>
          <RouterLink
            to="/browse?is_free=true"
            class="text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
          >
            Free to Watch
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
              to="/watchlist"
              class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              title="Watchlist"
            >
              <Bookmark class="w-5 h-5" />
            </RouterLink>

            <RouterLink
              to="/submit"
              class="p-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              title="Submit a documentary"
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
                  to="/profile"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-t-lg"
                >
                  Profile
                </RouterLink>
                <RouterLink
                  to="/watchlist"
                  class="block px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                >
                  My Watchlist
                </RouterLink>
                <button
                  @click="handleLogout"
                  class="w-full text-left px-4 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-b-lg flex items-center gap-2"
                >
                  <LogOut class="w-4 h-4" />
                  Logout
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
              Login
            </RouterLink>
            <RouterLink
              to="/register"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Sign Up
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
