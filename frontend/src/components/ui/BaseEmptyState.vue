<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  title: string
  description?: string
  icon?: Component
}>()
</script>

<template>
  <div
    class="bg-white border-2 border-dashed border-border-default rounded-xl p-10 md:p-20 text-center flex flex-col items-center justify-center"
  >
    <component :is="icon" v-if="icon" class="w-16 h-16 text-text-placeholder mb-4 opacity-50" />
    <h3 class="text-xl font-bold text-text-primary">{{ title }}</h3>
    <p v-if="description" class="text-text-secondary mt-2 max-w-md mx-auto">
      {{ description }}
    </p>
    <div v-if="$slots.action" class="mt-6">
      <slot name="action" />
    </div>
  </div>
</template>
