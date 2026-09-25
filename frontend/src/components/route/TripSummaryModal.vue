<script setup lang="ts">
import { CheckCircle2 } from 'lucide-vue-next'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps<{
  show: boolean
  summary: {
    distance: number
    fuel: number
    cost: number
  }
}>()

const emit = defineEmits(['close'])
</script>

<template>
  <BaseModal :show="show" @cancel="emit('close')" title="Route Completed!">
    <div class="py-4 text-center">
      <div
        class="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6"
      >
        <CheckCircle2 class="w-10 h-10" />
      </div>
      <h3 class="text-xl font-bold mb-2">Great job!</h3>
      <p class="text-text-secondary mb-8">Trip details have been calculated automatically.</p>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-bg-surface p-4 rounded-xl border border-border-default">
          <p class="text-[10px] font-black text-text-placeholder uppercase mb-1">
            Estimated Distance
          </p>
          <p class="text-2xl font-bold text-text-primary">
            {{ summary.distance }} <span class="text-sm font-medium">km</span>
          </p>
        </div>
        <div class="bg-brand-primary/5 p-4 rounded-xl border border-brand-primary/10">
          <p class="text-[10px] font-black text-brand-primary uppercase mb-1">Fuel Consumed</p>
          <p class="text-2xl font-bold text-brand-primary">
            {{ summary.fuel.toFixed(2) }} <span class="text-sm font-medium">L</span>
          </p>
        </div>
        <div class="bg-brand-primary/10 p-4 rounded-xl border border-border-default">
          <p class="text-[10px] font-black text-brand-primary uppercase mb-1">Fuel Cost</p>
          <p class="text-2xl font-bold text-brand-primary">
            {{ summary.cost.toFixed(2) }} <span class="text-sm font-medium">UAH</span>
          </p>
        </div>
      </div>
    </div>
    <template #footer>
      <BaseButton variant="primary" @click="emit('close')" class="w-full py-4"> DONE </BaseButton>
    </template>
  </BaseModal>
</template>
