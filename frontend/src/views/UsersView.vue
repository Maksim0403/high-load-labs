<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Search, Loader2 } from 'lucide-vue-next'
import { routesApi } from '@/api/routes'
import type { User } from '@/types'

const drivers = ref<User[]>([])
const isLoading = ref(true)
const searchQuery = ref('')

const fetchDrivers = async () => {
  isLoading.value = true
  try {
    drivers.value = await routesApi.getDrivers()
  } catch (error) {
    console.error('Failed to fetch drivers:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchDrivers)

const filteredDrivers = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return drivers.value

  return drivers.value.filter(
    (d) =>
      (d.full_name || '').toLowerCase().includes(query) || d.email.toLowerCase().includes(query),
  )
})
</script>

<template>
  <div class="p-8 font-roboto text-text-primary">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-[32px] font-bold">Drivers</h1>
        <p class="text-text-secondary">Manage platform drivers and their assigned vehicles</p>
      </div>
    </div>

    <div class="bg-bg-canvas border border-border-default rounded-lg overflow-hidden">
      <div class="p-4 border-b border-border-default flex gap-4">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-placeholder" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by name or email..."
            class="w-full pl-10 pr-4 py-2 bg-bg-surface border border-border-default rounded outline-none focus:border-brand-primary transition-colors"
          />
        </div>
      </div>

      <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
        <Loader2 class="w-10 h-10 text-brand-primary animate-spin mb-4" />
        <p class="text-text-secondary">Loading drivers...</p>
      </div>

      <table v-else class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-bg-surface border-b border-border-default">
            <th class="py-4 px-6 text-sm font-bold text-text-secondary uppercase tracking-wider">
              Driver
            </th>
            <th class="py-4 px-6 text-sm font-bold text-text-secondary uppercase tracking-wider">
              Vehicle
            </th>
            <th class="py-4 px-6 text-sm font-bold text-text-secondary uppercase tracking-wider">
              Contact
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-default">
          <tr
            v-for="driver in filteredDrivers"
            :key="driver.id"
            class="hover:bg-bg-surface transition-colors cursor-pointer"
          >
            <td class="py-4 px-6">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 bg-brand-primary text-white rounded-full flex items-center justify-center font-bold"
                >
                  {{ (driver.full_name || 'U').charAt(0) }}
                </div>
                <div>
                  <div class="font-bold text-text-primary">
                    {{ driver.full_name || 'Unknown User' }}
                  </div>
                  <div
                    class="text-[10px] bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded font-black uppercase"
                  >
                    ID: {{ driver.id }}
                  </div>
                </div>
              </div>
            </td>
            <td class="py-4 px-6">
              <div v-if="driver.vehicle" class="flex flex-col">
                <span class="text-sm font-bold text-text-primary">
                  {{ driver.vehicle.brand }} {{ driver.vehicle.model }}
                </span>
                <span class="text-xs text-text-secondary">{{ driver.vehicle.license_plate }}</span>
              </div>
              <span v-else class="text-xs text-text-placeholder italic">No vehicle assigned</span>
            </td>
            <td class="py-4 px-6">
              <div class="text-sm text-text-primary">{{ driver.email }}</div>
              <div class="text-xs text-text-secondary">{{ driver.phone_number }}</div>
            </td>
          </tr>
        </tbody>
      </table>

      <div
        v-if="!isLoading && drivers.length > 0 && filteredDrivers.length === 0"
        class="p-20 text-center flex flex-col items-center justify-center gap-4"
      >
        <div
          class="w-16 h-16 bg-bg-surface rounded-full flex items-center justify-center border border-border-default"
        >
          <Search class="w-8 h-8 text-text-placeholder" />
        </div>
        <div>
          <p class="text-lg font-bold text-text-primary">No results found</p>
          <p class="text-sm text-text-secondary">
            We couldn't find any driver matching "{{ searchQuery }}"
          </p>
        </div>
        <button
          @click="searchQuery = ''"
          class="text-sm font-bold text-brand-primary hover:underline"
        >
          Clear search
        </button>
      </div>

      <div
        v-if="!isLoading && drivers.length === 0"
        class="p-10 text-center text-text-secondary italic"
      >
        No drivers found in the system.
      </div>
    </div>
  </div>
</template>
