<script setup lang="ts">
import { Fuel, Gauge, Wrench, Loader2, Save, Trash2, AlertCircle } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import type { VehicleCreate } from '@/types'

const vehicleForm = defineModel<VehicleCreate>('vehicleForm', { required: true })

defineProps<{
  isEditing: boolean
  isSaving: boolean
  isDeleting: boolean
  error: string
  successMessage: string
}>()

const emit = defineEmits<{
  submit: []
  delete: []
}>()
</script>

<template>
  <section class="bg-bg-canvas border border-border-default rounded-lg p-6 shadow-sm">
    <h2 class="text-xl font-bold mb-6 flex items-center gap-2">Vehicle Specifications</h2>

    <form @submit.prevent="emit('submit')" class="space-y-6">
      <div
        v-if="error"
        class="p-3 bg-red-50 border border-red-200 text-red-600 rounded flex items-center gap-2"
      >
        <AlertCircle class="w-5 h-5" />
        {{ error }}
      </div>

      <div
        v-if="successMessage"
        class="p-3 bg-green-50 border border-green-200 text-green-600 rounded flex items-center gap-2"
      >
        <Save class="w-5 h-5" />
        {{ successMessage }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-1">
          <label class="text-sm font-bold text-text-secondary uppercase tracking-wider"
            >Brand</label
          >
          <input
            v-model="vehicleForm.brand"
            type="text"
            required
            :disabled="isEditing"
            class="w-full px-4 py-3 bg-bg-surface border border-border-default rounded focus:outline-none focus:border-brand-primary disabled:opacity-70 disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="e.g. Mercedes-Benz"
          />
        </div>

        <div class="space-y-1">
          <label class="text-sm font-bold text-text-secondary uppercase tracking-wider"
            >Model</label
          >
          <input
            v-model="vehicleForm.model"
            type="text"
            required
            :disabled="isEditing"
            class="w-full px-4 py-3 bg-bg-surface border border-border-default rounded focus:outline-none focus:border-brand-primary disabled:opacity-70 disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="e.g. Sprinter"
          />
        </div>

        <div class="space-y-1">
          <label class="text-sm font-bold text-text-secondary uppercase tracking-wider"
            >License Plate</label
          >
          <input
            v-model="vehicleForm.license_plate"
            type="text"
            required
            maxlength="8"
            :disabled="isEditing"
            class="w-full px-4 py-3 bg-bg-surface border border-border-default rounded focus:outline-none focus:border-brand-primary disabled:opacity-70 disabled:bg-gray-100 disabled:cursor-not-allowed uppercase"
            placeholder="AA1234BP"
          />
        </div>

        <div class="space-y-1">
          <label class="text-sm font-bold text-text-secondary uppercase tracking-wider"
            >Max Weight (kg)</label
          >
          <input
            v-model.number="vehicleForm.max_weight"
            type="number"
            required
            min="1"
            :disabled="isEditing"
            class="w-full px-4 py-3 bg-bg-surface border border-border-default rounded focus:outline-none focus:border-brand-primary disabled:opacity-70 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>

        <div class="space-y-1">
          <label class="text-sm font-bold text-text-secondary uppercase tracking-wider"
            >Max Volume (m³)</label
          >
          <input
            v-model.number="vehicleForm.max_volume"
            type="number"
            required
            min="0.1"
            step="0.1"
            :disabled="isEditing"
            class="w-full px-4 py-3 bg-bg-surface border border-border-default rounded focus:outline-none focus:border-brand-primary disabled:opacity-70 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>

        <div class="space-y-1">
          <label
            class="text-sm font-bold text-text-secondary uppercase tracking-wider flex items-center gap-2"
          >
            <Fuel class="w-4 h-4 text-brand-primary" /> Fuel Consumption (l/100km)
          </label>
          <input
            v-model.number="vehicleForm.fuel_consumption"
            type="number"
            required
            step="0.1"
            :class="[
              'w-full px-4 py-3 bg-bg-surface border rounded focus:outline-none focus:border-brand-primary',
              vehicleForm.fuel_consumption < 0 ? 'border-red-500' : 'border-border-default',
            ]"
          />
        </div>

        <div class="space-y-1">
          <label
            class="text-sm font-bold text-text-secondary uppercase tracking-wider flex items-center gap-2"
          >
            <Fuel class="w-4 h-4 text-brand-primary" /> Fuel Price (UAH/l)
          </label>
          <input
            v-model.number="vehicleForm.fuel_price"
            type="number"
            required
            step="0.1"
            :class="[
              'w-full px-4 py-3 bg-bg-surface border rounded focus:outline-none focus:border-brand-primary',
              vehicleForm.fuel_price < 0 ? 'border-red-500' : 'border-border-default',
            ]"
          />
        </div>

        <div class="space-y-1">
          <label
            class="text-sm font-bold text-text-secondary uppercase tracking-wider flex items-center gap-2"
          >
            <Gauge class="w-4 h-4 text-brand-primary" /> Current Mileage (km)
          </label>
          <input
            v-model.number="vehicleForm.current_mileage"
            type="number"
            required
            min="0"
            :class="[
              'w-full px-4 py-3 bg-bg-surface border rounded focus:outline-none focus:border-brand-primary',
              vehicleForm.current_mileage < 0 ? 'border-red-500' : 'border-border-default',
            ]"
          />
        </div>

        <div class="space-y-1 md:col-span-2">
          <label
            class="text-sm font-bold text-text-secondary uppercase tracking-wider flex items-center gap-2"
          >
            <Wrench class="w-4 h-4 text-brand-primary" /> Maintenance Interval (km)
          </label>
          <input
            v-model.number="vehicleForm.maintenance_interval"
            type="number"
            required
            min="1000"
            class="w-full px-4 py-3 bg-bg-surface border border-border-default rounded focus:outline-none focus:border-brand-primary"
          />
          <p class="text-xs text-text-secondary mt-1">
            The system will remind you of maintenance every time the mileage increases by this
            interval.
          </p>
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-end gap-3 pt-4">
        <BaseButton
          v-if="isEditing"
          type="button"
          variant="secondary"
          @click="emit('delete')"
          :disabled="isDeleting || isSaving"
          class="text-red-600 border-red-200 hover:bg-red-50"
        >
          <Loader2 v-if="isDeleting" class="w-4 h-4 mr-2 animate-spin" />
          <Trash2 v-else class="w-4 h-4 mr-2" />
          Remove Vehicle
        </BaseButton>

        <BaseButton type="submit" class="px-8 py-3" :disabled="isSaving || isDeleting">
          <Loader2 v-if="isSaving" class="w-4 h-4 mr-2 animate-spin" />
          <Save v-else class="w-4 h-4 mr-2" />
          {{ isEditing ? 'Update Settings' : 'Add Vehicle' }}
        </BaseButton>
      </div>
    </form>
  </section>
</template>
