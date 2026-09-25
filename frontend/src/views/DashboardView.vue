<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import { ordersApi } from '@/api/orders'
import { routesApi } from '@/api/routes'
import type { Order, Route } from '@/types'
import StatCard from '@/components/dashboard/StatCard.vue'
import LatestUpdates from '@/components/dashboard/LatestUpdates.vue'
import ActiveDeliveries, { type Delivery } from '@/components/dashboard/ActiveDeliveries.vue'
import MonthlyExpensesChart from '@/components/dashboard/MonthlyExpensesChart.vue'
import { Loader2, Truck, AlertCircle } from 'lucide-vue-next'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const isLoading = ref(true)
const orders = ref<Order[]>([])
const allRoutes = ref<Route[]>([])
const fetchData = async () => {
  isLoading.value = true
  try {
    const [ordersRes, routesRes] = await Promise.all([
      ordersApi.getOrders(),
      authStore.isManager ? routesApi.getDriverRoutes() : Promise.resolve([]),
      notificationStore.fetchNotifications(),
    ])

    orders.value = ordersRes
    allRoutes.value = routesRes
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)

const recentRoutesForManager = computed(() => {
  if (!allRoutes.value || allRoutes.value.length === 0) return []

  return allRoutes.value
    .slice()
    .sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0))
    .slice(0, 3)
    .map((r) => ({
      id: r.id.toString(),
      orderId: r.order_id.toString(),
      title: r.order?.title || `Route #${r.id}`,
      status: r.completed_at ? 'delivered' : r.started_at ? 'in_transit' : 'assigned',
      estimatedArrival: r.eta
        ? new Date(r.eta).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : 'N/A',
    }))
})

const managerStats = computed(() => {
  const total = orders.value.length
  const inTransit = orders.value.filter((o) => o.status === 'in_progress').length
  const delivered = orders.value.filter((o) => o.status === 'completed').length
  const pending = orders.value.filter((o) => o.status === 'pending').length

  return [
    { title: 'Total Shipments', value: total.toString() },
    { title: 'In Transit', value: inTransit.toString() },
    { title: 'Delivered', value: delivered.toString() },
    { title: 'Pending', value: pending.toString() },
  ]
})

const driverStats = computed(() => {
  const currentRoute = orders.value.filter((o) => o.status === 'in_progress').length
  return [
    {
      title: 'Current Shipments',
      value: currentRoute.toString(),
    },
    {
      title: 'Maintenance Alerts',
      value: notificationStore.maintenanceAlerts.length.toString(),
      color: notificationStore.hasUnreadMaintenance ? 'text-red-500 font-bold' : '',
    },
    {
      title: 'New Notifications',
      value: notificationStore.unreadNotifications.length.toString(),
    },
  ]
})

const clientStats = computed(() => {
  const active = orders.value.filter(
    (o) => o.status === 'in_progress' || o.status === 'pending',
  ).length
  const received = orders.value.filter((o) => o.status === 'completed').length

  return [
    { title: 'Active Shipments', value: active.toString() },
    { title: 'Total Received', value: received.toString() },
    {
      title: 'Notifications',
      value: notificationStore.unreadNotifications.length.toString(),
    },
    {
      title: 'Total Weight',
      value: orders.value.reduce((acc, o) => acc + o.weight, 0).toFixed(1) + 'kg',
    },
  ]
})

const currentMonth = new Date().toISOString().slice(0, 7)

const activeDeliveries = computed(() =>
  orders.value
    .filter((o) => o.status === 'in_progress' || o.status === 'pending')
    .map((o) => {
      const route = allRoutes.value.find((r) => r.order_id === o.id)
      return {
        id: o.id.toString(),
        orderId: o.id.toString(),
        title: o.title,
        status: o.status,
        estimatedArrival: route?.eta
          ? new Date(route.eta).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          : 'TBD',
      }
    }),
)

const handleDeliveryClick = (delivery: Delivery) => {
  const orderId = delivery.orderId || delivery.id
  if (authStore.isManager) {
    router.push(`/shipments/${orderId}`)
  } else if (authStore.isClient) {
    router.push(`/recipient/orders/${orderId}`)
  } else if (authStore.isDriver) {
    router.push('/driver/route')
  }
}

const handleViewAll = () => {
  if (authStore.isManager) {
    router.push('/shipments')
  } else if (authStore.isClient) {
    router.push('/recipient/orders')
  } else if (authStore.isDriver) {
    router.push('/driver/route')
  }
}

const latestUpdates = computed(() =>
  notificationStore.notifications.slice(0, 5).map((n) => ({
    time: new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    text: n.message,
  })),
)
</script>

<template>
  <div class="p-8 bg-bg-surface min-h-screen">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-text-primary">Dashboard</h1>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <Loader2 class="w-10 h-10 text-primary animate-spin mb-4" />
      <p class="text-text-secondary">Loading your dashboard...</p>
    </div>

    <template v-else>
      <template v-if="authStore.isManager">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard v-for="stat in managerStats" :key="stat.title" v-bind="stat" />
        </div>

        <div class="space-y-6 mb-8">
          <LatestUpdates :updates="latestUpdates" title="System Activity" />

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ActiveDeliveries
              :deliveries="recentRoutesForManager"
              title="Recent Routes"
              @select="handleDeliveryClick"
              @view-all="handleViewAll"
            />

            <div class="bg-bg-canvas border border-border-default rounded-lg p-6 flex flex-col">
              <h2 class="text-xl font-bold text-text-primary mb-6">Quick Actions</h2>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
                <router-link
                  to="/route-assignment"
                  class="flex flex-col items-center justify-center p-6 border border-border-default rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-center group"
                >
                  <span
                    class="text-lg font-bold text-text-primary mb-2 group-hover:text-primary transition-colors"
                    >Assign Routes</span
                  >
                  <span class="text-sm text-text-secondary">Assign drivers to pending orders</span>
                </router-link>
                <router-link
                  to="/shipments"
                  class="flex flex-col items-center justify-center p-6 border border-border-default rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-center group"
                >
                  <span
                    class="text-lg font-bold text-text-primary mb-2 group-hover:text-primary transition-colors"
                    >Monitor Shipments</span
                  >
                  <span class="text-sm text-text-secondary">Check current delivery statuses</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="authStore.isClient">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard v-for="stat in clientStats" :key="stat.title" v-bind="stat" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div class="lg:col-span-2 space-y-6">
            <MonthlyExpensesChart :month="currentMonth" />
            <ActiveDeliveries
              v-if="activeDeliveries.length > 0"
              :deliveries="activeDeliveries"
              @select="handleDeliveryClick"
              @view-all="handleViewAll"
            />
            <div
              v-else
              class="bg-bg-canvas border border-border-default rounded-lg p-10 text-center"
            >
              <h3 class="text-lg font-bold text-text-primary mb-2">No active shipments</h3>
              <p class="text-text-secondary mb-6">
                Create a new delivery request to start tracking.
              </p>
              <router-link
                to="/recipient/delivery/new"
                class="px-6 py-2 bg-primary text-white rounded font-bold"
              >
                New Delivery
              </router-link>
            </div>
            <LatestUpdates :updates="latestUpdates" title="My Notifications" />
          </div>
          <div class="space-y-6">
            <div class="bg-bg-canvas border border-border-default rounded-lg p-6">
              <h3 class="text-lg font-bold mb-4">Billing Snapshot</h3>
              <p class="text-sm text-text-secondary mb-4">
                View your full expenses and reports in the billing section.
              </p>
              <router-link
                to="/recipient/billing"
                class="block w-full py-2 bg-bg-surface border border-border-default rounded text-center text-sm font-medium hover:border-primary transition-all"
              >
                Go to Billing
              </router-link>
            </div>
            <div class="bg-primary/5 border border-primary/20 rounded-lg p-6 text-center">
              <h3 class="text-lg font-bold text-primary mb-2">Recipient Support</h3>
              <p class="text-sm text-text-secondary mb-4">Need help with an order?</p>
              <button
                class="w-full py-2 bg-primary text-white rounded-md font-medium hover:bg-primary/90 transition-colors"
              >
                Contact Manager
              </button>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="authStore.isDriver">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          <StatCard v-for="stat in driverStats" :key="stat.title" v-bind="stat" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div class="lg:col-span-2 space-y-6">
            <div
              v-if="notificationStore.hasUnreadMaintenance"
              class="bg-red-50 border border-red-200 rounded-lg p-6"
            >
              <div class="flex items-start gap-4">
                <div class="p-3 bg-red-100 rounded-full text-red-600">
                  <AlertCircle class="w-6 h-6" />
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold text-red-900 mb-1">Maintenance Required</h3>
                  <p class="text-red-700 text-sm mb-4">
                    Your vehicle has reached its mileage limit for maintenance. Please check the
                    maintenance section for details.
                  </p>
                  <router-link
                    to="/driver/vehicle"
                    class="inline-flex items-center text-sm font-bold text-red-600 hover:text-red-800 transition-colors uppercase tracking-wider"
                  >
                    Manage Vehicle →
                  </router-link>
                </div>
              </div>
            </div>

            <ActiveDeliveries
              v-if="activeDeliveries.length > 0"
              :deliveries="activeDeliveries"
              @select="handleDeliveryClick"
              @view-all="handleViewAll"
            />
            <div
              v-else
              class="bg-bg-canvas border border-border-default rounded-lg p-10 text-center"
            >
              <Truck class="w-12 h-12 text-text-placeholder mx-auto mb-4" />
              <h3 class="text-lg font-bold text-text-primary mb-2">No active route</h3>
              <p class="text-text-secondary mb-6">
                You don't have any assigned orders at the moment.
              </p>
              <router-link
                to="/driver/route"
                class="px-8 py-3 bg-primary text-white rounded-md font-bold hover:bg-primary/90 transition-colors"
              >
                Go to My Route
              </router-link>
            </div>
          </div>
          <div class="space-y-6">
            <LatestUpdates :updates="latestUpdates" title="Recent Notifications" />
          </div>
        </div>
      </template>

      <template v-else>
        <div
          class="flex flex-col items-center justify-center py-20 bg-bg-canvas border border-border-default rounded-lg text-center"
        >
          <h2 class="text-xl font-bold text-text-primary mb-2">Welcome to LogiFlow</h2>
          <p class="text-text-placeholder mb-6 max-w-md mx-auto">
            Please contact your administrator to assign a role and access the platform features.
          </p>
        </div>
      </template>
    </template>
  </div>
</template>
