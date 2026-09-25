<script setup lang="ts">
import { ref } from 'vue'
import { Camera, X, Upload } from 'lucide-vue-next'
import { routesApi } from '@/api/routes'

const props = defineProps<{
  routeId: number
}>()

const emit = defineEmits<{
  uploaded: []
  close: []
}>()

const isDragging = ref(false)
const preview = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const error = ref('')

const handleFile = (file: File): void => {
  if (!file.type.startsWith('image/')) {
    error.value = 'Only image file types are allowed'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'File size must be under 10MB'
    return
  }
  error.value = ''
  selectedFile.value = file
  preview.value = URL.createObjectURL(file)
}

const onFileInput = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) handleFile(input.files[0])
}

const onDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files?.[0]) handleFile(e.dataTransfer.files[0])
}

const clearFile = () => {
  preview.value = null
  selectedFile.value = null
  error.value = ''
}

const handleUpload = async () => {
  if (!selectedFile.value) return
  isUploading.value = true
  try {
    await routesApi.uploadRoutePhoto(props.routeId, selectedFile.value)
    emit('uploaded')
    emit('close')
  } catch {
    error.value = 'Upload failed. Please try again.'
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div
      v-if="!preview"
      class="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer"
      :class="
        isDragging
          ? 'border-brand-primary bg-brand-primary/5'
          : 'border-border-default hover:border-brand-primary'
      "
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="onDrop"
      @click="($refs.fileInput as HTMLInputElement).click()"
    >
      <Camera class="w-10 h-10 text-text-placeholder mx-auto mb-3" />
      <p class="text-sm font-bold text-text-primary">Drop photo here or click to upload</p>
      <p class="text-xs text-text-secondary mt-1">PNG, JPG, WEBP up to 10MB</p>
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileInput" />
    </div>

    <div v-else class="relative rounded-xl overflow-hidden border border-border-default">
      <img :src="preview" class="w-full max-h-64 object-cover" alt="img" />
      <button
        v-if="!isUploading"
        @click="clearFile"
        class="absolute top-2 right-2 w-7 h-7 bg-white rounded-full flex items-center justify-center shadow hover:bg-bg-surface"
      >
        <X class="w-4 h-4 text-text-primary" />
      </button>
    </div>

    <p v-if="error" class="text-xs text-red-500 font-medium">{{ error }}</p>

    <div class="flex gap-3">
      <button
        @click="$emit('close')"
        class="flex-1 min-h-[44px] border border-border-default rounded-lg text-sm font-bold hover:bg-bg-surface transition-colors"
      >
        Cancel
      </button>
      <button
        :disabled="!selectedFile || isUploading"
        @click="handleUpload"
        class="flex-1 min-h-[44px] bg-brand-primary text-white rounded-lg text-sm font-bold disabled:opacity-50 flex items-center justify-center gap-2 hover:bg-btn-primary-hover transition-colors"
      >
        <Upload v-if="!isUploading" class="w-4 h-4" />
        <span>{{ isUploading ? 'Uploading...' : 'Upload Photo' }}</span>
      </button>
    </div>
  </div>
</template>
