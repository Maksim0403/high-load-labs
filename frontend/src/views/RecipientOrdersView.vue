<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ordersApi } from '@/api/orders'
import { routesApi } from '@/api/routes'
import type { Order, Route } from '@/types'
import { Package, Search, Plus, ChevronRight, Loader2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseEmptyState from '@/components/ui/BaseEmptyState.vue'
import { getErrorMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { showError } = useToast()
const orders = ref<Order[]>([])
const routes = ref<Route[]>([])
const isLoading = ref(true)
const error = ref('')
const searchQuery = ref('')

const showCancelModal = ref(false)
const showConfirmModal = ref(false)
const showRefuseModal = ref(false)
const orderToCancel = ref<number | null>(null)
const orderToConfirm = ref<number | null>(null)
const orderToRefuse = ref<number | null>(null)

const confirmCancel = (e: Event, orderId: number) => {
  e.stopPropagation()
  orderToCancel.value = orderId
  showCancelModal.value = true
}

const openConfirmModal = (e: Event, orderId: number) => {
  e.stopPropagation()
  orderToConfirm.value = orderId
  showConfirmModal.value = true
}

const openRefuseModal = (e: Event, orderId: number) => {
  e.stopPropagation()
  orderToRefuse.value = orderId
  showRefuseModal.value = true
}

const handleCancel = async () => {
  if (!orderToCancel.value) return

  try {
    await ordersApi.cancelOrder(orderToCancel.value)
    showCancelModal.value = false
    orderToCancel.value = null
    await fetchOrders()
  } catch (err) {
    console.error('Failed to cancel order:', err)
    showError(getErrorMessage(err))
  }
}

const handleRefuse = async () => {
  if (!orderToRefuse.value) return

  try {
    await ordersApi.cancelOrder(orderToRefuse.value)
    showRefuseModal.value = false
    orderToRefuse.value = null
    await fetchOrders()
  } catch (err) {
    console.error('Failed to refuse order:', err)
    showError(getErrorMessage(err))
  }
}

const handleConfirmReceipt = async () => {
  if (!orderToConfirm.value) return

  try {
    await ordersApi.confirmReceipt(orderToConfirm.value)
    showConfirmModal.value = false
    orderToConfirm.value = null
    await fetchOrders()
  } catch (err) {
    console.error('Failed to confirm receipt:', err)
    showConfirmModal.value = false
    orderToConfirm.value = null
    showError(getErrorMessage(err))
  }
}

const fetchOrders = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const [ordersRes, routesRes] = await Promise.all([
      ordersApi.getOrders(),
      routesApi.getDriverRoutes(),
    ])
    orders.value = ordersRes
    routes.value = routesRes
  } catch (err: unknown) {
    console.error('Failed to fetch orders or routes:', err)
    error.value = getErrorMessage(err)
  } finally {
    isLoading.value = false
  }
}

const getOrderEta = (orderId: number) => {
  const route = routes.value.find((r) => r.order_id === orderId)
  if (!route) return null
  return new Date(route.eta).toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusClasses = (status: string) => {
  const s = status.toUpperCase()
  switch (s) {
    case 'PENDING':
      return 'bg-orange-100 text-orange-600'
    case 'IN_PROGRESS':
      return 'bg-blue-100 text-blue-600'
    case 'COMPLETED':
      return 'bg-green-100 text-green-600'
    case 'CANCELED':
      return 'bg-red-100 text-red-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

onMounted(fetchOrders)

const filteredOrders = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return orders.value

  return orders.value.filter(
    (o) =>
      o.title.toLowerCase().includes(query) ||
      o.id.toString().includes(query) ||
      (o.origin_address && o.origin_address.toLowerCase().includes(query)) ||
      (o.destination_address && o.destination_address.toLowerCase().includes(query)),
  )
})
</script>

<template>
  <div class="p-4 md:p-8 font-roboto text-text-primary max-w-7xl mx-auto">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-[32px] font-bold">My Orders</h1>
        <p class="text-text-secondary text-sm md:text-base">
          Manage and track your delivery requests
        </p>
      </div>
      <button
        @click="router.push('/recipient/delivery/new')"
        class="w-full sm:w-auto flex items-center justify-center gap-2 bg-btn-primary-default text-white px-6 py-3 rounded font-bold hover:bg-btn-primary-hover transition-colors"
      >
        <Plus class="w-5 h-5" /> Create New Delivery
      </button>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <Loader2 class="w-12 h-12 text-brand-primary animate-spin mb-4" />
      <p class="text-text-secondary font-bold">LOADING ORDERS...</p>
    </div>

    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 text-red-600 p-4 rounded text-center"
    >
      {{ error }}
      <button @click="fetchOrders" class="ml-4 underline font-bold">Retry</button>
    </div>

    <BaseEmptyState
      v-else-if="orders.length === 0"
      :icon="Package"
      title="No orders found"
      description="You haven't created any delivery requests yet."
    >
      <template #action>
        <button
          @click="router.push('/recipient/delivery/new')"
          class="text-brand-primary font-bold hover:underline"
        >
          Create your first delivery
        </button>
      </template>
    </BaseEmptyState>

    <div v-else class="bg-bg-canvas border border-border-default rounded-lg overflow-hidden">
      <div class="p-4 border-b border-border-default flex flex-col sm:flex-row gap-4">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-placeholder" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by title, address or ID..."
            class="w-full pl-10 pr-4 py-2 bg-bg-surface border border-border-default rounded outline-none focus:border-brand-primary transition-colors text-sm"
          />
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-bg-surface border-b border-border-default">
              <th class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider">
                Order
              </th>
              <th class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider">
                Date
              </th>
              <th class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider">
                ETA
              </th>
              <th class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider">
                Weight
              </th>
              <th class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider">
                Status
              </th>
              <th
                class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider text-right"
              >
                Action
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border-default">
            <tr
              v-for="order in filteredOrders"
              :key="order.id"
              class="hover:bg-bg-surface transition-colors cursor-pointer group"
              @click="router.push(`/recipient/orders/${order.id}`)"
            >
              <td class="py-4 px-6">
                <div
                  class="font-bold text-text-primary group-hover:text-brand-primary transition-colors"
                >
                  {{ order.title }}
                </div>
                <div class="text-[10px] text-text-secondary flex items-center gap-1 mt-1">
                  <span class="font-bold text-orange-400">FROM:</span>
                  <span class="truncate max-w-[80px] sm:max-w-[150px]">{{
                    order.origin_address
                  }}</span>
                  <ChevronRight class="w-2 h-2" />
                  <span class="font-bold text-green-500">TO:</span>
                  <span class="truncate max-w-[80px] sm:max-w-[150px]">{{
                    order.destination_address
                  }}</span>
                </div>
              </td>
              <td class="py-4 px-6 text-sm text-text-secondary">
                {{ new Date(order.created_at).toLocaleDateString() }}
              </td>
              <td class="py-4 px-6">
                <div v-if="getOrderEta(order.id)" class="flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-brand-primary animate-pulse"></span>
                  <span class="text-sm font-bold text-text-primary">{{
                    getOrderEta(order.id)
                  }}</span>
                </div>
                <span v-else class="text-xs text-text-placeholder italic">TBD</span>
              </td>
              <td class="py-4 px-6 text-sm text-text-primary font-medium">{{ order.weight }} kg</td>
              <td class="py-4 px-6">
                <span
                  class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter"
                  :class="getStatusClasses(order.status)"
                >
                  {{ order.status }}
                </span>
                <div v-if="order.received_at" class="text-[8px] text-green-600 mt-1 font-bold">
                  RECEIVED: {{ new Date(order.received_at).toLocaleDateString() }}
                </div>
              </td>
              <td class="py-4 px-6 text-right whitespace-nowrap">
                <button
                  v-if="order.status.toUpperCase() === 'PENDING'"
                  @click="confirmCancel($event, order.id)"
                  class="text-red-500 font-bold text-xs hover:underline mr-4"
                >
                  Cancel
                </button>
                <button
                  v-if="order.status.toUpperCase() === 'IN_PROGRESS'"
                  @click="openRefuseModal($event, order.id)"
                  class="text-orange-500 font-bold text-xs hover:underline mr-4"
                >
                  Refuse
                </button>
                <button
                  v-if="order.status.toUpperCase() === 'IN_PROGRESS'"
                  @click="openConfirmModal($event, order.id)"
                  class="text-green-500 font-bold text-xs hover:underline mr-4"
                >
                  Confirm Receipt
                </button>
                <button class="text-brand-primary font-bold text-xs hover:underline">
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="!isLoading && orders.length > 0 && filteredOrders.length === 0"
        class="p-20 text-center flex flex-col items-center justify-center gap-4"
      >
        <div
          class="w-16 h-16 bg-bg-surface rounded-full flex items-center justify-center border border-border-default"
        >
          <Search class="w-8 h-8 text-text-placeholder" />
        </div>
        <div>
          <p class="text-lg font-bold text-text-primary">No matching orders</p>
          <p class="text-sm text-text-secondary">
            We couldn't find anything matching "{{ searchQuery }}"
          </p>
        </div>
        <button
          @click="searchQuery = ''"
          class="text-sm font-bold text-brand-primary hover:underline"
        >
          Clear search
        </button>
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
    </div>
  </div>
</template>
