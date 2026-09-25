<script setup lang="ts">
defineProps<{
  active: boolean
}>()
</script>

<template>
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="transition-colors duration-200"
  >
    <template v-if="!active">
      <path
        d="M20 12C20 10.19 16.24 8.015 11.993 8C7.775 7.985 4 10.178 4 12C4 13.825 7.754 16.006 11.997 16C16.252 15.994 20 13.82 20 12Z"
        stroke="currentColor"
        stroke-width="1.5"
      />
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.5" />
    </template>

    <template v-else>
      <path
        d="M3.27 3L2 4.27l4.69 4.69C5.06 10.06 4 11.21 4 12c0 2 4 6 8 6 1.07 0 2.1-.27 3.06-.75l1.97 1.97L18.73 21 20 19.73 3.27 3zm5.42 5.42L14.31 14a4 4 0 01-5.62-5.58zM12 6c-1.07 0-2.1.27-3.06.75L10.92 8.73A4 4 0 0115.27 13.08L17.31 15.1C18.94 13.94 20 12.21 20 12c0-2-4-6-8-6z"
        fill="currentColor"
      />
    </template>
  </svg>
</template>
