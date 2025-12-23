<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { User, Mail, Calendar, Pencil, X, Check } from 'lucide-vue-next'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const isEditing = ref(false)
const isSaving = ref(false)
const error = ref<string | null>(null)

const editForm = ref({
  username: '',
  bio: '',
})

function startEditing() {
  editForm.value = {
    username: user.value?.username || '',
    bio: user.value?.profile?.bio || '',
  }
  isEditing.value = true
  error.value = null
}

function cancelEditing() {
  isEditing.value = false
  error.value = null
}

async function saveProfile() {
  isSaving.value = true
  error.value = null

  try {
    await authStore.updateProfile({
      username: editForm.value.username,
      bio: editForm.value.bio,
    })
    isEditing.value = false
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const axiosError = err as { response?: { data?: { username?: string[]; detail?: string } } }
      error.value = axiosError.response?.data?.username?.[0]
        || axiosError.response?.data?.detail
        || 'Failed to save profile'
    } else {
      error.value = 'Failed to save profile'
    }
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">My Profile</h1>
      <button
        v-if="!isEditing"
        @click="startEditing"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600"
      >
        <Pencil class="w-4 h-4" />
        Edit Profile
      </button>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
      <div class="flex items-start gap-6">
        <div class="w-24 h-24 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0">
          <img
            v-if="user?.profile?.avatar"
            :src="user.profile.avatar"
            :alt="user.username"
            class="w-full h-full rounded-full object-cover"
          />
          <User v-else class="w-12 h-12 text-slate-400" />
        </div>

        <div class="flex-1">
          <!-- View Mode -->
          <template v-if="!isEditing">
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
            <div v-else class="mt-4">
              <p class="text-slate-500 dark:text-slate-500 italic">No bio yet. Click "Edit Profile" to add one.</p>
            </div>
          </template>

          <!-- Edit Mode -->
          <template v-else>
            <form @submit.prevent="saveProfile" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Username
                </label>
                <input
                  v-model="editForm.username"
                  type="text"
                  required
                  class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Bio
                </label>
                <textarea
                  v-model="editForm.bio"
                  rows="3"
                  placeholder="Tell us about yourself..."
                  class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                ></textarea>
              </div>

              <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
                {{ error }}
              </div>

              <div class="flex items-center gap-3">
                <button
                  type="submit"
                  :disabled="isSaving"
                  class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Check class="w-4 h-4" />
                  {{ isSaving ? 'Saving...' : 'Save Changes' }}
                </button>
                <button
                  type="button"
                  @click="cancelEditing"
                  :disabled="isSaving"
                  class="inline-flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  <X class="w-4 h-4" />
                  Cancel
                </button>
              </div>
            </form>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
