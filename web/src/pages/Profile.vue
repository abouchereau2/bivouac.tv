<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { User, Mail, Calendar } from 'lucide-vue-next'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-8">My Profile</h1>

    <div class="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
      <div class="flex items-start gap-6">
        <div class="w-24 h-24 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center">
          <User class="w-12 h-12 text-slate-400" />
        </div>

        <div class="flex-1">
          <h2 class="text-xl font-semibold text-slate-900 dark:text-white">
            {{ user?.username || 'User' }}
          </h2>

          <div class="mt-4 space-y-2 text-slate-600 dark:text-slate-400">
            <p class="flex items-center gap-2">
              <Mail class="w-4 h-4" />
              {{ user?.email }}
            </p>
            <p class="flex items-center gap-2">
              <Calendar class="w-4 h-4" />
              Member since {{ new Date(user?.date_joined || '').toLocaleDateString() }}
            </p>
          </div>

          <div v-if="user?.profile?.bio" class="mt-4">
            <p class="text-slate-700 dark:text-slate-300">{{ user.profile.bio }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
