<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDocumentariesStore } from '@/stores/documentaries'
import { linkSuggestionsApi } from '@/services/api'
import { X } from 'lucide-vue-next'

const { t } = useI18n()

const props = defineProps<{
  documentaryId: number
}>()

const emit = defineEmits<{
  'close': []
  'success': []
}>()

const docStore = useDocumentariesStore()

const platformId = ref<number | null>(null)
const url = ref('')
const isFree = ref(false)
const notes = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const success = ref(false)

const canSubmit = computed(() => platformId.value && url.value.trim() && !isSubmitting.value)

onMounted(() => {
  if (docStore.platforms.length === 0) {
    docStore.fetchTaxonomy()
  }
})

async function handleSubmit() {
  if (!canSubmit.value || !platformId.value) return

  isSubmitting.value = true
  error.value = null

  try {
    await linkSuggestionsApi.create({
      documentary: props.documentaryId,
      platform: platformId.value,
      url: url.value.trim(),
      is_free: isFree.value,
      notes: notes.value.trim() || undefined,
    })
    success.value = true
    setTimeout(() => {
      emit('success')
      emit('close')
    }, 1500)
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosError = err as { response?: { data?: { detail?: string; non_field_errors?: string[] } } }
      error.value = axiosError.response?.data?.detail
        || axiosError.response?.data?.non_field_errors?.[0]
        || t('link.suggestionError')
    } else {
      error.value = t('link.suggestionError')
    }
  } finally {
    isSubmitting.value = false
  }
}

function handleBackdropClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click="handleBackdropClick"
  >
    <div class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-md mx-4 overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white">
          {{ t('link.suggestTitle') }}
        </h3>
        <button
          @click="emit('close')"
          class="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <div v-if="success" class="text-center py-4">
          <p class="text-green-600 dark:text-green-400 font-medium">
            {{ t('link.suggestionSuccess') }}
          </p>
        </div>

        <form v-else @submit.prevent="handleSubmit">
          <!-- Platform Select -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ t('link.platform') }} *
            </label>
            <select
              v-model="platformId"
              class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option :value="null" disabled>{{ t('link.selectPlatform') }}</option>
              <option
                v-for="platform in docStore.platforms"
                :key="platform.id"
                :value="platform.id"
              >
                {{ platform.name }}
              </option>
            </select>
          </div>

          <!-- URL -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ t('link.url') }} *
            </label>
            <input
              v-model="url"
              type="url"
              :placeholder="t('link.urlPlaceholder')"
              class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <!-- Is Free -->
          <div class="mb-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="isFree"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
              />
              <span class="text-sm text-slate-700 dark:text-slate-300">
                {{ t('link.isFree') }}
              </span>
            </label>
          </div>

          <!-- Notes -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ t('link.notes') }}
            </label>
            <textarea
              v-model="notes"
              rows="2"
              :placeholder="t('link.notesPlaceholder')"
              class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            ></textarea>
          </div>

          <!-- Error -->
          <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3">
            <button
              type="button"
              @click="emit('close')"
              class="px-4 py-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="!canSubmit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isSubmitting ? t('common.submitting') : t('link.submit') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
