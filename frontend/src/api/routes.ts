import apiClient from './axios'
import type { Route, RouteStatus, DeliveryPhoto, User } from '@/types'

export interface RouteStatusCreate {
  status: string
  location?: string
  description?: string
}

export const routesApi = {
  async getTodayRoutes(): Promise<Route[]> {
    const response = await apiClient.get<Route[]>('/dashboard/routes/today')
    return response.data
  },

  async addRouteStatus(routeId: number, statusIn: RouteStatusCreate): Promise<unknown> {
    const response = await apiClient.post(`/dashboard/routes/${routeId}/statuses`, statusIn)
    return response.data
  },

  async getRouteStatuses(routeId: number): Promise<RouteStatus[]> {
    const response = await apiClient.get<RouteStatus[]>(`/dashboard/routes/${routeId}/statuses`)
    return response.data
  },

  async getDrivers(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/dashboard/drivers')
    return response.data
  },

  async getDriverRoutes(status?: string): Promise<Route[]> {
    const params = status ? { status } : {}
    const response = await apiClient.get<Route[]>('/dashboard/routes', { params })
    return response.data
  },

  async assignRoute(
    orderId: number,
    driver_id: number,
    vehicle_id: number,
    eta: string,
  ): Promise<Route> {
    const response = await apiClient.post<Route>(`/dashboard/orders/${orderId}/assign`, {
      driver_id,
      vehicle_id,
      eta,
    })
    return response.data
  },

  async getRoutePhotos(routeId: number): Promise<DeliveryPhoto[]> {
    const response = await apiClient.get<DeliveryPhoto[]>(`/dashboard/routes/${routeId}/photos`)
    return (response.data || []).map((photo) => {
      // Since backend schema might not include URL, we build it here.
      // The bucket is public, so we can use the direct link.
      const baseUrl = 'http://localhost:8333/public-images'
      const url = photo.url || (photo.key ? `${baseUrl}/${photo.key}` : '')

      return {
        ...photo,
        url: (url || '')
          .replace('http://seaweedfs:8333', 'http://localhost:8333')
          .replace('http://s3:9000', 'http://localhost:9000'),
      }
    })
  },

  async uploadRoutePhoto(routeId: number, file: File, description?: string): Promise<void> {
    const formData = new FormData()
    formData.append('file', file)
    if (description) {
      formData.append('description', description)
    }
    await apiClient.post(`/dashboard/routes/${routeId}/photos`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  async deleteRoutePhoto(photoId: number): Promise<void> {
    await apiClient.delete(`/dashboard/routes/photos/${photoId}`)
  },
}
