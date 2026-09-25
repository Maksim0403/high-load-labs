<script setup lang="ts">
import { Package, Clock, ExternalLink } from 'lucide-vue-next'

export interface Delivery {
  id: string
  orderId?: string
  title: string
  status: string
  estimatedArrival: string
}

defineProps<{
  deliveries: Delivery[]
  title?: string
}>()

const emit = defineEmits<{
  select: [delivery: Delivery]
  viewAll: []
}>()
</script>

<template>
  <div class="bg-bg-canvas border border-border-default rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-text-primary">{{ title || 'Active Deliveries' }}</h3>
      <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
        {{ deliveries.length }} Recent
      </span>
    </div>

    <div
      v-if="deliveries.length === 0"
      class="flex flex-col items-center justify-center py-12 text-center"
    >
      <div class="w-16 h-16 bg-bg-surface rounded-full flex items-center justify-center mb-4">
        <Package class="w-8 h-8 text-text-placeholder" />
      </div>
      <p class="text-text-primary font-medium">No active deliveries</p>
      <p class="text-sm text-text-placeholder max-w-[250px] mx-auto">
        You don't have any active shipments at the moment.
      </p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="delivery in deliveries"
        :key="delivery.id"
        @click="emit('select', delivery)"
        class="flex items-center justify-between p-4 bg-bg-surface rounded-lg border border-border-default hover:border-primary hover:shadow-md transition-all cursor-pointer group"
      >
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
            <Package class="w-5 h-5 text-primary" />
          </div>
          <div>
            <p
              class="text-sm font-semibold text-text-primary group-hover:text-primary transition-colors"
            >
              {{ delivery.title }}
            </p>
            <div class="flex items-center gap-2 text-xs text-text-placeholder mt-1">
              <Clock class="w-3.3 h-3.3" />
              <span>Est. arrival: {{ delivery.estimatedArrival }}</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <span
            class="text-xs font-medium px-2 py-1 rounded bg-bg-canvas border border-border-default text-text-secondary capitalize"
          >
            {{ delivery.status }}
          </span>
          <ExternalLink class="w-4 h-4 text-text-placeholder group-hover:text-primary" />
        </div>
      </div>
    </div>

    <button
      v-if="deliveries.length > 0"
      @click="emit('viewAll')"
      class="w-full mt-6 py-2.5 text-sm font-bold text-brand-primary hover:bg-brand-primary/5 transition-all border border-brand-primary/20 rounded-md"
    >
      View all
    </button>
  </div>
</template>
