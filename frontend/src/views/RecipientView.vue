<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { invoicesApi } from '@/api/invoices'
import { ordersApi } from '@/api/orders'
import type { Invoice, Order } from '@/types'
import { Loader2, AlertCircle, ChevronRight } from 'lucide-vue-next'
import { getErrorMessage } from '@/utils/errorHandler'
import MonthlyExpensesChart from '@/components/dashboard/MonthlyExpensesChart.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const invoices = ref<Invoice[]>([])
const orders = ref<Order[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)
const selectedMonth = ref(new Date().toISOString().slice(0, 7)) // YYYY-MM

const availableMonths = computed(() => {
  const months = new Set<string>()
  const now = new Date()
  months.add(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)

  invoices.value.forEach((inv) => {
    const d = new Date(inv.billing_month)
    months.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`)
  })

  return Array.from(months).sort().reverse()
})

const filteredInvoices = computed(() => {
  return invoices.value.filter((inv) => {
    const d = new Date(inv.billing_month)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    return `${year}-${month}` === selectedMonth.value
  })
})

const totalShipments = computed(() => {
  return filteredInvoices.value.reduce((acc, inv) => acc + (inv.total_shipment || 0), 0)
})

const showDetailsModal = ref(false)
const selectedInvoice = ref<Invoice | null>(null)
const invoiceShipments = ref<Order[]>([])
const isDetailsLoading = ref(false)

const openInvoiceDetails = async (invoice: Invoice) => {
  selectedInvoice.value = invoice
  showDetailsModal.value = true
  isDetailsLoading.value = true
  try {
    // Filter orders for this billing month
    const d = new Date(invoice.billing_month)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const monthStr = `${year}-${month}`

    invoiceShipments.value = orders.value.filter((order) => {
      if (order.status.toUpperCase() !== 'COMPLETED' || !order.received_at) return false
      const rd = new Date(order.received_at)
      const ry = rd.getFullYear()
      const rm = String(rd.getMonth() + 1).padStart(2, '0')
      return `${ry}-${rm}` === monthStr
    })
  } catch (err) {
    console.error('Failed to filter invoice shipments:', err)
  } finally {
    isDetailsLoading.value = false
  }
}

const totalCost = computed(() => {
  return filteredInvoices.value.reduce((acc, inv) => acc + (inv.total_amount || 0), 0)
})

const fetchData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [invoicesRes, ordersRes] = await Promise.all([
      invoicesApi.getInvoices(),
      ordersApi.getOrders(),
    ])
    invoices.value = invoicesRes
    orders.value = ordersRes
  } catch (err) {
    console.error('Failed to fetch data:', err)
    error.value = getErrorMessage(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const formatMonth = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  })
}
</script>

<template>
  <div class="p-4 md:p-8 w-full max-w-7xl mx-auto font-roboto text-text-primary">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-[32px] font-bold">Billings & Reports</h1>
        <p class="text-text-secondary">Control your budget and view logistics reports</p>
      </div>
      <div class="flex items-center gap-3 bg-bg-canvas p-2 rounded-lg border border-border-default">
        <label for="month-filter" class="text-sm font-medium text-text-secondary pl-2"
          >Period:</label
        >
        <select
          id="month-filter"
          v-model="selectedMonth"
          class="bg-transparent border-none text-sm font-bold focus:ring-0 cursor-pointer"
        >
          <option v-for="month in availableMonths" :key="month" :value="month">
            {{ new Date(month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}
          </option>
        </select>
      </div>
    </div>

    <div
      v-if="error"
      class="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg flex items-center gap-2"
    >
      <AlertCircle class="w-5 h-5" />
      {{ error }}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
      <div class="lg:col-span-2">
        <MonthlyExpensesChart :month="selectedMonth" />
      </div>
      <div class="bg-bg-canvas border border-border-default rounded-lg p-6">
        <h3 class="text-lg font-bold mb-4">Financial Summary</h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center pb-4 border-b border-border-default">
            <span class="text-text-secondary">Total Shipments</span>
            <span class="font-bold">{{ totalShipments }}</span>
          </div>
          <div class="flex justify-between items-center pb-4 border-b border-border-default">
            <span class="text-text-secondary">Total Weight</span>
            <span class="font-bold"
              >{{
                filteredInvoices.reduce((acc, inv) => acc + inv.total_weight, 0).toLocaleString()
              }}
              kg</span
            >
          </div>
          <div class="flex justify-between items-center pb-4 border-b border-border-default">
            <span class="text-text-secondary">Total Expenses</span>
            <span class="font-bold text-brand-primary">₴{{ totalCost.toLocaleString() }}</span>
          </div>
          <div
            class="flex justify-between items-center pb-4 border-b border-border-default"
            v-if="filteredInvoices.some((inv) => (inv as any).total_fuel_cost > 0)"
          >
            <span class="text-text-secondary">Est. Logistics Fuel</span>
            <span class="font-bold text-orange-600"
              >₴{{
                filteredInvoices
                  .reduce((acc, inv) => acc + ((inv as any).total_fuel_cost || 0), 0)
                  .toLocaleString()
              }}</span
            >
          </div>
          <div class="pt-2">
            <p
              class="text-[10px] text-text-placeholder mt-3 text-center uppercase tracking-wider font-bold"
            >
              * Billing is calculated based on completed orders for the period
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="w-full">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">Invoice History</h2>
        <button
          @click="fetchData"
          class="text-sm text-brand-primary hover:underline flex items-center gap-1"
          :disabled="isLoading"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          Refresh
        </button>
      </div>

      <div
        v-if="isLoading"
        class="flex flex-col items-center justify-center py-20 bg-bg-canvas rounded-xl border border-border-default"
      >
        <Loader2 class="w-10 h-10 text-brand-primary animate-spin mb-4" />
        <p class="text-text-secondary font-medium">Loading your invoices...</p>
      </div>

      <div
        v-else-if="filteredInvoices.length === 0"
        class="flex flex-col items-center justify-center py-20 bg-bg-canvas rounded-xl border border-border-default text-center"
      >
        <div
          class="w-16 h-16 bg-bg-surface rounded-full flex items-center justify-center mb-4 mx-auto"
        >
          <AlertCircle class="w-8 h-8 text-text-placeholder" />
        </div>
        <p class="text-text-primary font-bold mb-1">No invoices found for this period</p>
        <p class="text-text-secondary text-sm">
          Try selecting a different month or generate a new report.
        </p>
      </div>

      <div v-else class="bg-bg-canvas border border-border-default rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-bg-surface border-b border-border-default">
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider"
                >
                  ID
                </th>
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider"
                >
                  Billing Period
                </th>
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider"
                >
                  Shipments
                </th>
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider"
                >
                  Total Weight
                </th>
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider"
                >
                  Amount
                </th>
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider"
                >
                  Generated At
                </th>
                <th
                  class="py-4 px-6 text-xs font-bold text-text-secondary uppercase tracking-wider text-right"
                >
                  Action
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border-default">
              <tr
                v-for="invoice in filteredInvoices"
                :key="invoice.id"
                class="hover:bg-bg-surface transition-colors cursor-pointer group"
                @click="openInvoiceDetails(invoice)"
              >
                <td class="py-4 px-6 text-sm text-text-primary font-medium">
                  #INV-{{ String(invoice.id).padStart(3, '0') }}
                </td>
                <td class="py-4 px-6 text-sm text-text-secondary capitalize">
                  {{ formatMonth(invoice.billing_month) }}
                </td>
                <td class="py-4 px-6 text-sm text-text-secondary">{{ invoice.total_shipment }}</td>
                <td class="py-4 px-6 text-sm text-text-secondary">{{ invoice.total_weight }} kg</td>
                <td class="py-4 px-6 text-sm font-bold text-text-primary">
                  ₴{{ (invoice.total_amount || 0).toLocaleString() }}
                </td>
                <td class="py-4 px-6 text-sm text-text-secondary">
                  {{ formatDate(invoice.generated_at) }}
                </td>
                <td class="py-4 px-6 text-right">
                  <button
                    class="bg-brand-primary/10 text-brand-primary px-4 py-1.5 rounded-full text-xs font-semibold hover:bg-brand-primary hover:text-white transition-colors"
                  >
                    View Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <BaseModal :show="showDetailsModal" @cancel="showDetailsModal = false" title="Invoice Details">
      <div class="flex flex-col">
        <h3 class="text-xl font-bold text-text-primary">
          Invoice Details #INV-{{ String(selectedInvoice?.id).padStart(3, '0') }}
        </h3>
        <p class="text-sm text-text-secondary">
          Shipment History for
          {{ selectedInvoice ? formatMonth(selectedInvoice.billing_month) : '' }}
        </p>
      </div>

      <div class="mt-4">
        <div v-if="isDetailsLoading" class="flex justify-center py-10">
          <Loader2 class="w-8 h-8 animate-spin text-brand-primary" />
        </div>
        <div
          v-else-if="invoiceShipments.length === 0"
          class="text-center py-10 text-text-secondary"
        >
          No individual shipment records found for this period.
        </div>
        <div v-else class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
          <div
            v-for="order in invoiceShipments"
            :key="order.id"
            class="flex items-center justify-between p-4 bg-bg-surface rounded-lg border border-border-default hover:border-brand-primary/30 transition-colors cursor-pointer"
            @click="router.push(`/recipient/orders/${order.id}`)"
          >
            <div class="flex-1">
              <div class="font-bold text-sm text-text-primary">{{ order.title }}</div>
              <div class="text-[10px] text-text-secondary flex items-center gap-1 mt-1">
                <span>{{ order.origin_address }}</span>
                <ChevronRight class="w-2 h-2" />
                <span>{{ order.destination_address }}</span>
              </div>
            </div>
            <div class="text-right ml-4">
              <div class="font-bold text-sm text-brand-primary">
                ₴{{ order.total_amount.toLocaleString() }}
              </div>
              <div class="text-[10px] text-text-placeholder uppercase font-bold">
                {{ order.received_at ? new Date(order.received_at).toLocaleDateString() : '' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full">
          <div class="text-left">
            <span class="text-xs text-text-secondary block">Total Amount</span>
            <span class="text-lg font-bold text-brand-primary"
              >₴{{ selectedInvoice?.total_amount.toLocaleString() }}</span
            >
          </div>
          <BaseButton variant="secondary" @click="showDetailsModal = false">Close</BaseButton>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
