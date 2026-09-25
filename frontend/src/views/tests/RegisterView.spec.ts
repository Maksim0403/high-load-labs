import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'

vi.mock('@/components/ui/BaseInput.vue', () => ({
  default: {
    name: 'BaseInput',
    template:
      '<input :type="type || \'text\'" :placeholder="placeholder" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'label', 'placeholder', 'type'],
    emits: ['update:modelValue'],
  },
}))

vi.mock('@/components/ui/BaseButton.vue', () => ({
  default: {
    name: 'BaseButton',
    template: '<button :type="type" :disabled="disabled"><slot /></button>',
    props: ['type', 'variant', 'disabled'],
  },
}))

vi.mock('@/components/ui/BaseSelect.vue', () => ({
  default: {
    name: 'BaseSelect',
    template:
      '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><option v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}</option></select>',
    props: ['modelValue', 'label', 'options'],
    emits: ['update:modelValue'],
  },
}))

vi.mock('@/components/icons/IconEye.vue', () => ({
  default: { name: 'IconEye', template: '<span />', props: ['active'] },
}))

vi.mock('@/components/auth/AuthSidebar.vue', () => ({
  default: { name: 'AuthSidebar', template: '<div />' },
}))

// --- Mock apiClient ---
const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(),
}))

vi.mock('@/api/axios.ts', () => ({
  default: { post: mockPost },
}))

// --- Mock router (RegisterView imports router directly, not useRouter) ---
const { mockPush } = vi.hoisted(() => ({
  mockPush: vi.fn(),
}))

vi.mock('@/router', () => ({
  default: { push: mockPush },
}))

import RegisterView from '../RegisterView.vue'

const createWrapper = () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/login', component: { template: '<div />' } },
    ],
  })

  return mount(RegisterView, { global: { plugins: [router] } })
}

const fillForm = async (wrapper: ReturnType<typeof createWrapper>, overrides = {}) => {
  const defaults = {
    fullName: 'John Doe',
    email: 'john@example.com',
    phone: '+380991234567',
    role: 'client',
    password: 'password123',
    confirm: 'password123',
  }
  const values = { ...defaults, ...overrides }

  const inputs = wrapper.findAll('input')
  await inputs.at(0)!.setValue(values.fullName)
  await inputs.at(1)!.setValue(values.email)
  await inputs.at(2)!.setValue(values.phone)
  await wrapper.find('select').setValue(values.role)
  await inputs.at(3)!.setValue(values.password)
  await inputs.at(4)!.setValue(values.confirm)
}

describe('RegisterView', () => {
  beforeEach(() => vi.clearAllMocks())

  // --- Rendering ---
  describe('rendering', () => {
    it('displays the page heading', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h1').text()).toBe('Create an account')
    })

    it('renders 5 input fields', () => {
      const wrapper = createWrapper()
      expect(wrapper.findAll('input').length).toBe(5)
    })

    it('renders the role select', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('select').exists()).toBe(true)
    })

    it('submit button shows "Create Account" by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('button[type="submit"]').text()).toBe('Create Account')
    })

    it('does not show an error message initially', () => {
      const wrapper = createWrapper()
      expect(wrapper.text()).not.toContain('password')
    })

    it('renders a link to /login', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('[to="/login"]').exists()).toBe(false)
    })
  })

  // --- Validation ---
  describe('password validation', () => {
    it('shows error when passwords do not match', async () => {
      const wrapper = createWrapper()
      await fillForm(wrapper, { password: 'abc12345', confirm: 'different' })
      await wrapper.find('form').trigger('submit')

      expect(wrapper.text()).toContain('Passwords does not match')
    })

    it('does not call API when passwords do not match', async () => {
      const wrapper = createWrapper()
      await fillForm(wrapper, { password: 'abc12345', confirm: 'different' })
      await wrapper.find('form').trigger('submit')

      expect(mockPost).not.toHaveBeenCalled()
    })
  })

  describe('successful registration', () => {
    it('sends POST to /auth/register with correct payload', async () => {
      mockPost.mockResolvedValueOnce({ data: {} })
      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockPost).toHaveBeenCalledWith('/auth/register', {
        email: 'john@example.com',
        password: 'password123',
        full_name: 'John Doe',
        phone_number: '+380991234567',
        role: 'client',
      })
    })

    it('redirects to /login after successful registration', async () => {
      mockPost.mockResolvedValueOnce({ data: {} })
      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockPush).toHaveBeenCalledWith('/login')
    })
  })

  // --- Error handling ---
  describe('error handling', () => {
    it('shows detail string error from server', async () => {
      const { default: axios } = await import('axios')
      const axiosError = Object.assign(new axios.AxiosError('Conflict'), {
        response: { data: { detail: 'Email already registered' } },
      })
      mockPost.mockRejectedValueOnce(axiosError)

      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Email already registered')
    })

    it('shows validation error message when detail is an array', async () => {
      const { default: axios } = await import('axios')
      const axiosError = Object.assign(new axios.AxiosError('Validation Error'), {
        response: { data: { detail: [{ msg: 'field required' }] } },
      })
      mockPost.mockRejectedValueOnce(axiosError)

      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Please, fill all the necessary fields correctly.')
    })

    it('shows connection error when no detail in response', async () => {
      const { default: axios } = await import('axios')
      const axiosError = new axios.AxiosError('Network Error')
      mockPost.mockRejectedValueOnce(axiosError)

      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Server connection failed')
    })

    it('shows unknown error message for non-axios errors', async () => {
      mockPost.mockRejectedValueOnce(new Error('Something went wrong'))

      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Unknown error')
    })
  })

  // --- Loading state ---
  describe('loading state', () => {
    it('shows "Creating Account..." while request is pending', async () => {
      mockPost.mockReturnValueOnce(new Promise(() => {}))
      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')

      expect(wrapper.find('button[type="submit"]').text()).toBe('Creating Account...')
    })

    it('disables submit button while loading', async () => {
      mockPost.mockReturnValueOnce(new Promise(() => {}))
      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    })

    it('re-enables submit button after request completes', async () => {
      mockPost.mockResolvedValueOnce({ data: {} })
      const wrapper = createWrapper()
      await fillForm(wrapper)
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
    })
  })
})
