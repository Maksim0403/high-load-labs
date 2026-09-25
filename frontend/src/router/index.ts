import { createRouter, createWebHistory } from 'vue-router'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { useAuthStore } from '../stores/auth'
import RecipientLayout from '@/layouts/RecipientLayout.vue'
import DriverLayout from '@/layouts/DriverLayout.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import RecipientView from '@/views/RecipientView.vue'
import TodaysRouteView from '@/views/TodaysRouteView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/',
      component: DashboardLayout,
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView,
        },
        {
          path: 'shipments',
          name: 'shipments',
          component: () => import('@/views/ShipmentsListView.vue'),
        },
        {
          path: 'shipments/:id',
          name: 'shipment-details',
          component: () => import('@/views/ShipmentDetailsView.vue'),
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/UsersView.vue'),
        },
        {
          path: 'route-assignment',
          name: 'route-assignment',
          component: () => import('@/views/RouteAssignmentView.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
    {
      path: '/recipient',
      component: RecipientLayout,
      children: [
        {
          path: 'orders',
          name: 'recipient-orders',
          component: () => import('@/views/RecipientOrdersView.vue'),
        },
        {
          path: 'orders/:id',
          name: 'recipient-order-details',
          component: () => import('@/views/RecipientOrderDetailsView.vue'),
        },
        {
          path: 'active',
          name: 'recipient-active',
          component: () => import('@/views/RecipientActiveView.vue'),
        },
        {
          path: 'billing',
          name: 'recipient-billing',
          component: RecipientView,
        },
        {
          path: 'delivery/new',
          name: 'create-delivery',
          component: () => import('@/views/CreateDelivery.vue'),
        },
        {
          path: 'settings',
          name: 'recipient-settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
    {
      path: '/driver',
      component: DriverLayout,
      children: [
        {
          path: 'route',
          name: 'driver-route',
          component: TodaysRouteView,
        },
        {
          path: 'vehicle',
          name: 'driver-vehicle',
          component: () => import('@/views/MyVehicleView.vue'),
        },
        {
          path: 'settings',
          name: 'driver-settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  if (to.name !== 'login' && to.name !== 'register' && !isAuthenticated) {
    return { name: 'login' }
  }

  if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
    if (authStore.isManager) return { name: 'dashboard' }
    if (authStore.isDriver) return { name: 'driver-route' }
    if (authStore.isClient) return { name: 'recipient-billing' }
    return { name: 'dashboard' }
  }

  if (isAuthenticated) {
    const path = to.path

    let defaultRoute = { name: 'dashboard' }
    if (authStore.isDriver) defaultRoute = { name: 'driver-route' }
    if (authStore.isClient) defaultRoute = { name: 'recipient-billing' }

    if (path.startsWith('/recipient') && !authStore.isClient) {
      console.warn('Access denied: Client only area')
      return defaultRoute
    }

    if (path.startsWith('/driver') && !authStore.isDriver) {
      console.warn('Access denied: Driver only area')
      return defaultRoute
    }

    const managerOnlyPaths = ['/dashboard', '/shipments', '/users', '/route-assignment']
    if (managerOnlyPaths.some((p) => path.startsWith(p)) && !authStore.isManager) {
      console.warn('Access denied: Manager only area')
      return defaultRoute
    }
  }

  return true
})

export default router
