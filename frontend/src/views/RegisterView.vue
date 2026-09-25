<script setup lang="ts">
import { ref } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import IconEye from '@/components/icons/IconEye.vue'
import AuthSidebar from '@/components/auth/AuthSidebar.vue'
import apiClient from '@/api/axios.ts'
import { useRouter } from 'vue-router'
import { getErrorMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'
import { AUTH } from '@/constants/ui'

const router = useRouter()
const { showSuccess, showError } = useToast()

const fullName = ref('')
const email = ref('')
const phoneNumber = ref('')
const role = ref('')
const password = ref('')
const confirmPassword = ref('')

const fullNameError = ref('')
const emailError = ref('')
const phoneNumberError = ref('')
const roleError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const isLoading = ref(false)

const roleOptions = [
  { value: 'client', label: AUTH.roles.client },
  { value: 'manager', label: AUTH.roles.manager },
  { value: 'driver', label: AUTH.roles.driver },
]

const validateFullName = () => {
  fullNameError.value = ''
  if (!fullName.value) {
    fullNameError.value = AUTH.errors.fullNameRequired
    return false
  }
  return true
}

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

const validatePhone = () => {
  phoneNumberError.value = ''
  if (!phoneNumber.value) {
    phoneNumberError.value = AUTH.errors.phoneRequired
    return false
  } else if (!/^\+?380\d{9}$/.test(phoneNumber.value)) {
    phoneNumberError.value = AUTH.errors.phoneInvalid
    return false
  }
  return true
}

const validateRole = () => {
  roleError.value = ''
  if (!role.value) {
    roleError.value = AUTH.errors.roleRequired
    return false
  }
  return true
}

const validatePassword = () => {
  passwordError.value = ''
  if (!password.value) {
    passwordError.value = AUTH.errors.passwordRequired
    return false
  } else if (password.value.length < 8) {
    passwordError.value = AUTH.errors.passwordMinLength
    return false
  }
  return true
}

const validateConfirmPassword = () => {
  confirmPasswordError.value = ''
  if (!confirmPassword.value) {
    confirmPasswordError.value = AUTH.errors.confirmPasswordRequired
    return false
  } else if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = AUTH.errors.passwordsMismatch
    return false
  }
  return true
}

const validateForm = () => {
  const isFullNameValid = validateFullName()
  const isEmailValid = validateEmail()
  const isPhoneValid = validatePhone()
  const isRoleValid = validateRole()
  const isPasswordValid = validatePassword()
  const isConfirmPasswordValid = validateConfirmPassword()

  return (
    isFullNameValid &&
    isEmailValid &&
    isPhoneValid &&
    isRoleValid &&
    isPasswordValid &&
    isConfirmPasswordValid
  )
}

const handleRegister = async () => {
  if (!validateForm()) return

  isLoading.value = true

  try {
    await apiClient.post('/auth/register', {
      email: email.value,
      password: password.value,
      full_name: fullName.value,
      phone_number: phoneNumber.value,
      role: role.value,
    })

    showSuccess(AUTH.register.success)
    router.push('/login')
  } catch (error: unknown) {
    const msg = getErrorMessage(error)
    showError(msg)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen font-roboto bg-bg-canvas">
    <AuthSidebar />

    <div class="flex-1 flex flex-col justify-center px-6 sm:px-10 py-12 md:py-20">
      <div class="w-full max-w-[480px] mx-auto flex flex-col gap-8 sm:gap-10">
        <div>
          <h1 class="text-text-primary text-3xl sm:text-[42px] font-bold">
            {{ AUTH.register.title }}
          </h1>
          <p class="text-text-secondary mt-2">{{ AUTH.register.subtitle }}</p>
        </div>

        <form class="flex flex-col gap-6" @submit.prevent="handleRegister">
          <BaseInput
            v-model="fullName"
            :label="AUTH.register.fullNameLabel"
            :placeholder="AUTH.register.fullNamePlaceholder"
            :error="fullNameError"
            @input="fullNameError = ''"
            @blur="validateFullName"
          />

          <BaseInput
            v-model="email"
            :label="AUTH.register.emailLabel"
            :placeholder="AUTH.register.emailPlaceholder"
            :error="emailError"
            @input="emailError = ''"
            @blur="validateEmail"
          />

          <BaseInput
            v-model="phoneNumber"
            :label="AUTH.register.phoneLabel"
            :placeholder="AUTH.register.phonePlaceholder"
            :error="phoneNumberError"
            @input="phoneNumberError = ''"
            @blur="validatePhone"
          />

          <BaseSelect
            v-model="role"
            :label="AUTH.register.roleLabel"
            :options="roleOptions"
            :error="roleError"
            @update:model-value="roleError = ''"
            @blur="validateRole"
          />

          <BaseInput
            v-model="password"
            :label="AUTH.register.passwordLabel"
            :type="showPassword ? 'text' : 'password'"
            :placeholder="AUTH.register.passwordPlaceholder"
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
          <BaseInput
            v-model="confirmPassword"
            :label="AUTH.register.confirmPasswordLabel"
            :type="showConfirmPassword ? 'text' : 'password'"
            :placeholder="AUTH.register.confirmPasswordPlaceholder"
            :error="confirmPasswordError"
            @input="confirmPasswordError = ''"
            @blur="validateConfirmPassword"
          >
            <template #suffix>
              <button type="button" @click="showConfirmPassword = !showConfirmPassword">
                <IconEye :active="showConfirmPassword" />
              </button>
            </template>
          </BaseInput>

          <BaseButton type="submit" variant="primary" :disabled="isLoading">
            {{ isLoading ? AUTH.register.submitBtnLoading : AUTH.register.submitBtn }}
          </BaseButton>
        </form>

        <div class="h-px bg-border-default w-full"></div>

        <p class="text-sm">
          <span class="text-text-secondary">{{ AUTH.register.alreadyHaveAccount }}</span>
          <RouterLink to="/login" class="ml-1 text-text-link font-bold hover:underline">{{
            AUTH.register.logIn
          }}</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
