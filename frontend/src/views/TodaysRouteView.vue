<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { routesApi } from '@/api/routes'
import { useAuthStore } from '@/stores/auth'
import type { Route, DeliveryPhoto } from '@/types'
import { AlertCircle, CheckCircle2, Loader2, Truck, X } from 'lucide-vue-next'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseImageUpload from '@/components/ui/BaseImageUpload.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import { getErrorMessage } from '@/utils/errorHandler'
import { useRouter } from 'vue-router'

// New extracted components
import RouteDetailsModal from '@/components/route/RouteDetailsModal.vue'
import TripSummaryModal from '@/components/route/TripSummaryModal.vue'
import RouteItem from '@/components/route/RouteItem.vue'

const authStore = useAuthStore()
const router = useRouter()
const routes = ref<Route[]>([])
const routeStatuses = ref<Record<number, string>>({})
const isLoading = ref(true)
const isUpdating = ref<Record<number, boolean>>({})
const error = ref('')
const isPhotoModalOpen = ref(false)
const isSummaryModalOpen = ref(false)
const selectedRouteForPhoto = ref<number | null>(null)
const tripSummary = ref({ distance: 0, fuel: 0, cost: 0 })
const photos = ref<DeliveryPhoto[]>([])
const isFetchingPhotos = ref(false)
const selectedFullPhoto = ref<string | null>(null)
const photoToDelete = ref<number | null>(null)
const isDeleteModalOpen = ref(false)

const openPhotoUpload = (routeId: number) => {
  selectedRouteForPhoto.value = routeId
  isPhotoModalOpen.value = true
}

const fetchPhotos = async (routeId: number) => {
  isFetchingPhotos.value = true
  try {
    photos.value = await routesApi.getRoutePhotos(routeId)
  } catch (err) {
    console.error('Failed to fetch photos:', err)
  } finally {
    isFetchingPhotos.value = false
  }
}

const confirmDeletePhoto = (photoId: number) => {
  photoToDelete.value = photoId
  isDeleteModalOpen.value = true
}

const deletePhoto = async () => {
  if (!photoToDelete.value) return
  try {
    await routesApi.deleteRoutePhoto(photoToDelete.value)
    photos.value = photos.value.filter((p) => p.id !== photoToDelete.value)
    showToast('Photo deleted successfully')
  } catch (err) {
    showToast(getErrorMessage(err), 'error')
  } finally {
    isDeleteModalOpen.value = false
    photoToDelete.value = null
  }
}

const onPhotoUploaded = async () => {
  showToast('Photo uploaded successfully')
  if (selectedRouteForPhoto.value) {
    await fetchPhotos(selectedRouteForPhoto.value)
  }
}

const showTripSummary = (distance: number, fuel: number, cost: number) => {
  tripSummary.value = { distance, fuel, cost }
  isSummaryModalOpen.value = true
}

const toast = ref<{ show: boolean; message: string; type: 'success' | 'error' }>({
  show: false,
  message: '',
  type: 'success',
})

const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const isDetailsModalOpen = ref(false)
const selectedRoute = ref<Route | null>(null)

const openDetails = async (route: Route) => {
  selectedRoute.value = route
  isDetailsModalOpen.value = true
  await fetchPhotos(route.id)
}

const vehicle = computed(() => authStore.user?.vehicle)

const goToVehicle = () => {
  router.push('/driver/vehicle')
}

const currentStopId = computed(() => {
  const activeRoute = routes.value.find(
    (r) => (routeStatuses.value[r.id] || '').toLowerCase() !== 'delivered',
  )
  return activeRoute?.id
})

const fetchRoutes = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const data = await routesApi.getTodayRoutes()
    routes.value = data

    await Promise.all(
      data.map(async (route) => {
        try {
          const statuses = await routesApi.getRouteStatuses(route.id)
          if (statuses.length > 0) {
            const lastStatus = statuses[statuses.length - 1]
            routeStatuses.value[route.id] = lastStatus?.status ?? ''
          } else {
            routeStatuses.value[route.id] = ''
          }
        } catch (err) {
          console.error(`Failed to fetch status for route ${route.id}:`, err)
          routeStatuses.value[route.id] = ''
        }
      }),
    )
  } catch (err: unknown) {
    console.error('Failed to fetch routes:', err)
    error.value = getErrorMessage(err)
  } finally {
    isLoading.value = false
  }
}

const updateStatus = async (routeId: number, status: string) => {
  if (isUpdating.value[routeId]) return
  isUpdating.value[routeId] = true
  try {
    await routesApi.addRouteStatus(routeId, { status })
    routeStatuses.value[routeId] = status
    routes.value = await routesApi.getTodayRoutes()
    showToast(`Status updated to ${status.replace('_', ' ')}`)

    if (status.toLowerCase() === 'delivered') {
      const updatedRoute = routes.value.find((r) => r.id === routeId)
      if (updatedRoute && updatedRoute.fuel_cost !== null) {
        const distance = updatedRoute.order?.distance || 0
        const fuelConsumption = authStore.user?.vehicle?.fuel_consumption || 0

        const stats = {
          distance: distance,
          fuel: Number(((distance * fuelConsumption) / 100).toFixed(2)),
          cost: updatedRoute.fuel_cost || 0,
        }

        showTripSummary(stats.distance, stats.fuel, stats.cost)
        authStore.setLastTripStats(stats)
        authStore.addTripToHistory({ ...stats, routeId })
      }
    }
  } catch (err: unknown) {
    console.error('Failed to update status:', err)
    showToast(getErrorMessage(err), 'error')
  } finally {
    isUpdating.value[routeId] = false
  }
}

const getStatusColor = (routeId: number, buttonStatus: string) => {
  const current = (routeStatuses.value[routeId] || '').toLowerCase()
  const target = buttonStatus.toLowerCase()
  if (current === target) {
    return target === 'delivered' ? 'bg-green-500 text-white' : 'bg-brand-primary text-white'
  }
  if (!isStatusDisabled(routeId, buttonStatus)) {
    return 'bg-brand-primary/10 text-brand-primary border-brand-primary border'
  }
  return 'text-text-placeholder bg-bg-surface'
}

const isStatusDisabled = (routeId: number, targetStatus: string) => {
  const current = routeStatuses.value[routeId]
  if (isUpdating.value[routeId]) return true

  const transitions: Record<string, string> = {
    '': 'assigned',
    assigned: 'loaded',
    loaded: 'in_transit',
    in_transit: 'delivered',
    delivered: 'none',
  }

  const normalizedCurrent = current?.toLowerCase() || ''
  const normalizedTarget = targetStatus.toLowerCase()

  return transitions[normalizedCurrent] !== normalizedTarget
}

onMounted(fetchRoutes)
</script>

<template>
  <div class="p-4 md:p-8 bg-bg-surface min-h-screen font-roboto text-text-primary">
    <div
      class="mb-6 md:mb-10 flex flex-col md:flex-row justify-between items-start md:items-end border-b border-border-default pb-6 gap-6"
    >
      <div>
        <div class="flex items-center gap-4 mb-1 flex-wrap">
          <h1 class="text-2xl md:text-[32px] font-bold text-text-primary">Daily Route List</h1>
          <span
            v-if="routes.length > 0"
            class="bg-brand-primary text-white text-[10px] md:text-xs font-black px-3 py-1 rounded-full uppercase tracking-widest"
          >
            {{ routes.length }} STOPS TODAY
          </span>
        </div>
        <p class="text-text-secondary font-medium">
          Driver Console • {{ new Date().toLocaleDateString('uk-UA') }}
        </p>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
        <div
          v-if="vehicle"
          @click="goToVehicle"
          class="bg-white px-5 py-3 rounded-lg border border-border-default shadow-sm flex items-center gap-4 flex-1 md:flex-initial cursor-pointer hover:border-brand-primary transition-colors group"
        >
          <div
            class="w-10 h-10 bg-brand-primary/10 rounded-full flex items-center justify-center group-hover:bg-brand-primary group-hover:text-white transition-colors"
          >
            <Truck class="w-5 h-5 text-brand-primary group-hover:text-white" />
          </div>
          <div>
            <p
              class="text-[10px] font-black text-text-placeholder uppercase tracking-tighter leading-none mb-1"
            >
              Assigned Vehicle
            </p>
            <p class="text-sm font-bold text-text-primary leading-none">
              {{ vehicle.brand }} {{ vehicle.model }}
            </p>
            <p class="text-[11px] font-medium text-text-secondary mt-1">
              {{ vehicle.license_plate }} • {{ vehicle.max_weight }}kg limit
            </p>
          </div>
        </div>
        <div
          v-else
          class="bg-orange-50 px-5 py-3 rounded-lg border border-orange-200 flex items-center gap-4 flex-1 md:flex-initial"
        >
          <AlertCircle class="w-5 h-5 text-orange-500" />
          <div class="flex-1">
            <p
              class="text-[10px] font-black text-orange-400 uppercase tracking-tighter leading-none mb-1"
            >
              Warning
            </p>
            <p class="text-sm font-bold text-orange-700 leading-none">No vehicle assigned</p>
          </div>
          <BaseButton variant="secondary" size="sm" @click="goToVehicle">Add Vehicle</BaseButton>
        </div>
      </div>
    </div>

    <div
      v-if="error"
      class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700"
    >
      <AlertCircle class="w-5 h-5 flex-shrink-0" />
      <div class="flex-1">
        <p class="font-bold">Error loading routes</p>
        <p class="text-sm">{{ error }}</p>
      </div>
      <button
        @click="fetchRoutes"
        class="px-4 py-2 bg-white border border-red-200 rounded-md text-sm font-bold hover:bg-red-50 transition-colors"
      >
        Retry
      </button>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-32">
      <Loader2 class="w-12 h-12 text-brand-primary animate-spin mb-4" />
      <p class="text-text-secondary font-bold tracking-widest">LOADING ROUTES...</p>
    </div>

    <BaseEmptyState
      v-else-if="routes.length === 0"
      :icon="Truck"
      title="No routes assigned yet"
      description="Check back later or contact your manager."
    />

    <div v-else class="space-y-6">
      <RouteItem
        v-for="(route, index) in routes"
        :key="route.id"
        :route="route"
        :index="index"
        :status="routeStatuses[route.id] || ''"
        :is-current="route.id === currentStopId"
        :is-updating="!!isUpdating[route.id]"
        :is-status-disabled="isStatusDisabled"
        :get-status-color="getStatusColor"
        @open-photo-upload="openPhotoUpload"
        @open-details="openDetails"
        @update-status="updateStatus"
      />
    </div>

    <RouteDetailsModal
      :show="isDetailsModalOpen"
      :route="selectedRoute"
      :status="selectedRoute ? routeStatuses[selectedRoute.id] || '' : ''"
      :photos="photos"
      :is-fetching-photos="isFetchingPhotos"
      @close="isDetailsModalOpen = false"
      @delete-photo="confirmDeletePhoto"
      @preview-photo="selectedFullPhoto = $event"
    />

    <BaseModal
      :show="isPhotoModalOpen"
      @cancel="isPhotoModalOpen = false"
      title="Upload Photo"
      message=""
    >
      <BaseImageUpload
        v-if="selectedRouteForPhoto"
        :route-id="selectedRouteForPhoto"
        @uploaded="onPhotoUploaded"
        @close="isPhotoModalOpen = false"
      />
    </BaseModal>

    <BaseModal :show="!!selectedFullPhoto" @cancel="selectedFullPhoto = null" title="Photo Preview">
      <div class="flex justify-center">
        <img
          :src="selectedFullPhoto || ''"
          class="max-w-full max-h-[70vh] rounded-lg shadow-xl"
          alt="Full size photo"
        />
      </div>
      <template #footer>
        <BaseButton variant="primary" @click="selectedFullPhoto = null" class="w-full">
          Close
        </BaseButton>
      </template>
    </BaseModal>

    <TripSummaryModal
      :show="isSummaryModalOpen"
      :summary="tripSummary"
      @close="isSummaryModalOpen = false"
    />

    <BaseModal
      :show="isDeleteModalOpen"
      title="Delete Photo"
      message="Are you sure you want to delete this photo? This action cannot be undone."
      confirm-text="Delete"
      variant="danger"
      @confirm="deletePhoto"
      @cancel="isDeleteModalOpen = false"
    />

    <Transition
      enter-active-class="transform transition ease-out duration-300"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="toast.show"
        class="fixed bottom-6 right-6 z-[100] flex items-center gap-3 px-6 py-4 rounded-xl shadow-2xl border pointer-events-auto"
        :class="
          toast.type === 'success'
            ? 'bg-green-600 border-green-500 text-white'
            : 'bg-red-600 border-red-500 text-white'
        "
      >
        <CheckCircle2 v-if="toast.type === 'success'" class="w-5 h-5" />
        <AlertCircle v-else class="w-5 h-5" />
        <p class="text-sm font-bold tracking-wide uppercase">{{ toast.message }}</p>
        <button @click="toast.show = false" class="ml-2 hover:opacity-70">
          <X class="w-4 h-4" />
        </button>
      </div>
    </Transition>
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
