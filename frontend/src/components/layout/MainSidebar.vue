<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from 'vue-router'
import IconLogo from '@/components/icons/IconLogo.vue'
import apiClient from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import {
  Settings,
  User,
  LogOut,
  LayoutDashboard,
  Package,
  Users,
  Plus,
  Route,
  Truck,
  FileText,
  PackageCheck,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-vue-next'
import { onMounted, computed } from 'vue'

export interface SidebarLink {
  name: string
  path: string
  icon: string
}

const iconMap: Record<string, unknown> = {
  LayoutDashboard,
  Package,
  Users,
  Plus,
  Route,
  Truck,
  FileText,
  PackageCheck,
  Settings,
}

defineProps<{
  links: SidebarLink[]
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const settingsPath = computed(() => {
  if (authStore.isDriver) return '/driver/settings'
  if (authStore.isClient) return '/recipient/settings'
  return '/settings'
})

const handleNavClick = () => {
  // Закриваємо сайдбар при кліку на мобільних пристроях (якщо він відкритий)
  if (window.innerWidth < 1024) {
    emit('close')
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    notificationStore.fetchNotifications()
  }
})

const handleLogout = async () => {
  try {
    await apiClient.post('/auth/logout')
  } catch (error) {
    console.error('Помилка при виході:', error)
  } finally {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<template>
  <aside
    class="fixed lg:sticky top-0 h-screen flex-shrink-0 flex flex-col py-6 bg-bg-sidebar text-text-on-dark transition-all duration-300 z-50 shadow-none"
    :class="[
      isOpen
        ? 'w-[230px] px-5 opacity-100'
        : 'w-0 lg:w-20 px-0 lg:px-4 opacity-0 lg:opacity-100 overflow-hidden',
    ]"
  >
    <div class="flex items-center justify-between mb-8 min-h-[32px]">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <IconLogo v-if="isOpen" class="w-28 h-auto flex-shrink-0" />
      </Transition>

      <button
        class="flex items-center justify-center w-8 h-8 rounded text-text-sidebar-muted hover:text-white hover:bg-[#083672] transition-colors flex-shrink-0 ml-auto"
        @click="$emit('toggle')"
      >
        <PanelLeftClose v-if="isOpen" class="w-4 h-4" />
        <PanelLeftOpen v-else class="w-4 h-4" />
      </button>
    </div>

    <div class="flex mb-8 overflow-hidden justify-center items-center">
      <router-link
        :to="settingsPath"
        @click.stop="handleNavClick"
        class="w-10 h-10 rounded-full bg-brand-light flex items-center justify-center flex-shrink-0 hover:bg-brand-primary transition-all border-2 border-transparent hover:border-white/20 shadow-sm"
        title="My Profile"
      >
        <User class="w-5 h-5 text-white" />
      </router-link>
    </div>

    <nav class="flex flex-col gap-0.5 flex-1">
      <RouterLink
        v-for="link in links"
        :key="link.path"
        :to="link.path"
        @click="handleNavClick"
        class="flex items-center gap-3 py-2 rounded text-sm text-text-sidebar-muted hover:text-white transition-colors"
        :class="[
          route.path === link.path ? 'bg-[#083672] text-white' : 'hover:bg-[#083672]',
          isOpen ? 'px-3' : 'lg:justify-center lg:px-2',
        ]"
        :title="!isOpen ? link.name : undefined"
      >
        <div class="relative flex items-center justify-center">
          <component :is="iconMap[link.icon]" class="w-4 h-4 flex-shrink-0" />
          <div
            v-if="link.path === '/driver/vehicle' && notificationStore.hasUnreadMaintenance"
            class="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full border border-bg-sidebar"
          ></div>
        </div>
        <span v-if="isOpen" class="whitespace-nowrap overflow-hidden">{{ link.name }}</span>
      </RouterLink>
    </nav>

    <button
      @click="handleLogout"
      class="flex items-center gap-3 px-3 py-2 rounded text-sm text-text-sidebar-muted hover:text-red-400 hover:bg-[#083672] transition-colors mt-auto"
      :class="!isOpen && 'lg:justify-center lg:px-2'"
      :title="!isOpen ? 'Log Out' : undefined"
    >
      <LogOut class="w-4 h-4 flex-shrink-0" />
      <span v-if="isOpen">Log Out</span>
    </button>
  </aside>
</template>
