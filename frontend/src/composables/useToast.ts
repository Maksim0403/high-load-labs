import { useToastStore } from '@/stores/toast'

export function useToast() {
  const store = useToastStore()

  const showSuccess = (message: string, duration?: number) => {
    store.addToast(message, 'success', duration)
  }

  const showError = (message: string, duration?: number) => {
    store.addToast(message, 'error', duration)
  }

  const showInfo = (message: string, duration?: number) => {
    store.addToast(message, 'info', duration)
  }

  return {
    showSuccess,
    showError,
    showInfo,
  }
}
