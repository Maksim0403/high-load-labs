export type OrderStatus = 'pending' | 'in_progress' | 'completed' | 'canceled'

export interface Order {
  id: number
  title: string
  description: string | null
  weight: number
  total_amount: number
  status: OrderStatus
  owner_id: number
  origin_address: string
  destination_address: string
  distance: number
  is_template: boolean
  created_at: string
  received_at?: string | null
}

export interface OrderCreate {
  title: string
  description: string | null
  weight: number
  total_amount: number
  origin_address: string
  destination_address: string
  distance: number
  is_template: boolean
}
