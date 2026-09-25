import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Notification } from '@/types'
import { notificationsApi } from '@/api/notifications'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const loading = ref(false)

  const unreadNotifications = computed(() => notifications.value.filter((n) => !n.is_read))

  const maintenanceAlerts = computed(() =>
    unreadNotifications.value.filter((n) => {
      const msg = n.message.toLowerCase()
      return (
        msg.includes('то') ||
        msg.includes('мастил') ||
        msg.includes('maintenance') ||
        msg.includes('service') ||
        msg.includes('requires') ||
        msg.includes('repair')
      )
    }),
  )

  const hasUnreadMaintenance = computed(() => maintenanceAlerts.value.length > 0)

  async function fetchNotifications() {
    loading.value = true
    try {
      notifications.value = await notificationsApi.getNotifications()
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(id: number) {
    try {
      await notificationsApi.markAsRead(id)
      const index = notifications.value.findIndex((n) => n.id === id)
      if (index !== -1) {
        const notification = notifications.value[index]
        if (notification) {
          notification.is_read = true
        }
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  return {
    notifications,
    loading,
    unreadNotifications,
    maintenanceAlerts,
    hasUnreadMaintenance,
    fetchNotifications,
    markAsRead,
  }
})
