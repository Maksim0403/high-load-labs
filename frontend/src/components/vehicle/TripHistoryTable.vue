<script setup lang="ts">
import { Clock, Loader2 } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import { formatDate, formatTime } from '@/utils/date'
import type { TripRecord } from '@/types'

defineProps<{
  trips: TripRecord[]
  hasMore: boolean
  isLoading?: boolean
}>()
</script>

<template>
  <section
    class="bg-bg-canvas border border-border-default rounded-lg p-4 md:p-6 shadow-sm overflow-hidden"
  >
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg md:text-xl font-bold flex items-center gap-2">
        <Clock class="w-5 h-5 text-brand-primary" /> Recent Trips History
      </h2>
      <div v-if="isLoading" class="flex items-center gap-2 text-brand-primary text-sm font-bold">
        <Loader2 class="w-4 h-4 animate-spin" />
        REFRESHING...
      </div>
    </div>

    <div v-if="trips.length > 0" class="overflow-x-auto -mx-4 px-4 md:mx-0 md:px-0">
      <table class="w-full text-left min-w-[700px]">
        <thead>
          <tr
            class="text-[10px] font-black text-text-placeholder uppercase tracking-widest border-b border-border-default"
          >
            <th class="pb-3">Date</th>
            <th class="pb-3">Route ID</th>
            <th class="pb-3 text-right">Distance</th>
            <th class="pb-3 text-right">Fuel Spent</th>
            <th class="pb-3 text-right">Fuel Cost</th>
            <th class="pb-3 text-right">Efficiency</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-default">
          <tr v-for="trip in trips" :key="trip.routeId + trip.date" class="text-sm">
            <td class="py-4 text-text-secondary">
              {{ formatDate(trip.date) }}
              <span class="text-[10px] ml-1 opacity-50">
                {{ formatTime(trip.date) }}
              </span>
            </td>
            <td class="py-4 font-bold">#{{ trip.routeId }}</td>
            <td class="py-4 text-right font-medium">{{ trip.distance }} km</td>

            <td class="py-4 text-right">
              <span class="bg-brand-primary/5 text-brand-primary px-2 py-1 rounded font-bold">
                {{ Number(trip.fuel || 0).toFixed(2) }} L
              </span>
            </td>

            <td class="py-4 text-right">
              <span class="bg-brand-primary/10 text-brand-primary px-2 py-1 rounded font-bold">
                {{ Number(trip.cost || 0).toFixed(2) }} UAH
              </span>
            </td>

            <td class="py-4 text-right font-medium text-text-secondary">
              {{
                trip.distance > 0
                  ? ((Number(trip.fuel || 0) / Number(trip.distance)) * 100).toFixed(1)
                  : '0.0'
              }}
              <span class="text-[10px]">L/100km</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="hasMore" class="mt-6 text-center">
        <BaseButton variant="secondary" size="sm" @click="$emit('showMore')" class="px-8">
          Show More History
        </BaseButton>
      </div>
    </div>
    <div v-else class="text-center py-10 text-text-secondary italic">
      No trip history recorded yet. Complete your first route to see stats here.
    </div>
  </section>
</template>
