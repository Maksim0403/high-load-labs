<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import apiClient from '@/api/axios'
import type { Order } from '@/types'
import { Package, Clock, ChevronRight, Loader2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

interface Route {
  id: number
  order_id: number
  driver_id: number
  eta: string
}

const router = useRouter()
const orders = ref<Order[]>([])
const routes = ref<Route[]>([])
const isLoading = ref(true)

const fetchActiveOrders = async () => {
  isLoading.value = true
  try {
    const [allOrders, allRoutes] = await Promise.all([
      ordersApi.getOrders(),
      apiClient.get<Route[]>('/dashboard/routes'),
    ])

    orders.value = allOrders.filter((o) => o.status === 'pending' || o.status === 'in_progress')
    routes.value = allRoutes.data
  } catch (error) {
    console.error('Failed to fetch active orders or routes:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchActiveOrders)

const getOrderEta = (orderId: number) => {
  const route = routes.value.find((r) => r.order_id === orderId)
  if (!route) return 'TBD'
  return new Date(route.eta).toLocaleString('uk-UA', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'text-orange-500 bg-orange-50 border-orange-100'
    case 'in_progress':
      return 'text-blue-500 bg-blue-50 border-blue-100'
    default:
      return 'text-gray-500 bg-gray-50 border-gray-100'
  }
}
</script>

<template>
  <div class="p-4 md:p-8 max-w-7xl mx-auto font-roboto">
    <div class="mb-8">
      <h1 class="text-2xl md:text-[32px] font-bold text-text-primary">Active Deliveries</h1>
      <p class="text-text-secondary">Track your packages in real-time</p>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <Loader2 class="w-10 h-10 text-primary animate-spin mb-4" />
      <p class="text-text-secondary">Updating tracking data...</p>
    </div>

    <div
      v-else-if="orders.length === 0"
      class="bg-bg-canvas border border-border-default rounded-xl p-12 text-center"
    >
      <div
        class="w-20 h-20 bg-bg-surface rounded-full flex items-center justify-center mx-auto mb-6"
      >
        <Package class="w-10 h-10 text-text-placeholder" />
      </div>
      <h2 class="text-xl font-bold text-text-primary mb-2">No active deliveries</h2>
      <p class="text-text-secondary mb-8 max-w-md mx-auto">
        You don't have any shipments in transit or pending at the moment. Create a new delivery to
        get started.
      </p>
      <button
        @click="router.push('/recipient/delivery/new')"
        class="bg-primary text-white px-8 py-3 rounded-md font-bold hover:bg-primary/90 transition-colors"
      >
        Create New Delivery
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="order in orders"
        :key="order.id"
        class="bg-bg-canvas border border-border-default rounded-xl p-6 hover:border-primary transition-all cursor-pointer group"
        @click="router.push(`/recipient/orders/${order.id}`)"
      >
        <div class="flex justify-between items-start mb-6">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <Package class="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 class="font-bold text-text-primary group-hover:text-primary transition-colors">
                {{ order.title }}
              </h3>
              <p class="text-xs text-text-placeholder">
                Order #{{ String(order.id).padStart(5, '0') }}
              </p>
            </div>
          </div>
          <span
            class="px-3 py-1 rounded-full text-[10px] font-black uppercase border"
            :class="getStatusColor(order.status)"
          >
            {{ order.status }}
          </span>
        </div>

        <div class="space-y-4 mb-6">
          <div class="flex items-start gap-3">
            <div class="mt-1">
              <div class="w-2 h-2 rounded-full bg-orange-400"></div>
              <div class="w-0.5 h-6 bg-border-default mx-auto my-1"></div>
              <div class="w-2 h-2 rounded-full bg-green-500"></div>
            </div>
            <div class="flex-1 text-xs space-y-4">
              <div>
                <p class="text-text-placeholder uppercase font-bold text-[9px]">From</p>
                <p class="text-text-primary font-medium truncate">{{ order.origin_address }}</p>
              </div>
              <div>
                <p class="text-text-placeholder uppercase font-bold text-[9px]">To</p>
                <p class="text-text-primary font-medium truncate">
                  {{ order.destination_address }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-4 border-t border-border-default text-xs">
          <div class="flex items-center gap-2 text-text-secondary">
            <Clock class="w-4 h-4" />
            <span
              >Expected:
              <span class="text-text-primary font-medium">{{ getOrderEta(order.id) }}</span></span
            >
          </div>
          <div
            class="flex items-center gap-1 text-primary font-bold group-hover:gap-2 transition-all"
          >
            View details
            <ChevronRight class="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
