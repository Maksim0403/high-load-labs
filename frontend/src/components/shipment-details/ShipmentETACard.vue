<script setup lang="ts">
import { computed } from 'vue'
import { Clock, AlertTriangle, Calendar } from 'lucide-vue-next'
import type { Route } from '@/types'

const props = defineProps<{
  route: Route
}>()

const formatDate = (date: string | null | undefined): string => {
  if (!date) return '—'
  return new Date(date).toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatFullDate = (date: string | null | undefined): string => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('uk-UA', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const isDelayed = computed(() => {
  return props.route.is_delayed || (props.route.delay_minutes && props.route.delay_minutes > 60)
})

const delayText = computed(() => {
  if (!props.route.delay_minutes) return ''
  const hours = Math.floor(props.route.delay_minutes / 60)
  const minutes = props.route.delay_minutes % 60
  if (hours > 0) {
    return `${hours}h ${minutes}m delay`
  }
  return `${minutes}m delay`
})
</script>

<template>
  <div
    class="bg-white border-2 rounded-xl p-6 shadow-sm transition-all"
    :class="
      isDelayed ? 'border-amber-200 bg-amber-50/30' : 'border-brand-primary/20 bg-brand-primary/5'
    "
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <div
          class="p-2 rounded-lg"
          :class="
            isDelayed ? 'bg-amber-100 text-amber-600' : 'bg-brand-primary/10 text-brand-primary'
          "
        >
          <Clock v-if="!isDelayed" class="w-5 h-5" />
          <AlertTriangle v-else class="w-5 h-5" />
        </div>
        <h3 class="font-bold text-text-primary uppercase tracking-tight">Estimated Arrival</h3>
      </div>
      <div
        v-if="isDelayed"
        class="flex items-center gap-1 bg-amber-100 text-amber-700 px-2 py-1 rounded text-[10px] font-black uppercase tracking-widest"
      >
        Delayed
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <div class="flex items-baseline gap-2">
        <span class="text-4xl font-black text-text-primary tracking-tighter">
          {{ formatDate(route.eta) }}
        </span>
        <span class="text-sm text-text-secondary font-medium">
          {{ formatFullDate(route.eta) }}
        </span>
      </div>

      <div v-if="isDelayed" class="mt-3 flex flex-col gap-2">
        <div class="flex items-center gap-2 text-amber-700 text-sm font-medium">
          <AlertTriangle class="w-4 h-4" />
          <span>{{ delayText }}</span>
        </div>
        <p class="text-xs text-amber-600/80 italic">
          Traffic or weather conditions may have caused a delay. Please prepare your warehouse
          accordingly.
        </p>
      </div>
      <div v-else class="mt-3">
        <p class="text-xs text-text-secondary">
          Everything is on schedule. Your shipment is expected to arrive on time.
        </p>
      </div>
    </div>

    <div
      class="mt-6 pt-4 border-t border-border-default flex items-center justify-between text-[10px] text-text-placeholder uppercase font-bold tracking-widest"
    >
      <span>Original ETA: {{ formatDate(route.original_eta || route.eta) }}</span>
      <div class="flex items-center gap-1">
        <Calendar class="w-3 h-3" />
        <span>Today</span>
      </div>
    </div>
  </div>
</template>
