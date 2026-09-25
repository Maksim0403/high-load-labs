import apiClient from './axios'
import type { Invoice } from '@/types'

export const invoicesApi = {
  async getInvoices(): Promise<Invoice[]> {
    const response = await apiClient.get<Invoice[]>('/dashboard/invoices')
    return response.data
  },

  async getInvoice(id: number): Promise<Invoice> {
    const response = await apiClient.get<Invoice>(`/dashboard/invoices/${id}`)
    return response.data
  },
}
