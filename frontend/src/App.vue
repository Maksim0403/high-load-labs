<script setup lang="ts">
import { RouterView } from 'vue-router'
import BaseToast from '@/components/ui/BaseToast.vue'
import ErrorBoundary from '@/components/ui/ErrorBoundary.vue'
</script>

<template>
  <ErrorBoundary>
    <RouterView />
  </ErrorBoundary>
  <BaseToast />
</template>

<style scoped></style>
