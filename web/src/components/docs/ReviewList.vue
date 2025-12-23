<script setup lang="ts">
import { formatDistanceToNow } from 'date-fns'
import StarRating from '@/components/common/StarRating.vue'
import type { Review } from '@/types'

defineProps<{
  reviews: Review[]
  loading?: boolean
}>()

function formatDate(dateString: string): string {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true })
}
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="reviews.length === 0" class="text-center py-8 text-slate-500 dark:text-slate-400">
      No reviews yet. Be the first to share your thoughts!
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="review in reviews"
        :key="review.id"
        class="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700"
      >
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center flex-shrink-0">
            <img
              v-if="review.user.avatar"
              :src="review.user.avatar"
              :alt="review.user.username"
              class="w-full h-full rounded-full object-cover"
            />
            <span v-else class="text-slate-500 dark:text-slate-400 font-medium">
              {{ review.user.username.charAt(0).toUpperCase() }}
            </span>
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-medium text-slate-900 dark:text-white">
                {{ review.user.username }}
              </span>
              <StarRating :model-value="review.rating" readonly size="sm" />
              <span class="text-sm text-slate-500 dark:text-slate-400">
                {{ formatDate(review.created_at) }}
              </span>
            </div>

            <p v-if="review.content" class="mt-2 text-slate-700 dark:text-slate-300">
              {{ review.content }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
