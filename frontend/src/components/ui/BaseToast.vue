<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-vue-next'

const store = useToastStore()
</script>

<template>
  <div
    class="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none w-full max-w-sm"
  >
    <TransitionGroup
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-2 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-for="toast in store.toasts"
        :key="toast.id"
        class="flex items-center gap-3 px-6 py-4 rounded-xl shadow-2xl border pointer-events-auto"
        :class="[
          toast.type === 'success' ? 'bg-green-600 border-green-500 text-white' : '',
          toast.type === 'error' ? 'bg-red-600 border-red-500 text-white' : '',
          toast.type === 'info' ? 'bg-blue-600 border-blue-500 text-white' : '',
        ]"
      >
        <CheckCircle2 v-if="toast.type === 'success'" class="w-5 h-5" />
        <AlertCircle v-if="toast.type === 'error'" class="w-5 h-5" />
        <Info v-if="toast.type === 'info'" class="w-5 h-5" />

        <p class="text-sm font-bold tracking-wide uppercase flex-1">{{ toast.message }}</p>

        <button
          @click="store.removeToast(toast.id)"
          class="ml-2 hover:opacity-70 transition-opacity"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
