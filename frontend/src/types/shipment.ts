export interface Shipment {
  id: number
  order_id: number
  weight: number
  volume: number
  quantity: number
  description: string | null
}
