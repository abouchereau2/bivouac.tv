<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { linkReportsApi } from '@/services/api'
import { X } from 'lucide-vue-next'
import type { Availability } from '@/types'

const { t } = useI18n()

const props = defineProps<{
  availability: Availability
}>()

const emit = defineEmits<{
  'close': []
  'success': []
}>()

type ReportReason = 'broken' | 'geo_restricted' | 'paywall' | 'wrong_content' | 'other'

const reasons: { value: ReportReason; labelKey: string }[] = [
  { value: 'broken', labelKey: 'link.reasonBroken' },
  { value: 'geo_restricted', labelKey: 'link.reasonGeoRestricted' },
  { value: 'paywall', labelKey: 'link.reasonPaywall' },
  { value: 'wrong_content', labelKey: 'link.reasonWrongContent' },
  { value: 'other', labelKey: 'link.reasonOther' },
]

const reason = ref<ReportReason | null>(null)
const details = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const success = ref(false)

const canSubmit = computed(() => reason.value && !isSubmitting.value)

async function handleSubmit() {
  if (!canSubmit.value || !reason.value) return

  isSubmitting.value = true
  error.value = null

  try {
    await linkReportsApi.create({
      availability: props.availability.id,
      reason: reason.value,
      details: details.value.trim() || undefined,
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
        || t('link.reportError')
    } else {
      error.value = t('link.reportError')
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
          {{ t('link.reportTitle') }}
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
        <!-- Platform info -->
        <div class="mb-4 p-3 bg-slate-100 dark:bg-slate-700 rounded-lg">
          <p class="text-sm text-slate-600 dark:text-slate-300">
            {{ t('link.reportingFor') }} <strong>{{ availability.platform.name }}</strong>
          </p>
        </div>

        <div v-if="success" class="text-center py-4">
          <p class="text-green-600 dark:text-green-400 font-medium">
            {{ t('link.reportSuccess') }}
          </p>
        </div>

        <form v-else @submit.prevent="handleSubmit">
          <!-- Reason Select -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ t('link.reportReason') }} *
            </label>
            <div class="space-y-2">
              <label
                v-for="r in reasons"
                :key="r.value"
                class="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer"
              >
                <input
                  v-model="reason"
                  type="radio"
                  :value="r.value"
                  class="w-4 h-4 text-blue-600 border-slate-300 focus:ring-blue-500"
                />
                <span class="text-sm text-slate-700 dark:text-slate-300">
                  {{ t(r.labelKey) }}
                </span>
              </label>
            </div>
          </div>

          <!-- Details -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              {{ t('link.reportDetails') }}
            </label>
            <textarea
              v-model="details"
              rows="2"
              :placeholder="t('link.reportDetailsPlaceholder')"
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
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isSubmitting ? t('common.submitting') : t('link.reportSubmit') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
