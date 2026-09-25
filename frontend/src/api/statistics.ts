import apiClient from './axios'
import type { MonthlyExpensesResponse, MonthlyExpensePoint } from '@/types'

export const getMonthlyExpenses = async (month?: string): Promise<MonthlyExpensesResponse> => {
  const response = await apiClient.get<MonthlyExpensePoint[]>('/dashboard/statistics/monthly', {
    params: { month },
  })
  const rawData = response.data

  const sortedData = [...rawData].sort(
    (a, b) => new Date(a.month).getTime() - new Date(b.month).getTime(),
  )

  const data = sortedData.map((item) => ({
    ...item,
    date: item.month,
    amount: item.total_amount,
  }))

  const total_amount = data.reduce((acc, item) => acc + (item.total_amount || 0), 0)

  let period = month
    ? new Date(month).toLocaleDateString('uk-UA', { month: 'long', year: 'numeric' })
    : 'Last 12 Months'

  if (!month && data.length > 0) {
    const firstItem = data[0]
    const lastItem = data[data.length - 1]

    if (firstItem && lastItem) {
      const firstMonth = new Date(firstItem.month).toLocaleDateString('en-US', {
        month: 'short',
        year: 'numeric',
      })
      const lastMonth = new Date(lastItem.month).toLocaleDateString('en-US', {
        month: 'short',
        year: 'numeric',
      })
      period = `${firstMonth} - ${lastMonth}`
    }
  }

  return {
    total_amount,
    period,
    data,
  }
}
