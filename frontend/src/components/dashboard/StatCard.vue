<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  value: string | number
  trend?: number
  color?: string
}>()

const isPositive = computed(() => (props.trend || 0) > 0)
const trendFormatted = computed(() => {
  if (props.trend === undefined) return ''
  const sign = isPositive.value ? '+' : ''
  return `${sign}${props.trend}%`
})
</script>

<template>
  <div class="bg-bg-canvas border border-border-default rounded-lg p-5 flex flex-col gap-2">
    <div class="text-text-secondary text-xs font-bold uppercase tracking-wider">{{ title }}</div>
    <div class="flex items-end justify-between mt-1">
      <div class="text-3xl font-black" :class="color || 'text-text-primary'">{{ value }}</div>
      <div
        v-if="trend !== undefined"
        class="text-xs font-bold px-2 py-0.5 rounded-full"
        :class="isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
      >
        {{ trendFormatted }}
      </div>
    </div>
  </div>
</template>
