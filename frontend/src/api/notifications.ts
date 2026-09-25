import apiClient from './axios'
import type { Notification } from '@/types'

export const notificationsApi = {
  getNotifications: async (): Promise<Notification[]> => {
    const response = await apiClient.get<Notification[]>('/dashboard/notifications')
    return response.data
  },

  markAsRead: async (id: number): Promise<Notification> => {
    const response = await apiClient.patch<Notification>(`/dashboard/notifications/${id}`)
    return response.data
  },

  markAllAsRead: async (): Promise<void> => {
    await apiClient.patch('/dashboard/notifications/read-all')
  },
}
