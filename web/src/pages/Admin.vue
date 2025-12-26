<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useLocalePath } from '@/composables/useLocalePath'
import { adminApi } from '@/services/api'
import {
  Film, Link, AlertTriangle, Check, X, ExternalLink,
  Clock, User, ChevronDown, ChevronUp
} from 'lucide-vue-next'
import type { Submission, LinkSuggestion, LinkReport } from '@/types'

const { t } = useI18n()
const { localePath } = useLocalePath()
const authStore = useAuthStore()

const loading = ref(true)
const activeTab = ref<'submissions' | 'suggestions' | 'reports'>('submissions')

const submissions = ref<Submission[]>([])
const linkSuggestions = ref<LinkSuggestion[]>([])
const linkReports = ref<LinkReport[]>([])

const processingId = ref<number | null>(null)

const totalPending = computed(() =>
  submissions.value.length + linkSuggestions.value.length + linkReports.value.length
)

// Expanded items for showing notes input
const expandedItem = ref<{ type: string; id: number } | null>(null)
const actionNotes = ref('')

function toggleExpand(type: string, id: number) {
  if (expandedItem.value?.type === type && expandedItem.value?.id === id) {
    expandedItem.value = null
    actionNotes.value = ''
  } else {
    expandedItem.value = { type, id }
    actionNotes.value = ''
  }
}

async function fetchPendingItems() {
  loading.value = true
  try {
    const [subs, suggestions, reports] = await Promise.all([
      adminApi.pendingSubmissions(),
      adminApi.pendingLinkSuggestions(),
      adminApi.pendingLinkReports(),
    ])
    submissions.value = subs.data
    linkSuggestions.value = suggestions.data
    linkReports.value = reports.data
  } catch (err) {
    console.error('Failed to fetch pending items:', err)
  } finally {
    loading.value = false
  }
}

// Submission actions
async function approveSubmission(id: number) {
  processingId.value = id
  try {
    await adminApi.approveSubmission(id, actionNotes.value || undefined)
    submissions.value = submissions.value.filter(s => s.id !== id)
    expandedItem.value = null
    actionNotes.value = ''
    authStore.fetchPendingCount()
  } finally {
    processingId.value = null
  }
}

async function rejectSubmission(id: number) {
  processingId.value = id
  try {
    await adminApi.rejectSubmission(id, actionNotes.value || undefined)
    submissions.value = submissions.value.filter(s => s.id !== id)
    expandedItem.value = null
    actionNotes.value = ''
    authStore.fetchPendingCount()
  } finally {
    processingId.value = null
  }
}

// Link suggestion actions
async function approveLinkSuggestion(id: number) {
  processingId.value = id
  try {
    await adminApi.approveLinkSuggestion(id, actionNotes.value || undefined)
    linkSuggestions.value = linkSuggestions.value.filter(s => s.id !== id)
    expandedItem.value = null
    actionNotes.value = ''
    authStore.fetchPendingCount()
  } finally {
    processingId.value = null
  }
}

async function rejectLinkSuggestion(id: number) {
  processingId.value = id
  try {
    await adminApi.rejectLinkSuggestion(id, actionNotes.value || undefined)
    linkSuggestions.value = linkSuggestions.value.filter(s => s.id !== id)
    expandedItem.value = null
    actionNotes.value = ''
    authStore.fetchPendingCount()
  } finally {
    processingId.value = null
  }
}

// Link report actions
async function fixLinkReport(id: number) {
  processingId.value = id
  try {
    await adminApi.fixLinkReport(id, actionNotes.value || undefined)
    linkReports.value = linkReports.value.filter(r => r.id !== id)
    expandedItem.value = null
    actionNotes.value = ''
    authStore.fetchPendingCount()
  } finally {
    processingId.value = null
  }
}

async function dismissLinkReport(id: number) {
  processingId.value = id
  try {
    await adminApi.dismissLinkReport(id, actionNotes.value || undefined)
    linkReports.value = linkReports.value.filter(r => r.id !== id)
    expandedItem.value = null
    actionNotes.value = ''
    authStore.fetchPendingCount()
  } finally {
    processingId.value = null
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const reasonLabels: Record<string, string> = {
  broken: 'admin.reasonBroken',
  geo_restricted: 'admin.reasonGeoRestricted',
  paywall: 'admin.reasonPaywall',
  wrong_content: 'admin.reasonWrongContent',
  other: 'admin.reasonOther',
}

onMounted(fetchPendingItems)
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">
        {{ t('admin.title') }}
      </h1>
      <p class="mt-2 text-slate-600 dark:text-slate-400">
        {{ t('admin.subtitle', { count: totalPending }) }}
      </p>
    </div>

    <!-- Access denied -->
    <div v-if="!authStore.isAdmin" class="text-center py-16">
      <p class="text-slate-600 dark:text-slate-400">
        {{ t('admin.accessDenied') }}
      </p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="flex justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Tabs -->
      <div class="flex gap-1 mb-6 border-b border-slate-200 dark:border-slate-700">
        <button
          @click="activeTab = 'submissions'"
          class="flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="activeTab === 'submissions'
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
        >
          <Film class="w-4 h-4" />
          {{ t('admin.newDocs') }}
          <span v-if="submissions.length" class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
            {{ submissions.length }}
          </span>
        </button>
        <button
          @click="activeTab = 'suggestions'"
          class="flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="activeTab === 'suggestions'
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
        >
          <Link class="w-4 h-4" />
          {{ t('admin.linkSuggestions') }}
          <span v-if="linkSuggestions.length" class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
            {{ linkSuggestions.length }}
          </span>
        </button>
        <button
          @click="activeTab = 'reports'"
          class="flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="activeTab === 'reports'
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
        >
          <AlertTriangle class="w-4 h-4" />
          {{ t('admin.linkReports') }}
          <span v-if="linkReports.length" class="px-2 py-0.5 text-xs rounded-full bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300">
            {{ linkReports.length }}
          </span>
        </button>
      </div>

      <!-- Submissions Tab -->
      <div v-if="activeTab === 'submissions'">
        <div v-if="!submissions.length" class="text-center py-12 text-slate-500">
          {{ t('admin.noSubmissions') }}
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="sub in submissions"
            :key="sub.id"
            class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
          >
            <div class="p-4">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <h3 class="font-semibold text-slate-900 dark:text-white">
                    {{ sub.title }} <span class="font-normal text-slate-500">({{ sub.year }})</span>
                  </h3>
                  <div class="flex items-center gap-4 mt-1 text-sm text-slate-500">
                    <span class="flex items-center gap-1">
                      <User class="w-3.5 h-3.5" />
                      {{ sub.submitted_by.username }}
                    </span>
                    <span class="flex items-center gap-1">
                      <Clock class="w-3.5 h-3.5" />
                      {{ formatDate(sub.created_at) }}
                    </span>
                  </div>
                  <a
                    :href="sub.url"
                    target="_blank"
                    class="inline-flex items-center gap-1 mt-2 text-sm text-blue-600 hover:text-blue-700"
                  >
                    {{ sub.url }}
                    <ExternalLink class="w-3.5 h-3.5" />
                  </a>
                  <p v-if="sub.notes" class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                    {{ sub.notes }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="toggleExpand('submission', sub.id)"
                    class="p-1.5 text-slate-400 hover:text-slate-600"
                  >
                    <ChevronDown v-if="expandedItem?.type !== 'submission' || expandedItem?.id !== sub.id" class="w-5 h-5" />
                    <ChevronUp v-else class="w-5 h-5" />
                  </button>
                  <button
                    @click="approveSubmission(sub.id)"
                    :disabled="processingId === sub.id"
                    class="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg"
                    :title="t('admin.approve')"
                  >
                    <Check class="w-5 h-5" />
                  </button>
                  <button
                    @click="rejectSubmission(sub.id)"
                    :disabled="processingId === sub.id"
                    class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                    :title="t('admin.reject')"
                  >
                    <X class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
            <!-- Expanded notes input -->
            <div
              v-if="expandedItem?.type === 'submission' && expandedItem?.id === sub.id"
              class="px-4 pb-4 pt-2 border-t border-slate-100 dark:border-slate-700"
            >
              <input
                v-model="actionNotes"
                type="text"
                :placeholder="t('admin.notesPlaceholder')"
                class="w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Link Suggestions Tab -->
      <div v-if="activeTab === 'suggestions'">
        <div v-if="!linkSuggestions.length" class="text-center py-12 text-slate-500">
          {{ t('admin.noSuggestions') }}
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="sug in linkSuggestions"
            :key="sug.id"
            class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
          >
            <div class="p-4">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <RouterLink
                    :to="localePath(`/doc/${sug.documentary_slug}`)"
                    class="font-semibold text-slate-900 dark:text-white hover:text-blue-600"
                  >
                    {{ sug.documentary_title }}
                  </RouterLink>
                  <div class="flex items-center gap-4 mt-1 text-sm text-slate-500">
                    <span class="font-medium text-slate-700 dark:text-slate-300">
                      {{ sug.platform.name }}
                    </span>
                    <span v-if="sug.is_free" class="text-green-600">{{ t('common.free') }}</span>
                    <span class="flex items-center gap-1">
                      <User class="w-3.5 h-3.5" />
                      {{ sug.submitted_by.username }}
                    </span>
                    <span class="flex items-center gap-1">
                      <Clock class="w-3.5 h-3.5" />
                      {{ formatDate(sug.created_at) }}
                    </span>
                  </div>
                  <a
                    :href="sug.url"
                    target="_blank"
                    class="inline-flex items-center gap-1 mt-2 text-sm text-blue-600 hover:text-blue-700"
                  >
                    {{ sug.url }}
                    <ExternalLink class="w-3.5 h-3.5" />
                  </a>
                  <p v-if="sug.notes" class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                    {{ sug.notes }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="toggleExpand('suggestion', sug.id)"
                    class="p-1.5 text-slate-400 hover:text-slate-600"
                  >
                    <ChevronDown v-if="expandedItem?.type !== 'suggestion' || expandedItem?.id !== sug.id" class="w-5 h-5" />
                    <ChevronUp v-else class="w-5 h-5" />
                  </button>
                  <button
                    @click="approveLinkSuggestion(sug.id)"
                    :disabled="processingId === sug.id"
                    class="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg"
                    :title="t('admin.approve')"
                  >
                    <Check class="w-5 h-5" />
                  </button>
                  <button
                    @click="rejectLinkSuggestion(sug.id)"
                    :disabled="processingId === sug.id"
                    class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                    :title="t('admin.reject')"
                  >
                    <X class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
            <!-- Expanded notes input -->
            <div
              v-if="expandedItem?.type === 'suggestion' && expandedItem?.id === sug.id"
              class="px-4 pb-4 pt-2 border-t border-slate-100 dark:border-slate-700"
            >
              <input
                v-model="actionNotes"
                type="text"
                :placeholder="t('admin.notesPlaceholder')"
                class="w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Link Reports Tab -->
      <div v-if="activeTab === 'reports'">
        <div v-if="!linkReports.length" class="text-center py-12 text-slate-500">
          {{ t('admin.noReports') }}
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="report in linkReports"
            :key="report.id"
            class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
          >
            <div class="p-4">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <RouterLink
                    :to="localePath(`/doc/${report.documentary_slug}`)"
                    class="font-semibold text-slate-900 dark:text-white hover:text-blue-600"
                  >
                    {{ report.documentary_title }}
                  </RouterLink>
                  <div class="flex items-center gap-4 mt-1 text-sm text-slate-500">
                    <span class="font-medium text-slate-700 dark:text-slate-300">
                      {{ report.platform_name }}
                    </span>
                    <span class="px-2 py-0.5 text-xs rounded-full bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300">
                      {{ t(reasonLabels[report.reason] || report.reason) }}
                    </span>
                    <span class="flex items-center gap-1">
                      <User class="w-3.5 h-3.5" />
                      {{ report.reported_by.username }}
                    </span>
                    <span class="flex items-center gap-1">
                      <Clock class="w-3.5 h-3.5" />
                      {{ formatDate(report.created_at) }}
                    </span>
                  </div>
                  <a
                    :href="report.availability_url"
                    target="_blank"
                    class="inline-flex items-center gap-1 mt-2 text-sm text-blue-600 hover:text-blue-700"
                  >
                    {{ report.availability_url }}
                    <ExternalLink class="w-3.5 h-3.5" />
                  </a>
                  <p v-if="report.details" class="mt-2 text-sm text-slate-600 dark:text-slate-400">
                    {{ report.details }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="toggleExpand('report', report.id)"
                    class="p-1.5 text-slate-400 hover:text-slate-600"
                  >
                    <ChevronDown v-if="expandedItem?.type !== 'report' || expandedItem?.id !== report.id" class="w-5 h-5" />
                    <ChevronUp v-else class="w-5 h-5" />
                  </button>
                  <button
                    @click="fixLinkReport(report.id)"
                    :disabled="processingId === report.id"
                    class="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg"
                    :title="t('admin.markFixed')"
                  >
                    <Check class="w-5 h-5" />
                  </button>
                  <button
                    @click="dismissLinkReport(report.id)"
                    :disabled="processingId === report.id"
                    class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                    :title="t('admin.dismiss')"
                  >
                    <X class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
            <!-- Expanded notes input -->
            <div
              v-if="expandedItem?.type === 'report' && expandedItem?.id === report.id"
              class="px-4 pb-4 pt-2 border-t border-slate-100 dark:border-slate-700"
            >
              <input
                v-model="actionNotes"
                type="text"
                :placeholder="t('admin.notesPlaceholder')"
                class="w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
