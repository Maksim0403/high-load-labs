<script setup lang="ts">
const model = defineModel<boolean>()

defineProps<{
  label?: string
}>()
</script>

<template>
  <label class="flex items-center gap-2 cursor-pointer group">
    <div
      class="relative flex items-center justify-center w-4 h-4 border transition-colors"
      :class="
        model
          ? 'bg-btn-primary-default border-btn-primary-default'
          : 'bg-white border-border-default group-hover:border-btn-primary-default'
      "
    >
      <input type="checkbox" v-model="model" class="sr-only" />

      <svg
        v-if="model"
        width="10"
        height="8"
        viewBox="0 0 10 8"
        fill="none"
        class="absolute pointer-events-none"
      >
        <path
          d="M1 4L3.5 6.5L9 1"
          stroke="white"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </div>

    <span v-if="label" class="text-text-primary text-sm select-none">{{ label }}</span>
  </label>
</template>
