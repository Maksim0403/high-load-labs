<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { AlertCircle, RefreshCw } from 'lucide-vue-next'
import BaseButton from './BaseButton.vue'

const error = ref<Error | null>(null)

onErrorCaptured((err) => {
  error.value = err as Error
  return false // prevent error from bubbling further
})

const resetError = () => {
  error.value = null
  window.location.reload()
}
</script>

<template>
  <div
    v-if="error"
    class="min-h-[400px] flex flex-col items-center justify-center p-8 text-center bg-bg-surface border border-border-default rounded-xl shadow-sm"
  >
    <div
      class="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mb-6"
    >
      <AlertCircle class="w-10 h-10" />
    </div>

    <h2 class="text-2xl font-bold text-text-primary mb-2">Something went wrong</h2>
    <p class="text-text-secondary mb-8 max-w-md mx-auto">
      An unexpected error occurred while rendering this part of the application. Please try
      refreshing the page or contact support if the problem persists.
    </p>

    <div
      class="p-4 bg-red-50 border border-red-200 rounded-lg mb-8 text-left w-full max-w-lg overflow-auto"
    >
      <p class="text-xs font-mono text-red-700 whitespace-pre-wrap">{{ error.message }}</p>
    </div>

    <BaseButton variant="primary" @click="resetError" class="flex items-center gap-2">
      <RefreshCw class="w-4 h-4" />
      Reload Application
    </BaseButton>
  </div>
  <slot v-else />
</template>
