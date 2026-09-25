<script setup lang="ts">
import type { Order, Route, User } from '@/types'
import ShipmentPackageDetails from '@/components/shipment-details/ShipmentPackageDetails.vue'
import ShipmentStatusTimeline from '@/components/shipment-details/ShipmentStatusTimeline.vue'
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import apiClient from '@/api/axios'
import { ordersApi } from '@/api/orders'
import { useAuthStore } from '@/stores/auth'
import { Trash2, ArrowLeft, Navigation } from 'lucide-vue-next'
import { getErrorMessage } from '@/utils/errorHandler'

const authStore = useAuthStore()
const router = useRouter()
const routePath = useRoute()
const orderId = routePath.params.id

const order = ref<Order | null>(null)
const route = ref<Route | null>(null)
const assignedDriver = ref<User | null>(null)
const isLoading = ref(true)
const isCancelling = ref(false)
const isConfirming = ref(false)
const showCancelModal = ref(false)
const showConfirmModal = ref(false)
const showErrorModal = ref(false)
const modalErrorMessage = ref('')
const error = ref('')

const handleCancel = async () => {
  if (!order.value) return
  showCancelModal.value = false
  isCancelling.value = true
  try {
    await ordersApi.cancelOrder(order.value.id)
    await fetchData()
  } catch (err) {
    console.error('Failed to cancel order:', err)
    modalErrorMessage.value = getErrorMessage(err)
    showErrorModal.value = true
  } finally {
    isCancelling.value = false
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
    modalErrorMessage.value = getErrorMessage(err)
    showErrorModal.value = true
  } finally {
    isConfirming.value = false
  }
}

const fetchData = async () => {
  isLoading.value = true
  error.value = ''
  try {
    let orderData: Order | null = null

    if (authStore.isManager) {
      const allOrdersRes = await apiClient.get('/dashboard/orders')
      orderData = allOrdersRes.data.find((o: Order) => o.id === Number(orderId)) || null
    } else {
      try {
        const orderRes = await apiClient.get(`/dashboard/orders/${orderId}`)
        orderData = orderRes.data
      } catch (err) {
        console.warn('Could not fetch order directly, likely access denied.', err)
      }
    }

    if (!orderData) {
      throw new Error('Order not found')
    }
    order.value = orderData

    const routeRes = await apiClient.get(`/dashboard/routes`, {
      params: { order_id: orderId },
    })

    if (routeRes.data && routeRes.data.length > 0) {
      const routeData = routeRes.data[0]
      try {
        const statusesRes = await apiClient.get(`/dashboard/routes/${routeData.id}/statuses`)
        routeData.statuses = statusesRes.data
      } catch (err) {
        console.error('Failed to fetch route statuses:', err)
      }
      route.value = routeData

      if (routeData.driver_id) {
        try {
          const driversRes = await apiClient.get('/dashboard/drivers')
          const driver = driversRes.data.find((d: User) => d.id === routeData.driver_id)
          if (driver) {
            assignedDriver.value = driver
          }
        } catch (err) {
          console.error('Failed to fetch driver info:', err)
        }
      }
    }
  } catch (err: unknown) {
    console.error('Failed to fetch shipment details:', err)
    error.value = getErrorMessage(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div v-if="isLoading" class="flex justify-center items-center min-h-screen">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
  </div>

  <div v-else-if="error || !order" class="p-8 text-center">
    <div class="bg-red-50 border border-red-200 text-red-600 p-4 rounded mb-4">
      {{ error || 'Order not found' }}
    </div>
    <BaseButton @click="router.back()">Go Back</BaseButton>
  </div>

  <div v-else class="p-4 md:p-8 font-roboto max-w-7xl mx-auto">
    <button
      class="flex items-center gap-1 text-text-secondary text-[10px] md:text-xs mb-4 hover:text-text-primary transition-colors uppercase font-black tracking-widest"
      @click="router.back()"
    >
      <ArrowLeft class="w-3 h-3" /> BACK TO SHIPMENTS
    </button>

    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-[32px] font-bold text-text-primary leading-tight">
          Tracking: {{ order.title }}
        </h1>
        <div class="flex items-center gap-2 mt-2">
          <span
            class="text-[10px] bg-brand-primary/10 text-brand-primary px-2 py-0.5 rounded font-black uppercase tracking-widest"
          >
            {{ order.status }}
          </span>
          <span class="text-[10px] text-text-placeholder font-medium uppercase tracking-tighter">
            Created: {{ new Date(order.created_at).toLocaleDateString() }}
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
          @refresh="fetchData"
        />
      </div>
      <div class="space-y-8">
        <ShipmentStatusTimeline v-if="route" :route="route" @refresh="fetchData" />
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
      title="Cancel Shipment"
      message="Are you sure you want to cancel this shipment? This will stop the delivery process immediately."
      confirm-text="Yes, Cancel Shipment"
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
      :show="showErrorModal"
      title="Operation Failed"
      :message="modalErrorMessage"
      confirm-text="Close"
      @confirm="showErrorModal = false"
      @cancel="showErrorModal = false"
    />
  </div>
</template>
