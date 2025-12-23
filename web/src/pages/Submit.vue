<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { submissionsApi } from '@/services/api'
import { Plus, Check } from 'lucide-vue-next'

const router = useRouter()

const title = ref('')
const year = ref(new Date().getFullYear())
const url = ref('')
const notes = ref('')
const loading = ref(false)
const success = ref(false)
const error = ref('')

async function handleSubmit() {
  error.value = ''
  loading.value = true

  try {
    await submissionsApi.create({
      title: title.value,
      year: year.value,
      url: url.value,
      notes: notes.value,
    })
    success.value = true
    setTimeout(() => router.push('/'), 2000)
  } catch {
    error.value = 'Failed to submit. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center gap-3 mb-8">
      <Plus class="w-8 h-8 text-blue-600" />
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Submit a Documentary</h1>
    </div>

    <div v-if="success" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6 text-center">
      <Check class="w-12 h-12 text-green-600 mx-auto mb-4" />
      <h2 class="text-xl font-semibold text-green-800 dark:text-green-200 mb-2">Thank you!</h2>
      <p class="text-green-600 dark:text-green-400">Your submission has been received and will be reviewed soon.</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
      <p class="text-slate-600 dark:text-slate-400 mb-6">
        Know a great adventure documentary that's not on Bivouac.tv? Submit it here and help grow our collection!
      </p>

      <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
        {{ error }}
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Documentary Title *
        </label>
        <input
          v-model="title"
          type="text"
          required
          class="w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Free Solo"
        />
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Year *
        </label>
        <input
          v-model.number="year"
          type="number"
          required
          min="1900"
          :max="new Date().getFullYear() + 1"
          class="w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Link *
        </label>
        <input
          v-model="url"
          type="url"
          required
          class="w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="https://... (trailer or streaming link)"
        />
        <p class="text-sm text-slate-500 mt-1">Link to a trailer, IMDb page, or streaming platform</p>
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Additional Notes
        </label>
        <textarea
          v-model="notes"
          rows="3"
          class="w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Any additional information about the documentary..."
        ></textarea>
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
      >
        {{ loading ? 'Submitting...' : 'Submit Documentary' }}
      </button>
    </form>
  </div>
</template>
