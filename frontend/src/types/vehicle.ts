export interface Vehicle {
  id: number
  driver_id: number | null
  brand: string
  model: string
  license_plate: string
  max_weight: number
  max_volume: number
  fuel_consumption: number
  fuel_price: number
  current_mileage: number
  maintenance_interval: number
}

export interface VehicleCreate {
  brand: string
  model: string
  license_plate: string
  max_weight: number
  max_volume: number
  fuel_consumption: number
  fuel_price: number
  current_mileage: number
  maintenance_interval: number
}

export interface VehicleUpdate {
  current_mileage?: number
  fuel_consumption?: number
  fuel_price?: number
  maintenance_interval?: number
}

export interface TripRecord {
  date: string
  routeId: number
  distance: number
  fuel: number
  cost: number
}
