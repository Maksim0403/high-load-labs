<script setup lang="ts">
import { Fuel } from 'lucide-vue-next'

defineProps<{
  lastTripStats: { fuel: number; distance: number; cost: number } | null
}>()
</script>

<template>
  <section class="bg-bg-canvas border border-border-default rounded-lg p-6 shadow-sm">
    <h2 class="text-xl font-bold mb-6 flex items-center gap-2">
      <Fuel class="w-5 h-5 text-brand-primary" /> Fuel Consumption
    </h2>

    <div class="space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="p-4 bg-bg-surface rounded border border-border-default">
          <p class="text-text-secondary text-xs font-bold uppercase tracking-wider mb-1">
            Last Route Consumption
          </p>
          <div class="flex items-end gap-2">
            <span class="text-2xl font-bold text-text-primary">{{
              lastTripStats?.fuel || '--'
            }}</span>
            <span class="text-text-secondary pb-1">L</span>
          </div>
        </div>

        <div class="p-4 bg-bg-surface rounded border border-border-default">
          <p class="text-text-secondary text-xs font-bold uppercase tracking-wider mb-1">
            Last Route Cost
          </p>
          <div class="flex items-end gap-2">
            <span class="text-2xl font-bold text-text-primary">{{
              lastTripStats?.cost || '--'
            }}</span>
            <span class="text-text-secondary pb-1">UAH</span>
          </div>
        </div>
      </div>

      <div
        v-if="lastTripStats"
        class="p-4 bg-brand-primary/5 rounded border border-brand-primary/10"
      >
        <p class="text-text-secondary text-xs font-bold uppercase tracking-wider mb-1">
          Distance Covered
        </p>
        <div class="flex items-end gap-2">
          <span class="text-2xl font-bold text-brand-primary">{{ lastTripStats.distance }}</span>
          <span class="text-brand-primary/70 pb-1 font-medium">km</span>
        </div>
      </div>

      <p v-if="!lastTripStats" class="text-sm text-text-secondary italic text-center py-4">
        Fuel statistics will be calculated automatically after your first completed route.
      </p>
    </div>
  </section>
</template>
