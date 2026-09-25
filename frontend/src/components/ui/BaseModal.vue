<script setup lang="ts">
import { X } from 'lucide-vue-next'
import BaseButton from './BaseButton.vue'

defineProps<{
  show: boolean
  title: string
  message?: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'primary'
}>()

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="emit('cancel')"
      >
        <div
          class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200"
        >
          <div class="flex items-center justify-between px-6 py-4 border-b border-border-default">
            <h3 class="text-lg font-bold text-text-primary">{{ title }}</h3>
            <button
              @click="emit('cancel')"
              class="p-1 rounded-full hover:bg-bg-surface transition-colors"
            >
              <X class="w-5 h-5 text-text-secondary" />
            </button>
          </div>

          <div class="px-6 py-6 max-h-[70vh] overflow-y-auto">
            <slot>
              <p class="text-text-secondary leading-relaxed">
                {{ message }}
              </p>
            </slot>
          </div>

          <div
            v-if="$slots.footer || confirmText || cancelText"
            class="px-6 py-4 bg-bg-surface/50 border-t border-border-default flex gap-3 justify-end"
          >
            <slot name="footer">
              <BaseButton variant="secondary" @click="emit('cancel')" class="px-6">
                {{ cancelText || 'Cancel' }}
              </BaseButton>
              <BaseButton
                v-if="confirmText"
                :variant="variant === 'danger' ? 'primary' : 'primary'"
                @click="emit('confirm')"
                class="px-6"
                :class="{ 'bg-red-500 hover:bg-red-600 border-red-500': variant === 'danger' }"
              >
                {{ confirmText || 'Confirm' }}
              </BaseButton>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
