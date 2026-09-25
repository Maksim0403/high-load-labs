<script setup lang="ts">
defineProps<{
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}>()
</script>

<template>
  <button
    :type="type || 'button'"
    :disabled="disabled"
    class="flex items-center justify-center h-12 w-full font-bold transition-all"
    :class="[
      variant === 'secondary'
        ? 'bg-transparent border-2 border-brand-primary text-brand-primary hover:bg-brand-subtle'
        : 'bg-btn-primary-default text-white hover:bg-btn-primary-hover active:bg-btn-primary-pressed',
    ]"
  >
    <slot />
  </button>
</template>
