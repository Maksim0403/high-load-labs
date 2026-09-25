export interface Invoice {
  id: number
  owner_id: number
  billing_month: string
  total_shipment: number
  total_weight: number
  total_volume: number
  total_distance: number
  total_amount: number
  generated_at: string
}
