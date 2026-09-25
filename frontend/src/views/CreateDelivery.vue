<script setup lang="ts">
import { reactive, ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/axios'
import { ordersApi } from '@/api/orders'
import type { Order } from '@/types'
import { Package, X, Copy, ChevronDown } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import { getErrorMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth.ts'

interface OrderForm {
  title: string
  description: string
  weight: string
  volume: string
  quantity: string
  origin_address: string
  destination_address: string
  distance: string
  isTemplate: boolean
  tariff: string
}

const STORAGE_KEY = 'order-form-draft'
const DEFAULT_TARIFF = 45 // UAH per kg

const router = useRouter()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()
const isSubmitting = ref(false)
const templates = ref<Order[]>([])
const showTemplates = ref(false)

const errors = reactive({
  title: '',
  weight: '',
  volume: '',
  quantity: '',
  origin_address: '',
  destination_address: '',
  distance: '',
  tariff: '',
})

const savedDraft = localStorage.getItem(STORAGE_KEY)

const form = reactive<OrderForm>(
  savedDraft
    ? JSON.parse(savedDraft)
    : {
        title: '',
        description: '',
        weight: '',
        volume: '',
        quantity: '',
        origin_address: '',
        destination_address: '',
        distance: '0',
        isTemplate: false,
        tariff: DEFAULT_TARIFF.toString(),
      },
)

const estimatedCost = computed(() => {
  const w = parseFloat(form.weight)
  const t = parseFloat(form.tariff)
  if (isNaN(w) || isNaN(t)) return 0
  return w * t
})

onMounted(async () => {
  try {
    templates.value = await ordersApi.getTemplates()
  } catch (err) {
    console.error('Failed to load templates:', err)
  }
})

const applyTemplate = (template: Order) => {
  form.title = template.title
  form.description = template.description || ''
  form.weight = template.weight.toString()
  form.origin_address = template.origin_address || ''
  form.destination_address = template.destination_address || ''
  form.distance = template.distance ? template.distance.toString() : '0'
  form.volume = ''
  form.quantity = ''
  form.isTemplate = true
  showTemplates.value = false
  Object.keys(errors).forEach((key) => (errors[key as keyof typeof errors] = ''))
}

watch(
  () => form.title,
  () => {
    if (form.title.length >= 3) errors.title = ''
  },
)

watch(
  () => form.weight,
  () => {
    if (parseFloat(form.weight) > 0) errors.weight = ''
  },
)

watch(
  () => form.distance,
  () => {
    if (parseFloat(form.distance) > 0) errors.distance = ''
  },
)

watch(
  () => form.volume,
  () => {
    if (!form.volume || parseFloat(form.volume) > 0) errors.volume = ''
  },
)

watch(
  () => form.quantity,
  () => {
    if (!form.quantity || parseInt(form.quantity) > 0) errors.quantity = ''
  },
)

watch(
  () => form.origin_address,
  () => {
    if (form.origin_address) errors.origin_address = ''
  },
)

watch(
  () => form.destination_address,
  () => {
    if (form.destination_address) errors.destination_address = ''
  },
)

watch(
  form,
  (newVal) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
  },
  { deep: true },
)

const submitOrder = async () => {
  Object.keys(errors).forEach((key) => (errors[key as keyof typeof errors] = ''))

  let hasError = false
  if (!form.title || form.title.length < 3) {
    errors.title = 'Title must be at least 3 characters'
    hasError = true
  } else if (form.title.length > 100) {
    errors.title = 'Title must be less than 100 characters'
    hasError = true
  }

  if (!form.weight || parseFloat(form.weight) <= 0) {
    errors.weight = 'Weight must be a positive number'
    hasError = true
  }

  if (!form.distance || parseFloat(form.distance) <= 0) {
    errors.distance = 'Distance must be a positive number'
    hasError = true
  }

  if (form.volume && parseFloat(form.volume) <= 0) {
    errors.volume = 'Volume must be a positive number'
    hasError = true
  }

  if (form.quantity && parseInt(form.quantity) <= 0) {
    errors.quantity = 'Quantity must be at least 1'
    hasError = true
  }

  if (!form.origin_address) {
    errors.origin_address = 'Origin address is required'
    hasError = true
  }
  if (!form.destination_address) {
    errors.destination_address = 'Destination address is required'
    hasError = true
  }

  if (hasError) {
    showError('Please fill all the required fields correctly.')
    return
  }

  isSubmitting.value = true

  try {
    const enrichedDescription = `Quantity: ${form.quantity || 'N/A'}, Volume: ${form.volume || 'N/A'}. ${form.description || ''}`

    await apiClient.post('/orders/', {
      title: form.title,
      description: enrichedDescription,
      weight: parseFloat(form.weight),
      distance: parseFloat(form.distance),
      total_amount: estimatedCost.value,
      origin_address: form.origin_address,
      destination_address: form.destination_address,
      is_template: form.isTemplate,
    })
    showSuccess('Delivery created successfully!')
    localStorage.removeItem(STORAGE_KEY)
    router.push('/recipient/orders')
  } catch (err: unknown) {
    console.error('Error creating order:', err)
    showError(getErrorMessage(err))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="p-4 md:p-8 max-w-7xl mx-auto text-primary font-roboto">
    <div class="mb-8 flex flex-col md:flex-row justify-between items-start gap-4">
      <div>
        <h1 class="text-2xl md:text-[32px] font-bold mb-1">Create New Delivery</h1>
        <p class="text-gray-500 text-sm md:text-base">Specify details for your shipment</p>
      </div>

      <div class="relative w-full md:w-auto" v-if="templates.length > 0">
        <button
          @click="showTemplates = !showTemplates"
          type="button"
          class="w-full md:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-bg-surface border border-border-default rounded hover:bg-gray-50 transition-colors text-sm font-bold"
        >
          <Copy class="w-4 h-4 text-brand-primary" />
          Use Template
          <ChevronDown
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-180': showTemplates }"
          />
        </button>

        <div
          v-if="showTemplates"
          class="absolute right-0 mt-2 w-full md:w-64 bg-white border border-border-default rounded-lg shadow-xl z-50 py-2"
        >
          <div
            v-for="template in templates"
            :key="template.id"
            @click="applyTemplate(template)"
            class="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b last:border-0 border-gray-100"
          >
            <div class="font-bold text-sm">{{ template.title }}</div>
            <div class="text-xs text-text-secondary">{{ template.weight }} kg</div>
          </div>
        </div>
      </div>
    </div>

    <form @submit.prevent="submitOrder">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-bg-canvas p-6 border border-gray-200 rounded-lg shadow-sm h-full">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-sm font-bold tracking-wider text-text-secondary uppercase">
                Shipment Information
              </h2>
              <span class="text-[10px] text-text-placeholder font-bold">* REQUIRED</span>
            </div>

            <div class="space-y-6">
              <BaseInput
                v-model="form.title"
                label="Delivery Title *"
                placeholder="e.g. Weekly Electronics Supply"
                :error="errors.title"
              />

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <BaseInput
                  v-model="form.origin_address"
                  label="Origin Address *"
                  placeholder="e.g. 123 Main St, City, Country"
                  :error="errors.origin_address"
                />
                <BaseInput
                  v-model="form.destination_address"
                  label="Destination Address *"
                  placeholder="e.g. 456 Delivery Ave, City, Country"
                  :error="errors.destination_address"
                />
              </div>

              <BaseInput
                v-model="form.distance"
                label="Estimated Distance (km) *"
                type="number"
                placeholder="0.0"
                step="0.1"
                :error="errors.distance"
              />

              <div class="flex flex-col gap-1 w-full">
                <label class="text-text-primary text-sm font-normal leading-[140%]">
                  Description (Optional)
                </label>
                <textarea
                  v-model="form.description"
                  rows="6"
                  placeholder="Any additional notes for the logistics company..."
                  class="px-4 py-3 bg-bg-surface border-b border-border-default focus:border-border-focus text-base text-text-primary placeholder-text-placeholder outline-none resize-none transition-colors rounded-t"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-bg-canvas p-6 border border-gray-200 rounded-lg shadow-sm">
            <h2 class="text-sm font-bold tracking-wider text-text-secondary uppercase mb-6">
              Package Specifications
            </h2>

            <div class="space-y-6">
              <BaseInput
                v-model="form.weight"
                label="Weight (kg) *"
                type="number"
                placeholder="0.0"
                :error="errors.weight"
              />
              <BaseInput
                v-model="form.volume"
                label="Volume (m³)"
                type="number"
                placeholder="0.0"
                :error="errors.volume"
              />
              <BaseInput
                v-model="form.quantity"
                label="Quantity"
                type="number"
                placeholder="1"
                :error="errors.quantity"
              />
            </div>
          </div>

          <div
            v-if="authStore.isManager"
            class="bg-bg-canvas p-6 border border-gray-200 rounded-lg shadow-sm"
          >
            <h2 class="text-sm font-bold tracking-wider text-text-secondary uppercase mb-6">
              Pricing & Tariff (Manager Only)
            </h2>

            <div class="space-y-6">
              <BaseInput
                v-model="form.tariff"
                label="Tariff (UAH/kg)"
                type="number"
                placeholder="45"
                :error="errors.tariff"
              />
              <div class="p-4 bg-bg-surface rounded-lg border border-border-default">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-text-secondary">Estimated Total:</span>
                  <span class="text-lg font-bold text-brand-primary"
                    >₴{{ estimatedCost.toLocaleString() }}</span
                  >
                </div>
              </div>
            </div>
          </div>

          <div v-else class="bg-bg-canvas p-6 border border-gray-200 rounded-lg shadow-sm">
            <h2 class="text-sm font-bold tracking-wider text-text-secondary uppercase mb-4">
              Estimated Delivery Cost
            </h2>
            <div
              class="flex justify-between items-center p-4 bg-brand-primary/5 rounded border border-brand-primary/10"
            >
              <div class="flex flex-col">
                <span class="text-[10px] text-brand-primary font-black uppercase tracking-widest"
                  >Est. Total</span
                >
                <span class="text-xl font-bold text-text-primary"
                  >₴{{ estimatedCost.toLocaleString() }}</span
                >
              </div>
              <div class="text-right">
                <span class="text-[10px] text-text-placeholder font-bold uppercase block"
                  >Rate</span
                >
                <span class="text-xs font-medium text-text-secondary"
                  >₴{{ DEFAULT_TARIFF }}/kg</span
                >
              </div>
            </div>
            <p class="text-[10px] text-text-placeholder mt-3 italic leading-relaxed">
              * The final price will be confirmed by a manager after shipment review and weighing.
            </p>
          </div>

          <div class="bg-bg-canvas p-6 border border-gray-200 rounded-lg shadow-sm">
            <h2 class="text-sm font-bold tracking-wider text-text-secondary uppercase mb-4">
              Options
            </h2>
            <BaseCheckbox v-model="form.isTemplate" label="Save this as a template" />
          </div>
        </div>
      </div>

      <div class="flex flex-col-reverse md:flex-row gap-4 md:justify-end">
        <BaseButton
          variant="secondary"
          type="button"
          class="w-full md:w-auto px-8"
          @click="$router.back()"
        >
          <X class="w-4 h-4 mr-2" /> Cancel
        </BaseButton>

        <BaseButton type="submit" :disabled="isSubmitting" class="w-full md:w-auto px-10">
          <Package class="w-4 h-4 mr-2" />
          {{ isSubmitting ? 'Processing...' : 'Create Shipment' }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>
