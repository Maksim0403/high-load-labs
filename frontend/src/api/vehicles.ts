import apiClient from './axios'
import type { Vehicle, VehicleCreate, VehicleUpdate } from '@/types'

export const vehiclesApi = {
  async getMyVehicles(): Promise<Vehicle[]> {
    const response = await apiClient.get<Vehicle[]>('/dashboard/vehicles')
    return response.data
  },

  async createVehicle(vehicle: VehicleCreate): Promise<Vehicle> {
    const response = await apiClient.post<Vehicle>('/dashboard/vehicles', vehicle)
    return response.data
  },

  async updateVehicle(id: number, vehicle: VehicleUpdate): Promise<Vehicle> {
    const response = await apiClient.patch<Vehicle>(`/dashboard/vehicles/${id}`, vehicle)
    return response.data
  },

  async deleteVehicle(id: number): Promise<void> {
    await apiClient.delete(`/dashboard/vehicles/${id}`)
  },
}
