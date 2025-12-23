<script setup lang="ts">
import { computed } from 'vue'
import { Star } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  modelValue?: number
  readonly?: boolean
  size?: 'sm' | 'md' | 'lg'
}>(), {
  modelValue: 0,
  readonly: false,
  size: 'md',
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-4 h-4'
    case 'lg': return 'w-8 h-8'
    default: return 'w-6 h-6'
  }
})

const gapClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'gap-0.5'
    case 'lg': return 'gap-1.5'
    default: return 'gap-1'
  }
})

function setRating(rating: number) {
  if (!props.readonly) {
    emit('update:modelValue', rating)
  }
}
</script>

<template>
  <div
    class="inline-flex"
    :class="[gapClass, { 'cursor-pointer': !readonly }]"
  >
    <button
      v-for="star in 5"
      :key="star"
      type="button"
      :disabled="readonly"
      @click="setRating(star)"
      class="focus:outline-none disabled:cursor-default transition-transform"
      :class="{ 'hover:scale-110': !readonly }"
    >
      <Star
        :class="[
          sizeClasses,
          star <= modelValue
            ? 'text-yellow-500 fill-yellow-500'
            : 'text-slate-300 dark:text-slate-600'
        ]"
      />
    </button>
  </div>
</template>
