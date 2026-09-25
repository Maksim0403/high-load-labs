<script setup lang="ts">
defineProps<{
  updates: { time: string; text: string }[]
}>()
</script>

<template>
  <div>
    <div class="flex flex-col gap-1">
      <div
        v-for="(update, idx) in updates"
        :key="idx"
        class="bg-bg-canvas border border-border-default rounded flex items-center px-4 py-3 text-sm"
      >
        <span class="text-text-placeholder w-28 shrink-0">{{ update.time }}</span>
        <span class="text-text-primary">{{ update.text }}</span>
      </div>
    </div>
  </div>
</template>
