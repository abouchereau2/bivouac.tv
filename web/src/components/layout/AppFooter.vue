<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Mountain } from 'lucide-vue-next'
import { useLocalePath } from '@/composables/useLocalePath'

const { t } = useI18n()
const { localePath } = useLocalePath()
</script>

<template>
  <footer class="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Brand -->
        <div class="col-span-1 md:col-span-2">
          <RouterLink :to="localePath('/')" class="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white mb-4">
            <Mountain class="w-8 h-8 text-blue-600" />
            <span>Bivouac.tv</span>
          </RouterLink>
          <p class="text-slate-600 dark:text-slate-400 max-w-md">
            {{ t('footer.tagline') }}
          </p>
        </div>

        <!-- Browse -->
        <div>
          <h3 class="font-semibold text-slate-900 dark:text-white mb-4">{{ t('footer.browseTitle') }}</h3>
          <ul class="space-y-2">
            <li>
              <RouterLink :to="localePath('/browse') + '?sport=climbing'" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                {{ t('footer.climbing') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink :to="localePath('/browse') + '?sport=skiing'" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                {{ t('footer.skiing') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink :to="localePath('/browse') + '?sport=surfing'" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                {{ t('footer.surfing') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink :to="localePath('/browse') + '?is_free=true'" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                {{ t('nav.freeToWatch') }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- About -->
        <div>
          <h3 class="font-semibold text-slate-900 dark:text-white mb-4">{{ t('footer.aboutTitle') }}</h3>
          <ul class="space-y-2">
            <li>
              <RouterLink :to="localePath('/submit')" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                {{ t('footer.submitDoc') }}
              </RouterLink>
            </li>
            <li>
              <a href="mailto:hello@bivouac.tv" class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400">
                {{ t('footer.contact') }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700 text-center text-slate-500 dark:text-slate-400 text-sm">
        <p>&copy; {{ new Date().getFullYear() }} Bivouac.tv. {{ t('footer.madeWith') }}</p>
      </div>
    </div>
  </footer>
</template>
