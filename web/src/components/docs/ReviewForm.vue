<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { reviewsApi } from '@/services/api'
import StarRating from '@/components/common/StarRating.vue'
import type { Review } from '@/types'

const props = defineProps<{
  documentaryId: number
  existingReview?: Review | null
}>()

const emit = defineEmits<{
  'review-saved': [review: Review]
}>()

const authStore = useAuthStore()

const rating = ref(props.existingReview?.rating || 0)
const content = ref(props.existingReview?.content || '')
const isSubmitting = ref(false)
const error = ref<string | null>(null)

const isEditing = computed(() => !!props.existingReview)
const canSubmit = computed(() => rating.value > 0 && !isSubmitting.value)

async function handleSubmit() {
  if (!canSubmit.value) return

  isSubmitting.value = true
  error.value = null

  try {
    let review: Review
    if (isEditing.value && props.existingReview) {
      const { data } = await reviewsApi.update(props.existingReview.id, {
        rating: rating.value,
        content: content.value || undefined,
      })
      review = data
    } else {
      const { data } = await reviewsApi.create({
        documentary: props.documentaryId,
        rating: rating.value,
        content: content.value || undefined,
      })
      review = data
    }
    emit('review-saved', review)
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosError = err as { response?: { data?: { detail?: string; non_field_errors?: string[] } } }
      error.value = axiosError.response?.data?.detail
        || axiosError.response?.data?.non_field_errors?.[0]
        || 'Failed to save review'
    } else {
      error.value = 'Failed to save review'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="authStore.isAuthenticated" class="bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
    <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
      {{ isEditing ? 'Edit Your Review' : 'Rate This Documentary' }}
    </h3>

    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Your Rating
        </label>
        <StarRating v-model="rating" size="lg" />
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Review (optional)
        </label>
        <textarea
          v-model="content"
          rows="3"
          placeholder="Share your thoughts about this documentary..."
          class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        ></textarea>
      </div>

      <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
        {{ error }}
      </div>

      <button
        type="submit"
        :disabled="!canSubmit"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isSubmitting ? 'Saving...' : (isEditing ? 'Update Review' : 'Submit Review') }}
      </button>
    </form>
  </div>

  <div v-else class="bg-slate-100 dark:bg-slate-800 rounded-lg p-6 text-center">
    <p class="text-slate-600 dark:text-slate-400 mb-3">
      Sign in to rate and review this documentary
    </p>
    <RouterLink
      to="/login"
      class="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      Sign In
    </RouterLink>
  </div>
</template>
