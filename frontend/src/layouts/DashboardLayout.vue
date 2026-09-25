<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'

const managerLinks = [
  { name: 'Overview Dashboard', path: '/dashboard', icon: 'LayoutDashboard' },
  { name: 'Route Assignment', path: '/route-assignment', icon: 'Truck' },
  { name: 'Shipments', path: '/shipments', icon: 'Package' },
  { name: 'Users', path: '/users', icon: 'Users' },
  { name: 'Settings', path: '/settings', icon: 'Settings' },
]
</script>

<template>
  <AppLayout :links="managerLinks" />
</template>
