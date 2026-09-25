<script setup lang="ts">
import { ref } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import IconEye from '@/components/icons/IconEye.vue'
import AuthSidebar from '@/components/auth/AuthSidebar.vue'
import apiClient from '@/api/axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getErrorMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'
import { AUTH } from '@/constants/ui'

const router = useRouter()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const emailError = ref('')
const passwordError = ref('')
const isLoading = ref(false)

const validateEmail = () => {
  emailError.value = ''
  if (!email.value) {
    emailError.value = AUTH.errors.emailRequired
    return false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    emailError.value = AUTH.errors.emailInvalid
    return false
  }
  return true
}

const validatePassword = () => {
  passwordError.value = ''
  if (!password.value) {
    passwordError.value = AUTH.errors.passwordRequired
    return false
  }
  return true
}

const validateForm = () => {
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  return isEmailValid && isPasswordValid
}

const redirectUser = async () => {
  const userRole = authStore.userRole
  if (userRole === 'manager') {
    await router.push('/dashboard')
  } else if (userRole === 'driver') {
    await router.push('/driver/route')
  } else if (userRole === 'client') {
    await router.push('/recipient/billing')
  } else {
    await router.push('/dashboard')
  }
}

const handleLogin = async () => {
  if (!validateForm()) return

  isLoading.value = true

  try {
    const response = await apiClient.post('/auth/login', {
      email: email.value,
      password: password.value,
    })

    authStore.setUser(response.data)
    showSuccess(AUTH.login.success)

    isLoading.value = false

    await redirectUser()
  } catch (error: unknown) {
    isLoading.value = false
    const msg = getErrorMessage(error)
    showError(msg)
    console.error('Login error:', error)
  }
}
</script>

<template>
  <div class="flex min-h-screen font-roboto bg-bg-canvas">
    <AuthSidebar />

    <div class="flex-1 flex flex-col justify-center px-6 sm:px-10">
      <div class="w-full max-w-[480px] mx-auto flex flex-col gap-8 sm:gap-10">
        <h1 class="text-text-primary text-3xl sm:text-[42px] font-bold">{{ AUTH.login.title }}</h1>

        <form class="flex flex-col gap-6" @submit.prevent="handleLogin">
          <BaseInput
            v-model="email"
            :label="AUTH.login.emailLabel"
            :placeholder="AUTH.login.emailPlaceholder"
            :error="emailError"
            @input="emailError = ''"
            @blur="validateEmail"
          />

          <BaseInput
            v-model="password"
            :label="AUTH.login.passwordLabel"
            :type="showPassword ? 'text' : 'password'"
            :placeholder="AUTH.login.passwordPlaceholder"
            :error="passwordError"
            @input="passwordError = ''"
            @blur="validatePassword"
          >
            <template #suffix>
              <button type="button" @click="showPassword = !showPassword">
                <IconEye :active="showPassword" />
              </button>
            </template>
          </BaseInput>

          <BaseButton type="submit" variant="primary" :disabled="isLoading">
            {{ isLoading ? AUTH.login.submitBtnLoading : AUTH.login.submitBtn }}
          </BaseButton>
        </form>

        <div class="h-px bg-border-default w-full"></div>
        <p class="text-sm">
          <span class="text-text-secondary">{{ AUTH.login.noAccount }}</span>
          <RouterLink to="/register" class="ml-1 text-text-link font-bold hover:underline">{{
            AUTH.login.signUp
          }}</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
