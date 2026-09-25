<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  Package,
  Truck,
  User,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  Loader2,
} from 'lucide-vue-next'
import { routesApi } from '@/api/routes'
import { ordersApi } from '@/api/orders'
import type { Order, User as UserType, Vehicle } from '@/types'
import { getErrorMessage } from '@/utils/errorHandler'

const unassignedOrders = ref<Order[]>([])
const drivers = ref<(UserType & { vehicle?: Vehicle })[]>([])
const isLoadingOrders = ref(true)
const isLoadingDrivers = ref(true)

const selectedOrder = ref<Order | null>(null)
const selectedDriver = ref<(UserType & { vehicle?: Vehicle }) | null>(null)
const selectedEta = ref('')
const selectedVehicleId = ref<number | null>(null)

watch(selectedDriver, (driver) => {
  if (driver?.vehicle) {
    selectedVehicleId.value = driver.vehicle.id
  } else {
    selectedVehicleId.value = null
  }
})

const setDefaultEta = () => {
  const date = new Date()
  date.setHours(date.getHours() + 3)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  selectedEta.value = `${year}-${month}-${day}T${hours}:${minutes}`
}

onMounted(async () => {
  setDefaultEta()
  try {
    unassignedOrders.value = await ordersApi.getUnassignedOrders()
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  } finally {
    isLoadingOrders.value = false
  }

  try {
    const fetchedDrivers = await routesApi.getDrivers()
    drivers.value = fetchedDrivers as (UserType & { vehicle?: Vehicle })[]
  } catch (error) {
    console.error('Failed to fetch drivers:', error)
  } finally {
    isLoadingDrivers.value = false
  }
})

const isSubmitting = ref(false)
const assignmentSuccess = ref(false)
const assignmentError = ref('')

const canAssign = computed(() => {
  if (!selectedOrder.value || !selectedDriver.value?.vehicle || !selectedEta.value) return false
  return (
    selectedOrder.value.weight <= selectedDriver.value.vehicle.max_weight &&
    selectedVehicleId.value !== null
  )
})

const handleAssign = async () => {
  if (
    !selectedOrder.value ||
    !selectedDriver.value ||
    !selectedVehicleId.value ||
    !selectedEta.value ||
    !canAssign.value
  )
    return

  isSubmitting.value = true
  assignmentError.value = ''
  try {
    const isoEta = new Date(selectedEta.value).toISOString()
    await routesApi.assignRoute(
      selectedOrder.value.id,
      selectedDriver.value.id,
      selectedVehicleId.value,
      isoEta,
    )

    assignmentSuccess.value = true
    const assignedOrderId = selectedOrder.value.id

    setTimeout(() => {
      unassignedOrders.value = unassignedOrders.value.filter((o) => o.id !== assignedOrderId)
      selectedOrder.value = null
      selectedDriver.value = null
      selectedVehicleId.value = null
      setDefaultEta()
      assignmentSuccess.value = false
    }, 2000)
  } catch (error: unknown) {
    console.error('Assignment failed', error)
    assignmentError.value = getErrorMessage(error)

    try {
      unassignedOrders.value = await ordersApi.getUnassignedOrders()
    } catch (e) {
      console.error('Failed to refresh orders:', e)
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="p-8 font-roboto text-text-primary">
    <div class="mb-8">
      <h1 class="text-[32px] font-bold">Route Assignment</h1>
      <p class="text-text-secondary">Assign pending orders to available drivers and vehicles</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Orders Column -->
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold flex items-center gap-2">
            <Package class="w-5 h-5 text-brand-primary" />
            Unassigned Orders
          </h2>
          <span
            class="bg-bg-surface px-3 py-1 rounded-full text-xs font-bold border border-border-default"
          >
            {{ unassignedOrders.length }} Pending
          </span>
        </div>

        <div class="space-y-3">
          <div
            v-if="isLoadingOrders"
            class="flex flex-col items-center justify-center py-12 bg-bg-canvas border border-dashed border-border-default rounded-lg"
          >
            <Loader2 class="w-8 h-8 text-brand-primary animate-spin mb-2" />
            <p class="text-text-secondary text-sm">Loading orders...</p>
          </div>

          <div
            v-else-if="unassignedOrders.length === 0"
            class="flex flex-col items-center justify-center py-12 bg-bg-canvas border border-dashed border-border-default rounded-lg"
          >
            <Package class="w-8 h-8 text-text-placeholder mb-2" />
            <p class="text-text-secondary text-sm">No unassigned orders found</p>
          </div>

          <template v-else>
            <div
              v-for="order in unassignedOrders"
              :key="order.id"
              @click="selectedOrder = order"
              class="p-4 border rounded-lg transition-all cursor-pointer"
              :class="[
                selectedOrder?.id === order.id
                  ? 'border-brand-primary bg-blue-50/50'
                  : 'border-border-default bg-bg-canvas hover:border-text-placeholder',
              ]"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-lg">{{ order.title }}</h3>
                <span class="text-sm font-bold text-brand-primary">{{ order.weight }} kg</span>
              </div>

              <div class="flex items-center gap-4 text-sm text-text-secondary">
                <div class="flex items-center gap-1">
                  <div class="w-2 h-2 rounded-full bg-orange-400"></div>
                  From: {{ order.origin_address?.split(',')[0] || 'N/A' }}
                </div>
                <ChevronRight class="w-3 h-3" />
                <div class="flex items-center gap-1">
                  <div class="w-2 h-2 rounded-full bg-green-500"></div>
                  To: {{ order.destination_address?.split(',')[0] || 'N/A' }}
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Drivers Column -->
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold flex items-center gap-2">
            <Truck class="w-5 h-5 text-brand-primary" />
            Available Drivers
          </h2>
        </div>

        <div
          v-if="isLoadingDrivers"
          class="flex flex-col items-center justify-center py-12 bg-bg-canvas border border-dashed border-border-default rounded-lg"
        >
          <Loader2 class="w-8 h-8 text-brand-primary animate-spin mb-2" />
          <p class="text-text-secondary text-sm">Loading drivers...</p>
        </div>

        <div
          v-else-if="!selectedOrder"
          class="bg-bg-surface border border-dashed border-border-default rounded-lg p-12 text-center"
        >
          <Package class="w-12 h-12 text-text-placeholder mx-auto mb-4" />
          <p class="text-text-secondary">Select an order first to see compatible drivers</p>
        </div>

        <div
          v-else-if="drivers.length === 0"
          class="bg-bg-surface border border-dashed border-border-default rounded-lg p-12 text-center"
        >
          <User class="w-12 h-12 text-text-placeholder mx-auto mb-4" />
          <p class="text-text-secondary">No drivers found in the system.</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="driver in drivers"
            :key="driver.id"
            @click="selectedDriver = driver"
            class="p-4 border rounded-lg transition-all cursor-pointer"
            :class="[
              selectedDriver?.id === driver.id
                ? 'border-brand-primary bg-blue-50/50'
                : 'border-border-default bg-bg-canvas hover:border-text-placeholder',
            ]"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-12 h-12 bg-bg-surface rounded-full flex items-center justify-center border border-border-default"
              >
                <User class="w-6 h-6 text-text-secondary" />
              </div>
              <div class="flex-1">
                <div class="flex justify-between items-start">
                  <div>
                    <h3 class="font-bold">{{ driver.full_name }}</h3>
                    <p v-if="driver.vehicle" class="text-xs text-text-secondary">
                      {{ driver.vehicle?.brand }} {{ driver.vehicle?.model }} •
                      {{ driver.vehicle?.license_plate }}
                    </p>
                    <p v-else class="text-xs text-orange-500 font-bold italic">
                      No vehicle assigned
                    </p>
                  </div>
                  <div v-if="driver.vehicle" class="text-right text-xs">
                    <span class="font-bold text-text-primary"
                      >Cap: {{ driver.vehicle?.max_weight }} kg</span
                    >
                  </div>
                </div>

                <div
                  v-if="
                    selectedOrder &&
                    driver.vehicle &&
                    selectedOrder.weight > driver.vehicle.max_weight
                  "
                  class="mt-2 flex items-center gap-1 text-red-500 text-xs font-bold"
                >
                  <AlertCircle class="w-3 h-3" />
                  Order too heavy for this vehicle
                </div>
              </div>
            </div>
          </div>

          <!-- Assignment Form -->
          <div
            v-if="selectedDriver"
            class="mt-8 p-6 bg-bg-canvas border border-border-default rounded-lg shadow-sm"
          >
            <h3 class="font-bold mb-4 uppercase text-[10px] tracking-wider text-text-secondary">
              Assignment Summary
            </h3>

            <div class="flex flex-col sm:flex-row items-center gap-4 mb-6">
              <div
                class="w-full sm:flex-1 p-3 bg-bg-surface rounded border border-border-default text-sm"
              >
                <div
                  class="text-[10px] text-text-secondary mb-1 uppercase font-black tracking-tighter"
                >
                  Order
                </div>
                <div class="font-bold text-brand-primary">{{ selectedOrder?.title }}</div>
              </div>
              <ChevronRight class="w-4 h-4 text-text-placeholder rotate-90 sm:rotate-0" />
              <div
                class="w-full sm:flex-1 p-3 bg-bg-surface rounded border border-border-default text-sm"
              >
                <div
                  class="text-[10px] text-text-secondary mb-1 uppercase font-black tracking-tighter"
                >
                  Driver
                </div>
                <div class="font-bold text-brand-primary">{{ selectedDriver.full_name }}</div>
              </div>
            </div>

            <div class="mb-6">
              <label
                class="block text-[10px] text-text-secondary mb-2 uppercase font-black tracking-widest"
                >Estimated Arrival Time (ETA)</label
              >
              <input
                v-model="selectedEta"
                type="datetime-local"
                class="w-full p-3 bg-bg-surface border border-border-default rounded-lg focus:border-brand-primary outline-none transition-colors font-bold text-sm"
              />
            </div>

            <div
              v-if="assignmentError"
              class="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 text-sm font-bold rounded flex items-center gap-2"
            >
              <AlertCircle class="w-4 h-4" />
              {{ assignmentError }}
            </div>

            <button
              @click="handleAssign"
              :disabled="!canAssign || isSubmitting || assignmentSuccess"
              class="w-full py-4 rounded font-bold flex items-center justify-center gap-2 transition-all"
              :class="[
                assignmentSuccess
                  ? 'bg-green-500 text-white'
                  : canAssign
                    ? 'bg-brand-primary hover:bg-btn-primary-hover text-white'
                    : 'bg-border-default text-text-placeholder cursor-not-allowed',
              ]"
            >
              <template v-if="isSubmitting">
                <div
                  class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"
                ></div>
                Assigning...
              </template>
              <template v-else-if="assignmentSuccess">
                <CheckCircle2 class="w-5 h-5" />
                Successfully Assigned!
              </template>
              <template v-else>Confirm Assignment</template>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
