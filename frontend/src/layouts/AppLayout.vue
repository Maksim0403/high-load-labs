<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import MainSidebar from '@/components/layout/MainSidebar.vue'
import { Menu } from 'lucide-vue-next'

export interface SidebarLink {
  name: string
  path: string
  icon: string
}

const props = defineProps<{
  links: SidebarLink[]
}>()

const isSidebarOpen = ref(window.innerWidth >= 1024)
let wasDesktop = window.innerWidth >= 1024

const handleResize = () => {
  const isDesktop = window.innerWidth >= 1024
  if (isDesktop !== wasDesktop) {
    isSidebarOpen.value = isDesktop
    wasDesktop = isDesktop
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="flex min-h-screen bg-bg-surface font-roboto">
    <header
      class="lg:hidden fixed top-0 left-0 right-0 h-16 bg-bg-sidebar flex items-center px-4 z-40 shadow-md"
    >
      <button
        @click="isSidebarOpen = true"
        class="p-2 -ml-2 text-text-sidebar-muted hover:text-white transition-colors"
      >
        <Menu class="w-6 h-6" />
      </button>
    </header>

    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isSidebarOpen"
        class="fixed inset-0 bg-black/60 z-30 lg:hidden backdrop-blur-sm"
        @click="isSidebarOpen = false"
      />
    </Transition>

    <MainSidebar
      :links="props.links"
      :is-open="isSidebarOpen"
      @close="isSidebarOpen = false"
      @toggle="isSidebarOpen = !isSidebarOpen"
      class="z-50"
    />

    <main class="flex-1 overflow-y-auto min-w-0 lg:pt-0 pt-16">
      <RouterView />
    </main>
  </div>
</template>
