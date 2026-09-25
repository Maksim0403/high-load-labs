<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
const driverLinks = [
  { name: "Today's Route", path: '/driver/route', icon: 'Route' },
  { name: 'My Vehicle', path: '/driver/vehicle', icon: 'Truck' },
  { name: 'Settings', path: '/driver/settings', icon: 'Settings' },
]
</script>

<template>
  <AppLayout :links="driverLinks" />
</template>
