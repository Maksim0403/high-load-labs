<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Truck, Loader2, AlertCircle } from 'lucide-vue-next'
import { vehiclesApi } from '@/api/vehicles'
import { routesApi } from '@/api/routes'
import type { VehicleCreate, Vehicle, TripRecord } from '@/types'
import { getErrorMessage } from '@/utils/errorHandler'
import { useNotificationStore } from '@/stores/notifications'
import BaseModal from '@/components/ui/BaseModal.vue'
import VehicleSpecsForm from '@/components/vehicle/VehicleSpecsForm.vue'
import MaintenanceAlerts from '@/components/vehicle/MaintenanceAlerts.vue'
import FuelInsights from '@/components/vehicle/FuelInsights.vue'
import TripHistoryTable from '@/components/vehicle/TripHistoryTable.vue'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const isEditing = computed(() => !!authStore.user?.vehicle?.id)

const vehicleForm = ref<VehicleCreate>({
  brand: '',
  model: '',
  license_plate: '',
  max_weight: 0,
  max_volume: 0,
  fuel_consumption: 0,
  fuel_price: 0,
  current_mileage: 0,
  maintenance_interval: 10000,
})

const isSaving = ref(false)
const isDeleting = ref(false)
const isLoading = ref(true)
const isHistoryLoading = ref(false)
const error = ref('')
const successMessage = ref('')
const isDeleteModalOpen = ref(false)
const displayLimit = ref(7)
const dbTripHistory = ref<TripRecord[]>([])

const visibleTrips = computed(() => {
  return dbTripHistory.value.slice(0, displayLimit.value)
})

const hasMoreTrips = computed(() => {
  return dbTripHistory.value.length > displayLimit.value
})

const showMore = () => {
  displayLimit.value += 10
}

const fetchTripHistory = async () => {
  isHistoryLoading.value = true
  try {
    const routes = await routesApi.getDriverRoutes()

    dbTripHistory.value = routes
      .filter((r) => r.completed_at || r.started_at || r.eta)
      .map((r) => {
        const distance = r.order?.distance || 0
        const fuelConsumption = vehicleForm.value.fuel_consumption || 0
        const fuelPrice = vehicleForm.value.fuel_price || 0

        const calculatedCost =
          r.fuel_cost !== null && r.fuel_cost !== undefined
            ? r.fuel_cost
            : Number((((distance * fuelConsumption) / 100) * fuelPrice).toFixed(2))

        return {
          date: r.completed_at || r.started_at || r.eta,
          routeId: r.id,
          distance: distance,
          fuel: fuelConsumption > 0 ? Number(((distance * fuelConsumption) / 100).toFixed(2)) : 0,
          cost: calculatedCost,
        }
      })
      .sort((a, b) => new Date(b.date!).getTime() - new Date(a.date!).getTime())
  } catch (err) {
    console.error('Failed to fetch trip history:', err)
  } finally {
    isHistoryLoading.value = false
  }
}

const fetchVehicle = async () => {
  isLoading.value = true
  try {
    const vehicles = await vehiclesApi.getMyVehicles()
    if (vehicles.length > 0) {
      const v = vehicles[0]
      if (v) {
        populateForm(v)
        if (authStore.user) {
          authStore.user.vehicle = v
          authStore.setUser({ ...authStore.user, vehicle: v })
        }
      }
    }
  } catch (err) {
    console.error('Failed to fetch vehicle:', err)
  } finally {
    isLoading.value = false
  }
}

const populateForm = (v: Vehicle) => {
  vehicleForm.value = {
    brand: v.brand,
    model: v.model,
    license_plate: v.license_plate,
    max_weight: v.max_weight,
    max_volume: v.max_volume,
    fuel_consumption: v.fuel_consumption,
    fuel_price: v.fuel_price,
    current_mileage: v.current_mileage,
    maintenance_interval: v.maintenance_interval,
  }
}

onMounted(async () => {
  await Promise.all([fetchVehicle(), fetchTripHistory()])
  if (authStore.isAuthenticated) {
    await notificationStore.fetchNotifications()
  }
})

const resetForm = () => {
  vehicleForm.value = {
    brand: '',
    model: '',
    license_plate: '',
    max_weight: 0,
    max_volume: 0,
    fuel_consumption: 0,
    fuel_price: 0,
    current_mileage: 0,
    maintenance_interval: 10000,
  }
}

const saveVehicle = async () => {
  error.value = ''
  successMessage.value = ''

  if (
    vehicleForm.value.fuel_consumption <= 0 ||
    vehicleForm.value.fuel_price <= 0 ||
    vehicleForm.value.current_mileage < 0 ||
    vehicleForm.value.max_weight <= 0 ||
    vehicleForm.value.max_volume <= 0 ||
    vehicleForm.value.maintenance_interval <= 0
  ) {
    error.value =
      'Please check the number format. Weight, volume, consumption, fuel price and interval must be greater than 0.'
    return
  }

  isSaving.value = true

  try {
    let updatedVehicle
    if (authStore.user?.vehicle?.id) {
      updatedVehicle = await vehiclesApi.updateVehicle(authStore.user.vehicle.id, {
        fuel_consumption: vehicleForm.value.fuel_consumption,
        fuel_price: vehicleForm.value.fuel_price,
        current_mileage: vehicleForm.value.current_mileage,
        maintenance_interval: vehicleForm.value.maintenance_interval,
      })
    } else {
      updatedVehicle = await vehiclesApi.createVehicle(vehicleForm.value)
    }

    if (authStore.user) {
      const updatedUser = { ...authStore.user, vehicle: updatedVehicle }
      authStore.setUser(updatedUser)
    }

    successMessage.value = 'Vehicle data saved successfully!'

    // Оновлюємо сповіщення, щоб побачити нові Maintenance Alerts відразу
    await notificationStore.fetchNotifications()

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    isSaving.value = false
  }
}

const deleteVehicle = async () => {
  if (!authStore.user?.vehicle?.id) return

  isDeleting.value = true
  error.value = ''

  try {
    await vehiclesApi.deleteVehicle(authStore.user.vehicle.id)

    if (authStore.user) {
      const updatedUser = { ...authStore.user, vehicle: undefined }
      authStore.setUser(updatedUser)
    }

    resetForm()
    isDeleteModalOpen.value = false
    successMessage.value = 'Vehicle removed successfully. You can now add a new one.'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = getErrorMessage(err)
    isDeleteModalOpen.value = false
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <div class="p-4 md:p-8 w-full font-roboto text-text-primary">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div class="flex items-center gap-4">
        <div class="p-3 bg-brand-primary/10 rounded-lg text-brand-primary shrink-0">
          <Truck class="w-8 h-8" />
        </div>
        <div>
          <h1 class="text-2xl md:text-[32px] font-bold leading-tight">My Vehicle</h1>
          <p class="text-text-secondary">Manage your vehicle details and maintenance schedules.</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <Loader2 class="w-12 h-12 text-brand-primary animate-spin mb-4" />
      <p class="text-text-secondary font-bold">LOADING VEHICLE DATA...</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-8">
      <VehicleSpecsForm
        v-model:vehicle-form="vehicleForm"
        :is-editing="isEditing"
        :is-saving="isSaving"
        :is-deleting="isDeleting"
        :error="error"
        :success-message="successMessage"
        @submit="saveVehicle"
        @delete="isDeleteModalOpen = true"
      />

      <div v-if="isEditing" class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <FuelInsights :last-trip-stats="authStore.lastTripStats" />

        <MaintenanceAlerts
          :current-mileage="Number(vehicleForm.current_mileage) || 0"
          :maintenance-interval="Number(vehicleForm.maintenance_interval) || 10000"
        />
      </div>

      <TripHistoryTable
        v-if="isEditing"
        :trips="visibleTrips"
        :has-more="hasMoreTrips"
        :is-loading="isHistoryLoading"
        @show-more="showMore"
      />
    </div>

    <BaseModal
      :show="isDeleteModalOpen"
      title="Remove Vehicle"
      confirm-text="Yes, Remove Vehicle"
      cancel-text="Cancel"
      variant="danger"
      @confirm="deleteVehicle"
      @cancel="isDeleteModalOpen = false"
    >
      <div class="p-4 bg-red-50 border border-red-100 rounded-lg flex items-start gap-3">
        <AlertCircle class="w-5 h-5 text-red-600 mt-0.5" />
        <p class="text-sm text-red-700">
          Are you sure you want to remove this vehicle? This action will permanently delete all
          associated mileage and consumption history.
        </p>
      </div>
    </BaseModal>
  </div>
</template>
