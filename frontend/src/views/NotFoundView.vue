<script setup lang="ts">
import { useRouter } from 'vue-router'
import { FileQuestion, Home, ArrowLeft } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-bg-canvas flex items-center justify-center p-6 font-roboto">
    <div class="max-w-md w-full text-center">
      <div class="mb-8 flex justify-center">
        <div class="relative">
          <FileQuestion class="w-32 h-32 text-brand-primary opacity-20" />
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-6xl font-black text-brand-primary">404</span>
          </div>
        </div>
      </div>

      <h1 class="text-3xl font-bold text-text-primary mb-4">Page Not Found</h1>
      <p class="text-text-secondary mb-10 text-lg">
        The page you are looking for might have been removed, had its name changed, or is
        temporarily unavailable.
      </p>

      <div class="flex flex-col gap-4">
        <BaseButton variant="primary" @click="goHome">
          <Home class="w-4 h-4 mr-2" /> Back to Home
        </BaseButton>

        <BaseButton variant="secondary" @click="goBack">
          <ArrowLeft class="w-4 h-4 mr-2" /> Go Back
        </BaseButton>
      </div>

      <div class="mt-12 pt-8 border-t border-border-default">
        <p class="text-xs text-text-placeholder font-bold uppercase tracking-widest">
          LogiFlow Transportation System
        </p>
      </div>
    </div>
  </div>
</template>
