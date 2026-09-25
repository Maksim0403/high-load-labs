<script setup lang="ts">
import { CheckCircle2, Clock, Package, Camera, Loader2 } from 'lucide-vue-next'
import type { Route } from '@/types'

const props = defineProps<{
  route: Route
  index: number
  status: string
  isCurrent: boolean
  isUpdating: boolean
  isStatusDisabled: (routeId: number, status: string) => boolean
  getStatusColor: (routeId: number, status: string) => string
}>()

const emit = defineEmits(['openPhotoUpload', 'openDetails', 'updateStatus'])

const formatDate = (date: string | null): string => {
  if (!date) return '—'
  return new Date(date).toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const extractDetails = (description: string | null | undefined) => {
  if (!description) {
    return { qty: '—', vol: '—', desc: 'No instructions' }
  }

  const qtyMatch = description.match(/Quantity: ([^,.]+)/)
  const volMatch = description.match(/Volume: ([^,.]+)/)

  return {
    qty: qtyMatch ? qtyMatch[1]?.trim() : '—',
    vol: volMatch ? volMatch[1]?.trim() : '—',
  }
}

const details = extractDetails(props.route.order?.description)
</script>

<template>
  <div
    class="bg-white border rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col lg:flex-row items-stretch relative"
    :class="[
      isCurrent ? 'border-brand-primary border-2 shadow-lg z-10' : 'border-border-default',
      status.toLowerCase() === 'delivered' ? 'opacity-75 grayscale-[0.3] bg-bg-surface/10' : '',
    ]"
  >
    <div
      v-if="isCurrent"
      class="absolute top-0 right-0 bg-brand-primary text-white text-[9px] font-black px-4 py-1.5 rounded-bl-lg z-20 uppercase tracking-widest shadow-sm"
    >
      Active Stop
    </div>
    <div
      v-else-if="status.toLowerCase() === 'delivered'"
      class="absolute top-0 right-0 bg-green-500 text-white text-[9px] font-black px-4 py-1.5 rounded-bl-lg z-20 uppercase tracking-widest flex items-center gap-1 shadow-sm"
    >
      <CheckCircle2 class="w-3 h-3" /> Completed
    </div>

    <div
      class="lg:w-40 bg-bg-surface/50 border-b lg:border-b-0 lg:border-r border-border-default p-4 lg:p-6 flex lg:flex-col items-center justify-between lg:justify-center gap-2 text-center"
    >
      <span class="text-[10px] font-black text-text-placeholder uppercase tracking-tighter"
        >STOP #{{ index + 1 }}</span
      >
      <div class="flex flex-row lg:flex-col items-center gap-2">
        <Clock class="w-4 h-4 lg:w-5 lg:h-5 text-brand-primary" />
        <span class="text-lg lg:text-xl font-black text-text-primary">{{
          formatDate(route.eta)
        }}</span>
      </div>
    </div>

    <div class="flex-1 p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="space-y-4">
        <div class="flex items-center gap-2 mb-3">
          <span
            class="text-[10px] bg-brand-primary/10 text-brand-primary px-2 py-0.5 rounded font-bold uppercase"
            >ID: {{ route.id }}</span
          >
          <h2 class="text-lg font-bold text-text-primary">Order #{{ route.order_id }}</h2>
        </div>

        <div class="space-y-3 relative">
          <div
            class="absolute left-[7px] top-3 bottom-3 w-[2px] bg-border-default border-dashed border-l"
          ></div>
          <div class="flex items-start gap-3 relative z-10">
            <div
              class="w-4 h-4 rounded-full bg-orange-400 mt-1 flex-shrink-0 border-2 border-white"
            ></div>
            <div>
              <p class="text-[9px] text-text-placeholder font-bold uppercase leading-none mb-1">
                Pickup From
              </p>
              <p class="text-sm font-bold text-text-primary leading-tight">
                {{ route.order?.origin_address || '—' }}
              </p>
            </div>
          </div>
          <div class="flex items-start gap-3 relative z-10">
            <div
              class="w-4 h-4 rounded-full bg-green-500 mt-1 flex-shrink-0 border-2 border-white"
            ></div>
            <div>
              <p class="text-[9px] text-text-placeholder font-bold uppercase leading-none mb-1">
                Deliver To
              </p>
              <p class="text-sm font-bold text-text-primary leading-tight">
                {{ route.order?.destination_address || '—' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-bg-surface/30 rounded-lg p-4 border border-border-default flex items-center">
        <div class="grid grid-cols-3 w-full gap-2">
          <div class="border-r border-border-default pr-2">
            <p class="text-[9px] text-text-placeholder font-bold uppercase mb-1">Weight</p>
            <div class="flex items-center gap-1 font-bold text-text-primary text-xs">
              <Package class="w-3 h-3 text-brand-primary" />
              <span>{{ route.order?.weight || '—' }}kg</span>
            </div>
          </div>
          <div class="border-r border-border-default px-2">
            <p class="text-[9px] text-text-placeholder font-bold uppercase mb-1">Qty</p>
            <div class="font-bold text-text-primary text-xs">
              {{ details.qty }}
            </div>
          </div>
          <div class="pl-2">
            <p class="text-[9px] text-text-placeholder font-bold uppercase mb-1">Vol</p>
            <div class="font-bold text-text-primary text-xs">
              {{ details.vol }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      class="lg:w-96 p-6 bg-bg-surface/20 border-t lg:border-t-0 lg:border-l border-border-default flex flex-col justify-center gap-4"
    >
      <div class="flex gap-2">
        <button
          @click="emit('openPhotoUpload', route.id)"
          class="flex-1 min-h-[48px] bg-white border border-border-default rounded-lg text-[11px] font-bold text-text-primary hover:bg-bg-surface transition-colors flex items-center justify-center gap-2"
        >
          <Camera class="w-4 h-4 text-brand-primary" /> ADD PHOTO
        </button>
        <button
          @click="emit('openDetails', route)"
          class="px-6 min-h-[48px] bg-white border border-border-default rounded-lg text-[11px] font-bold text-text-primary hover:bg-bg-surface"
        >
          DETAILS
        </button>
      </div>

      <div class="flex p-1.5 bg-white border border-border-default rounded-xl relative">
        <div
          v-if="isUpdating"
          class="absolute inset-0 bg-white/50 z-10 flex items-center justify-center rounded-xl"
        >
          <Loader2 class="w-5 h-5 text-brand-primary animate-spin" />
        </div>

        <button
          v-if="!status"
          @click="emit('updateStatus', route.id, 'assigned')"
          class="flex-1 min-h-[48px] text-[10px] font-black uppercase rounded-lg transition-all bg-brand-primary text-white hover:bg-brand-primary/90 shadow-sm"
        >
          Accept Route
        </button>

        <template v-else>
          <button
            @click="emit('updateStatus', route.id, 'loaded')"
            :disabled="isStatusDisabled(route.id, 'loaded')"
            :class="[
              'flex-1 min-h-[48px] text-[10px] font-black uppercase rounded-lg transition-all disabled:cursor-not-allowed',
              getStatusColor(route.id, 'loaded'),
            ]"
          >
            Loaded
          </button>
          <button
            @click="emit('updateStatus', route.id, 'in_transit')"
            :disabled="isStatusDisabled(route.id, 'in_transit')"
            :class="[
              'flex-1 min-h-[48px] text-[10px] font-black uppercase rounded-lg transition-all mx-1.5 disabled:cursor-not-allowed',
              getStatusColor(route.id, 'in_transit'),
            ]"
          >
            In Transit
          </button>
          <button
            @click="emit('updateStatus', route.id, 'delivered')"
            :disabled="isStatusDisabled(route.id, 'delivered')"
            :class="[
              'flex-1 min-h-[48px] text-[10px] font-black uppercase rounded-lg transition-all disabled:cursor-not-allowed',
              getStatusColor(route.id, 'delivered'),
            ]"
          >
            Delivered
          </button>
        </template>
      </div>
    </div>
  </div>
</template>
