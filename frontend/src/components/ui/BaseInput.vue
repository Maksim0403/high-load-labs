<script setup lang="ts">
const model = defineModel<string | number>()
defineProps<{
  label: string
  type?: string
  placeholder?: string
  error?: string
}>()

defineEmits<{
  (e: 'blur', event: FocusEvent): void
}>()
</script>

<template>
  <div class="flex flex-col gap-1 w-full">
    <label class="text-text-primary text-sm font-normal leading-[140%]">{{ label }}</label>
    <div
      class="flex items-center gap-2 h-12 px-4 bg-bg-surface border-b transition-colors"
      :class="[error ? 'border-red-500' : 'border-border-default focus-within:border-border-focus']"
    >
      <input
        v-model="model"
        :type="type || 'text'"
        :placeholder="placeholder"
        @blur="$emit('blur', $event)"
        class="flex-1 bg-transparent text-base text-text-primary placeholder-text-placeholder outline-none font-normal leading-[140%]"
      />
      <slot name="suffix" />
    </div>
    <span v-if="error" class="text-[10px] text-red-500 font-bold uppercase tracking-wider mt-0.5">
      {{ error }}
    </span>
  </div>
</template>
