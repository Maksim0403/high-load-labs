<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'

const recipientLinks = [
  { name: 'My Orders', path: '/recipient/orders', icon: 'Package' },
  { name: 'Billings & Reports', path: '/recipient/billing', icon: 'PackageCheck' },
  { name: 'Create New Delivery', path: '/recipient/delivery/new', icon: 'Plus' },
  { name: 'Active Deliveries', path: '/recipient/active', icon: 'FileText' },
  { name: 'Settings', path: '/recipient/settings', icon: 'Settings' },
]
</script>

<template>
  <AppLayout :links="recipientLinks" />
</template>
