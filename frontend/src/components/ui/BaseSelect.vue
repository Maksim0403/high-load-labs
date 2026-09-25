<script setup lang="ts">
const model = defineModel<string>()
defineProps<{
  label: string
  options: { value: string; label: string }[]
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
      class="flex items-center gap-2 h-12 px-4 bg-bg-surface border-b transition-colors relative"
      :class="[error ? 'border-red-500' : 'border-border-default']"
    >
      <select
        v-model="model"
        @blur="$emit('blur', $event)"
        class="flex-1 bg-transparent text-base text-text-primary outline-none appearance-none cursor-pointer"
      >
        <option value="" disabled>Select option</option>
        <option v-for="opt in options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      <svg
        class="absolute right-4 pointer-events-none"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
      >
        <path
          d="M12.071 13.314L17.021 8.364C17.1133 8.26849 17.2236 8.19231 17.3456 8.1399C17.4676 8.08749 17.5988 8.0599 17.7316 8.05875C17.8644 8.0576 17.9961 8.0829 18.119 8.13318C18.2419 8.18346 18.3535 8.25771 18.4474 8.35161C18.5413 8.4455 18.6156 8.55715 18.6658 8.68005C18.7161 8.80294 18.7414 8.93462 18.7403 9.0674C18.7391 9.20018 18.7115 9.3314 18.6591 9.4534C18.6067 9.57541 18.5305 9.68575 18.435 9.778L12.778 15.435C12.5905 15.6225 12.3362 15.7278 12.071 15.7278C11.8059 15.7278 11.5515 15.6225 11.364 15.435L5.70702 9.778C5.61151 9.68575 5.53533 9.57541 5.48292 9.4534C5.43051 9.3314 5.40292 9.20018 5.40177 9.0674C5.40062 8.93462 5.42592 8.80294 5.4762 8.68005C5.52648 8.55715 5.60073 8.4455 5.69463 8.35161C5.78852 8.25771 5.90017 8.18346 6.02307 8.13318C6.14596 8.0829 6.27764 8.0576 6.41042 8.05875C6.5432 8.0599 6.67442 8.08749 6.79643 8.1399C6.91843 8.19231 7.02877 8.26849 7.12102 8.364L12.071 13.314Z"
          fill="#9CA3AF"
        />
      </svg>
    </div>
    <span v-if="error" class="text-[10px] text-red-500 font-bold uppercase tracking-wider mt-0.5">
      {{ error }}
    </span>
  </div>
</template>
