export interface MonthlyExpensePoint {
  month: string
  total_shipments: number
  total_weight: number
  total_volume: number
  total_distance: number
  invoice_count: number
  total_amount: number
  date?: string
  amount?: number
}

export interface MonthlyExpensesResponse {
  total_amount: number
  data: MonthlyExpensePoint[]
  period: string
}
