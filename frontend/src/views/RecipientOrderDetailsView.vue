<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, CheckCircle2, Navigation, Trash2 } from 'lucide-vue-next'
import type { Order, Route, User } from '@/types'
import { ordersApi } from '@/api/orders'
import { routesApi } from '@/api/routes'
import ShipmentPackageDetails from '@/components/shipment-details/ShipmentPackageDetails.vue'
import ShipmentStatusTimeline from '@/components/shipment-details/ShipmentStatusTimeline.vue'
import ShipmentETACard from '@/components/shipment-details/ShipmentETACard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const routePath = useRoute()
const router = useRouter()
const orderId = Number(routePath.params.id)

const order = ref<Order | null>(null)
const route = ref<Route | null>(null)
const assignedDriver = ref<User | null>(null)
const isLoading = ref(true)
const error = ref('')

const isCancelling = ref(false)
const isConfirming = ref(false)
const isRefusing = ref(false)
const showCancelModal = ref(false)
const showConfirmModal = ref(false)
const showRefuseModal = ref(false)
const showErrorModal = ref(false)
const modalErrorMessage = ref('')

const isInTransit = computed(() => {
  if (!route.value?.statuses) return false
  return (
    route.value.statuses.some((s) => s.status === 'in_transit') &&
    !route.value.statuses.some(
      (s) => s.status === 'delivered' || s.status === 'failed' || s.status === 'cancelled',
    )
  )
})

const fetchData = async () => {
  isLoading.value = true
  error.value = ''
  try {
    order.value = await ordersApi.getOrder(orderId)

    try {
      const routes = await routesApi.getDriverRoutes()
      const routeData = routes.find((r) => r.order_id === orderId)

      if (routeData) {
        try {
          const statuses = await routesApi.getRouteStatuses(routeData.id)
          routeData.statuses = statuses
        } catch (err) {
          console.warn('Could not fetch route statuses', err)
        }

        route.value = routeData

        if (routeData.driver_id) {
          try {
            const drivers = await routesApi.getDrivers()
            const driver = drivers.find((d) => d.id === routeData.driver_id)
            if (driver) {
              assignedDriver.value = driver
            }
          } catch (err) {
            console.warn('Could not fetch driver info', err)
          }
        }
      }
    } catch (err) {
      console.warn('Route info not available for this order yet.', err)
    }
  } catch (err) {
    console.error('Failed to fetch order details:', err)
    error.value = "Failed to load order details. It might not exist or you don't have access."
  } finally {
    isLoading.value = false
  }
}

const handleCancel = async () => {
  if (!order.value) return
  showCancelModal.value = false
  isCancelling.value = true
  try {
    await ordersApi.cancelOrder(order.value.id)
    await fetchData()
  } catch (err) {
    console.error('Failed to cancel order:', err)
    modalErrorMessage.value = 'Failed to cancel order. It might already be in progress.'
    showErrorModal.value = true
  } finally {
    isCancelling.value = false
  }
}

const handleRefuse = async () => {
  if (!order.value) return
  showRefuseModal.value = false
  isRefusing.value = true
  try {
    await ordersApi.cancelOrder(order.value.id)
    await fetchData()
  } catch (err) {
    console.error('Failed to refuse cargo:', err)
    modalErrorMessage.value = 'Failed to refuse cargo. Please try again later.'
    showErrorModal.value = true
  } finally {
    isRefusing.value = false
  }
}

const handleConfirmReceipt = async () => {
  if (!order.value) return
  showConfirmModal.value = false
  isConfirming.value = true
  try {
    await ordersApi.confirmReceipt(order.value.id)
    await fetchData()
  } catch (err) {
    console.error('Failed to confirm receipt:', err)
    modalErrorMessage.value = 'Failed to confirm receipt. Please try again later.'
    showErrorModal.value = true
  } finally {
    isConfirming.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div v-if="isLoading" class="flex justify-center items-center min-h-[400px]">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
  </div>

  <div v-else-if="error || !order" class="p-8 text-center">
    <div class="bg-red-50 border border-red-200 text-red-600 p-4 rounded mb-4 max-w-2xl mx-auto">
      {{ error || 'Order not found' }}
    </div>
    <BaseButton @click="router.back()">Go Back</BaseButton>
  </div>

  <div v-else class="p-4 md:p-8 font-roboto max-w-7xl mx-auto">
    <button
      class="flex items-center gap-1 text-text-secondary text-[10px] md:text-xs mb-4 hover:text-text-primary transition-colors uppercase font-black tracking-widest"
      @click="router.back()"
    >
      <ArrowLeft class="w-3 h-3" /> BACK TO MY ORDERS
    </button>

    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-[32px] font-bold text-text-primary leading-tight">
          Order: {{ order.title }}
        </h1>
        <div class="flex items-center gap-2 mt-2">
          <div
            class="flex items-center gap-1.5 px-2 py-0.5 rounded font-black uppercase tracking-widest text-[10px]"
            :class="
              order.status.toUpperCase() === 'COMPLETED'
                ? 'bg-green-100 text-green-600'
                : 'bg-brand-primary/10 text-brand-primary'
            "
          >
            <CheckCircle2 v-if="order.status.toUpperCase() === 'COMPLETED'" class="w-3 h-3" />
            {{ order.status }}
          </div>
          <span class="text-[10px] text-text-placeholder font-medium uppercase tracking-tighter">
            Created: {{ new Date(order.created_at).toLocaleDateString() }}
          </span>
          <span
            v-if="order.received_at"
            class="text-[10px] text-green-600 font-medium uppercase tracking-tighter"
          >
            Received: {{ new Date(order.received_at).toLocaleDateString() }}
          </span>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <BaseButton
          v-if="order.status.toUpperCase() === 'PENDING'"
          variant="secondary"
          class="text-red-500 border-red-200 hover:bg-red-50 px-6 py-2 transition-colors text-xs font-bold"
          @click="showCancelModal = true"
          :disabled="isCancelling"
        >
          <Trash2 class="w-3.5 h-3.5 mr-2" />
          {{ isCancelling ? 'Cancelling...' : 'Cancel Order' }}
        </BaseButton>

        <BaseButton
          v-if="order.status.toUpperCase() === 'IN_PROGRESS'"
          variant="secondary"
          class="text-orange-600 border-orange-200 hover:bg-orange-50 px-6 py-2 transition-colors text-xs font-bold"
          @click="showRefuseModal = true"
          :disabled="isRefusing"
        >
          {{ isRefusing ? 'Refusing...' : 'Refuse Cargo' }}
        </BaseButton>

        <BaseButton
          v-if="order.status.toUpperCase() === 'IN_PROGRESS'"
          variant="primary"
          class="bg-green-600 hover:bg-green-700 border-green-600 px-6 py-2 transition-colors text-xs font-bold"
          @click="showConfirmModal = true"
          :disabled="isConfirming"
        >
          {{ isConfirming ? 'Confirming...' : 'Confirm Receipt' }}
        </BaseButton>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 space-y-8">
        <ShipmentPackageDetails
          :order="order"
          :route="route"
          :assigned-driver="assignedDriver"
          read-only
        />
      </div>
      <div class="space-y-8">
        <ShipmentETACard v-if="isInTransit && route" :route="route" />
        <ShipmentStatusTimeline v-if="route" :route="route" />
        <div
          v-else
          class="bg-bg-canvas border border-border-default rounded-lg p-10 text-center text-text-placeholder text-sm flex flex-col items-center gap-3"
        >
          <div class="w-12 h-12 rounded-full bg-bg-surface flex items-center justify-center">
            <Navigation class="w-6 h-6 text-text-placeholder opacity-30" />
          </div>
          <p class="font-medium">No route information available yet.</p>
        </div>
      </div>
    </div>

    <BaseModal
      :show="showCancelModal"
      title="Cancel Order"
      message="Are you sure you want to cancel this delivery request? This action cannot be undone."
      confirm-text="Yes, Cancel Order"
      variant="danger"
      @confirm="handleCancel"
      @cancel="showCancelModal = false"
    />

    <BaseModal
      :show="showConfirmModal"
      title="Confirm Receipt"
      message="Are you sure you have received this order? This will mark the order as completed."
      confirm-text="Yes, I Received It"
      @confirm="handleConfirmReceipt"
      @cancel="showConfirmModal = false"
    />

    <BaseModal
      :show="showRefuseModal"
      title="Refuse Cargo"
      message="Are you sure you want to refuse this cargo? This will mark the delivery as refused/canceled in the system."
      confirm-text="Yes, Refuse Cargo"
      variant="danger"
      @confirm="handleRefuse"
      @cancel="showRefuseModal = false"
    />

    <BaseModal
      :show="showErrorModal"
      title="Operation Failed"
      :message="modalErrorMessage"
      confirm-text="Close"
      @confirm="showErrorModal = false"
      @cancel="showErrorModal = false"
    />
  </div>
</template>
