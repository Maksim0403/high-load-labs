<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import { User, Mail, Phone, Truck, LogOut, ChevronRight } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const user = authStore.user
const router = useRouter()

const goToVehicle = () => {
  router.push('/driver/vehicle')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="p-4 md:p-8 w-full font-roboto text-text-primary max-w-6xl mx-auto">
    <div class="mb-8">
      <h1 class="text-2xl md:text-[32px] font-bold leading-tight">Settings</h1>
      <p class="text-text-secondary">Manage your account preferences and profile information.</p>
    </div>

    <div v-if="user" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="lg:col-span-1 space-y-6">
        <section
          class="bg-bg-canvas border border-border-default rounded-lg p-6 shadow-sm text-center"
        >
          <div class="relative inline-block mb-4">
            <div
              class="w-24 h-24 bg-brand-primary text-white flex items-center justify-center rounded-full text-3xl font-bold mx-auto border-4 border-bg-surface"
            >
              {{ user.full_name.charAt(0) }}
            </div>
            <div
              class="absolute bottom-0 right-0 p-1.5 bg-green-500 border-2 border-bg-surface rounded-full shadow-sm"
              title="Active Account"
            ></div>
          </div>
          <h2 class="text-xl font-bold">{{ user.full_name }}</h2>
          <p class="text-text-secondary text-sm capitalize mb-6">{{ user.role }}</p>

          <div class="space-y-2 text-left">
            <div
              v-if="authStore.isDriver"
              @click="goToVehicle"
              class="flex items-center justify-between p-3 rounded-md hover:bg-bg-surface cursor-pointer transition-colors group"
            >
              <div class="flex items-center gap-3">
                <Truck class="w-4 h-4 text-brand-primary" />
                <span class="text-sm font-medium">My Vehicle</span>
              </div>
              <ChevronRight class="w-4 h-4 text-text-placeholder group-hover:text-brand-primary" />
            </div>
          </div>

          <div class="mt-8 pt-6 border-t border-border-default">
            <button
              @click="handleLogout"
              class="w-full flex items-center justify-center gap-2 py-2 px-4 text-red-600 hover:bg-red-50 rounded-md transition-colors font-bold text-sm"
            >
              <LogOut class="w-4 h-4" /> Sign Out
            </button>
          </div>
        </section>
      </div>

      <div class="lg:col-span-2 space-y-8">
        <section class="bg-bg-canvas border border-border-default rounded-lg p-6 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold flex items-center gap-2">
              <User class="w-5 h-5 text-brand-primary" /> Profile Details
            </h3>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-1.5">
              <label class="text-[10px] font-black text-text-placeholder uppercase tracking-widest"
                >Full Name</label
              >
              <div
                class="flex items-center gap-3 px-4 py-3 bg-bg-surface border border-border-default rounded text-sm"
              >
                <span>{{ user.full_name }}</span>
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[10px] font-black text-text-placeholder uppercase tracking-widest"
                >Account Role</label
              >
              <div
                class="flex items-center gap-3 px-4 py-3 bg-bg-surface border border-border-default rounded text-sm capitalize"
              >
                <span>{{ user.role }}</span>
              </div>
            </div>

            <div class="space-y-1.5 md:col-span-2">
              <label class="text-[10px] font-black text-text-placeholder uppercase tracking-widest"
                >Email Address</label
              >
              <div
                class="flex items-center gap-3 px-4 py-3 bg-bg-surface border border-border-default rounded text-sm"
              >
                <Mail class="w-4 h-4 text-text-placeholder" />
                <span>{{ user.email }}</span>
              </div>
            </div>

            <div class="space-y-1.5 md:col-span-2">
              <label class="text-[10px] font-black text-text-placeholder uppercase tracking-widest"
                >Phone Number</label
              >
              <div
                class="flex items-center gap-3 px-4 py-3 bg-bg-surface border border-border-default rounded text-sm"
              >
                <Phone class="w-4 h-4 text-text-placeholder" />
                <span>{{ user.phone_number }}</span>
              </div>
            </div>
          </div>
        </section>

        <section
          v-if="authStore.isDriver && user.vehicle"
          class="bg-bg-canvas border border-border-default rounded-lg p-6 shadow-sm"
        >
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold flex items-center gap-2">
              <Truck class="w-5 h-5 text-brand-primary" /> Vehicle Assignment
            </h3>
            <BaseButton variant="secondary" size="sm" @click="goToVehicle">Manage</BaseButton>
          </div>

          <div class="p-4 bg-brand-primary/5 border border-brand-primary/10 rounded-lg">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-bold text-text-primary">
                  {{ user.vehicle.brand }} {{ user.vehicle.model }}
                </p>
                <p class="text-xs text-text-secondary uppercase tracking-tighter mt-1">
                  License: {{ user.vehicle.license_plate }}
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div v-else class="flex flex-col items-center justify-center py-20 text-center">
      <div class="p-4 bg-bg-surface rounded-full mb-4">
        <User class="w-12 h-12 text-text-placeholder" />
      </div>
      <h3 class="text-xl font-bold text-text-primary mb-2">Profile Not Found</h3>
      <p class="text-text-secondary mb-6">We couldn't load your profile information.</p>
      <BaseButton @click="router.push('/dashboard')">Back to Dashboard</BaseButton>
    </div>
  </div>
</template>
