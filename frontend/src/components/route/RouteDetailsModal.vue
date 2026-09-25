<script setup lang="ts">
import { Loader2, Trash2, Info } from 'lucide-vue-next'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import type { Route, DeliveryPhoto } from '@/types'

defineProps<{
  show: boolean
  route: Route | null
  status: string
  photos: DeliveryPhoto[]
  isFetchingPhotos: boolean
}>()

const emit = defineEmits(['close', 'deletePhoto', 'previewPhoto'])

const extractDetails = (description: string | null | undefined) => {
  if (!description) {
    return { qty: '—', vol: '—', desc: 'No instructions' }
  }

  const qtyMatch = description.match(/Quantity: ([^,.]+)/)
  const volMatch = description.match(/Volume: ([^,.]+)/)

  const cleanDesc = description
    .replace(/Quantity: [^,.]+[,.]?\s*/i, '')
    .replace(/Volume: [^,.]+[,.]?\s*/i, '')
    .trim()

  return {
    qty: qtyMatch ? qtyMatch[1]?.trim() : '—',
    vol: volMatch ? volMatch[1]?.trim() : '—',
    desc: cleanDesc || 'No additional instructions',
  }
}
</script>

<template>
  <BaseModal :show="show" @cancel="emit('close')" title="Order Details">
    <div v-if="route" class="space-y-6 py-2">
      <div class="flex items-center justify-between border-b pb-4">
        <div>
          <p class="text-[10px] font-black text-text-placeholder uppercase">Order ID</p>
          <p class="text-lg font-bold">#{{ route.order_id }}</p>
        </div>
        <div class="text-right">
          <p class="text-[10px] font-black text-text-placeholder uppercase">Current Status</p>
          <span
            class="text-xs font-bold bg-brand-primary/10 text-brand-primary px-2 py-1 rounded uppercase"
          >
            {{ status || 'Assigned' }}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="p-3 bg-bg-surface rounded-lg border border-border-default">
          <p class="text-[9px] font-black text-text-placeholder uppercase mb-1">Pickup Address</p>
          <p class="text-sm font-medium leading-tight">
            {{ route.order?.origin_address }}
          </p>
        </div>
        <div class="p-3 bg-bg-surface rounded-lg border border-border-default">
          <p class="text-[9px] font-black text-text-placeholder uppercase mb-1">Delivery Address</p>
          <p class="text-sm font-medium leading-tight">
            {{ route.order?.destination_address }}
          </p>
        </div>
      </div>

      <div>
        <p class="text-[10px] font-black text-text-placeholder uppercase mb-2">Order Information</p>
        <div class="bg-white border rounded-lg overflow-hidden">
          <div class="p-4 border-b flex justify-between items-center">
            <span class="text-sm font-bold text-text-primary">{{ route.order?.title }}</span>
            <span class="text-xs font-bold text-brand-primary">{{ route.order?.weight }} kg</span>
          </div>
          <div class="p-4 bg-bg-surface/30">
            <p class="text-xs text-text-secondary whitespace-pre-wrap leading-relaxed">
              {{ extractDetails(route.order?.description).desc }}
            </p>
          </div>
        </div>
      </div>

      <div>
        <p class="text-[10px] font-black text-text-placeholder uppercase mb-2">
          Damaged Package Photos
        </p>
        <div v-if="isFetchingPhotos" class="flex justify-center py-4">
          <Loader2 class="w-6 h-6 text-brand-primary animate-spin" />
        </div>
        <div v-else-if="photos.length > 0" class="grid grid-cols-2 gap-3">
          <div
            v-for="photo in photos"
            :key="photo.id"
            class="relative rounded-lg overflow-hidden border border-border-default group cursor-pointer"
            @click="emit('previewPhoto', photo.url)"
          >
            <img :src="photo.url" class="w-full h-32 object-cover" alt="Package photo" />
            <div
              class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
            >
              <button
                @click.stop="emit('deletePhoto', photo.id)"
                class="p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        <div v-else class="p-4 bg-bg-surface border border-dashed rounded-lg text-center">
          <p class="text-xs text-text-secondary">No photos uploaded yet</p>
        </div>
      </div>

      <div
        class="flex items-center gap-3 p-4 bg-brand-primary/5 rounded-lg border border-brand-primary/10"
      >
        <Info class="w-5 h-5 text-brand-primary flex-shrink-0" />
        <p class="text-xs text-text-primary">
          Please ensure you have all documents signed before marking as
          <span class="font-bold">Delivered</span>.
        </p>
      </div>
    </div>
    <template #footer>
      <BaseButton variant="primary" @click="emit('close')" class="w-full"> Close </BaseButton>
    </template>
  </BaseModal>
</template>
