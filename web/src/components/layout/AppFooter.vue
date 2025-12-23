<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Mountain } from 'lucide-vue-next'
</script>

<template>
  <footer class="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Brand -->
        <div class="col-span-1 md:col-span-2">
          <RouterLink to="/" class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white mb-4">
            <Mountain class="w-8 h-8 text-blue-600" />
            <span>Bivouac.tv</span>
          </RouterLink>
          <p class="text-slate-600 dark:text-slate-400 max-w-md">
            The basecamp for adventure, nature & extreme sports documentaries.
            Discover, rate, and share your favorite outdoor films.
          </p>
        </div>

        <!-- Browse -->
        <div>
          <h3 class="font-semibold text-slate-900 dark:text-white mb-4">Browse</h3>
          <ul class="space-y-2">
            <li>
              <RouterLink to="/browse?sport=climbing" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                Climbing
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/browse?sport=skiing" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                Skiing
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/browse?sport=surfing" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                Surfing
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/browse?is_free=true" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                Free to Watch
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- About -->
        <div>
          <h3 class="font-semibold text-slate-900 dark:text-white mb-4">About</h3>
          <ul class="space-y-2">
            <li>
              <RouterLink to="/submit" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                Submit a Doc
              </RouterLink>
            </li>
            <li>
              <a href="mailto:hello@bivouac.tv" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                Contact
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700 text-center text-slate-500 dark:text-slate-400 text-sm">
        <p>&copy; {{ new Date().getFullYear() }} Bivouac.tv. Made with love for adventure.</p>
      </div>
    </div>
  </footer>
</template>
