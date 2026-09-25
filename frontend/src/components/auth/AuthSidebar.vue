<script setup lang="ts">
const s3BaseUrl = import.meta.env.VITE_S3_BUCKET_URL

const backgroundImageUrl = s3BaseUrl
  ? `${s3BaseUrl}/img/auth/auth-bg.webp`
  : '/img/auth/auth-bg.webp'

const logoUrl = s3BaseUrl ? `${s3BaseUrl}/img/logo.svg` : '/img/logo.svg'
</script>

<template>
  <div
    class="hidden lg:flex relative w-1/2 flex-col overflow-hidden p-8 justify-between bg-cover bg-center bg-no-repeat"
    :style="{ backgroundImage: `url('${backgroundImageUrl}')` }"
  >
    <div class="relative z-10 flex flex-col text-white">
      <img :src="logoUrl" alt="LogiFlow Logo" class="w-[180px] h-auto" />

      <h2 class="text-4xl font-bold tracking-tight">Deliver smarter, track faster</h2>
    </div>

    <div class="relative z-10 text-white">
      <p class="text-[42px] font-bold leading-[1.1] max-w-[500px]">
        Real-time logistics management for your entire fleet
      </p>
    </div>
  </div>
</template>
