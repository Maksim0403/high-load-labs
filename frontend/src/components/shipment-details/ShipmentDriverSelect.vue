<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { User, UserPlus, Search, X, Loader2 } from 'lucide-vue-next'
import type { Route, User as UserType } from '@/types'
import apiClient from '@/api/axios'
import BaseButton from '@/components/ui/BaseButton.vue'
import { getErrorMessage } from '@/utils/errorHandler'

const props = defineProps<{
  route: Route | null
  orderId: number
  assignedDriver: UserType | null
}>()

const emit = defineEmits<{
  refresh: []
}>()

const showPicker = ref(false)
const searchQuery = ref('')
const drivers = ref<UserType[]>([])
const isLoading = ref(false)
const errorMessage = ref('')

const fetchDrivers = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await apiClient.get<UserType[]>('/dashboard/drivers')
    drivers.value = response.data
  } catch (err) {
    errorMessage.value = getErrorMessage(err)
    console.error('Failed to fetch drivers:', err)
  } finally {
    isLoading.value = false
  }
}

const filteredDrivers = computed(() => {
  if (!searchQuery.value) return drivers.value
  const q = searchQuery.value.toLowerCase()
  return drivers.value.filter(
    (d) => d.full_name?.toLowerCase().includes(q) || d.email.toLowerCase().includes(q),
  )
})

const handleAssign = async (driverId: number) => {
  errorMessage.value = ''
  try {
    if (props.route) {
      await apiClient.patch(`/dashboard/routes/${props.route.id}`, {
        driver_id: driverId,
      })
    } else {
      await apiClient.post('/dashboard/routes', {
        order_id: props.orderId,
        driver_id: driverId,
        eta: new Date().toISOString(),
      })
    }
    showPicker.value = false
    emit('refresh')
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
    console.error('Error assigning driver:', error)
  }
}

onMounted(fetchDrivers)
</script>

<template>
  <div class="flex items-center gap-3">
    <div
      v-if="assignedDriver"
      class="flex items-center gap-3 bg-bg-surface px-3 py-1.5 rounded-lg border border-border-default"
    >
      <div
        class="w-8 h-8 rounded-full bg-brand-primary/10 flex items-center justify-center flex-shrink-0"
      >
        <User class="w-4 h-4 text-brand-primary" />
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-bold text-text-primary leading-none">{{
          assignedDriver.full_name
        }}</span>
        <span class="text-[10px] text-text-secondary mt-1 uppercase font-black"
          >Driver ID: #{{ assignedDriver.id }}</span
        >
      </div>
    </div>

    <BaseButton @click="showPicker = true" variant="secondary" class="!h-10 !px-4 !w-auto text-xs">
      <UserPlus class="w-4 h-4 mr-2" />
      {{ assignedDriver ? 'CHANGE DRIVER' : 'ASSIGN DRIVER' }}
    </BaseButton>

    <Teleport to="body">
      <div
        v-if="showPicker"
        class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="showPicker = false"
      >
        <div
          class="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[80vh]"
        >
          <div class="px-6 py-4 border-b border-border-default flex justify-between items-center">
            <h3 class="text-lg font-bold">Select Driver</h3>
            <button
              @click="showPicker = false"
              class="text-text-placeholder hover:text-text-primary"
            >
              <X class="w-6 h-6" />
            </button>
          </div>

          <div class="p-4 bg-bg-surface border-b border-border-default">
            <div
              v-if="errorMessage"
              class="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 text-xs font-bold rounded flex items-center gap-2"
            >
              {{ errorMessage }}
            </div>
            <div class="relative">
              <Search
                class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-placeholder"
              />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search drivers by name or email..."
                class="w-full pl-10 pr-4 py-2 bg-white border border-border-default rounded-lg outline-none focus:border-brand-primary"
              />
            </div>
          </div>

          <div class="flex-1 overflow-y-auto p-2">
            <div v-if="isLoading" class="flex justify-center py-10">
              <Loader2 class="w-8 h-8 text-brand-primary animate-spin" />
            </div>
            <div
              v-else-if="filteredDrivers.length === 0"
              class="text-center py-10 text-text-placeholder"
            >
              No drivers found matching your search.
            </div>
            <div v-else class="space-y-1">
              <div
                v-for="driver in filteredDrivers"
                :key="driver.id"
                @click="handleAssign(driver.id)"
                class="w-full flex items-center gap-4 px-4 py-3 rounded-lg hover:bg-brand-primary/5 transition-colors text-left group cursor-pointer"
              >
                <div
                  class="w-10 h-10 rounded-full bg-bg-surface flex items-center justify-center font-bold text-brand-primary group-hover:bg-brand-primary group-hover:text-white transition-all flex-shrink-0"
                >
                  {{ driver.full_name?.charAt(0) }}
                </div>
                <div class="flex-1">
                  <p class="font-bold text-text-primary group-hover:text-brand-primary">
                    {{ driver.full_name }}
                  </p>
                  <p class="text-xs text-text-secondary">{{ driver.email }}</p>
                </div>
                <div class="text-[10px] font-black text-text-placeholder uppercase">
                  ID: #{{ driver.id }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
