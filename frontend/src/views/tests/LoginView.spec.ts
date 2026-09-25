import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import LoginView from '../LoginView.vue'

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

vi.mock('@/components/ui/BaseCheckbox.vue', () => ({
  default: {
    name: 'BaseCheckbox',
    template:
      '<input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />',
    props: ['modelValue', 'label'],
    emits: ['update:modelValue'],
  },
}))

vi.mock('@/components/icons/IconEye.vue', () => ({
  default: { name: 'IconEye', template: '<span />', props: ['active'] },
}))

vi.mock('@/components/auth/AuthSidebar.vue', () => ({
  default: { name: 'AuthSidebar', template: '<div />' },
}))

const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(),
}))

vi.mock('@/api/axios.ts', () => ({
  default: { post: mockPost },
}))

const createWrapper = () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/dashboard', component: { template: '<div />' } },
      { path: '/driver/route', component: { template: '<div />' } },
      { path: '/recipient/billing', component: { template: '<div />' } },
      { path: '/register', component: { template: '<div />' } },
    ],
  })

  const pinia = createPinia()
  setActivePinia(pinia)

  return mount(LoginView, {
    global: { plugins: [router, pinia] },
  })
}

describe('LoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('render', () => {
    it('shows header "Log in"', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('h1').text()).toBe('Log in')
    })

    it('shows email and password fields', () => {
      const wrapper = createWrapper()
      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThanOrEqual(2)
    })

    it('shows "Log In" button', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('button[type="submit"]').text()).toBe('Log In')
    })

    it('doesn`t show error message at the start', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('[data-testid="error-message"]').exists()).toBe(false)
    })

    it('contains reference for /register', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('a[href="/register"], [to="/register"]').exists()).toBe(true)
    })
  })

  describe('successfull login', () => {
    it('redirects manager on /dashboard', async () => {
      mockPost.mockResolvedValueOnce({ data: { role: 'manager' } })
      const wrapper = createWrapper()
      const router = wrapper.vm.$router

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('admin@test.com')
      await inputs.at(1)!.setValue('password123')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/dashboard')
    })

    it('redirects driver on /driver/route', async () => {
      mockPost.mockResolvedValueOnce({ data: { role: 'driver' } })
      const wrapper = createWrapper()
      const router = wrapper.vm.$router

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/driver/route')
    })

    it('redirects client on /recipient/billing', async () => {
      mockPost.mockResolvedValueOnce({ data: { role: 'client' } })
      const wrapper = createWrapper()
      const router = wrapper.vm.$router

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/recipient/billing')
    })

    it('unknown role — redirect on /dashboard', async () => {
      mockPost.mockResolvedValueOnce({ data: { role: 'superadmin' } })
      const wrapper = createWrapper()
      const router = wrapper.vm.$router

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/dashboard')
    })
  })

  describe('error handling', () => {
    it('shows detail error from the server', async () => {
      const { default: axios } = await import('axios')
      const axiosError = Object.assign(new axios.AxiosError('Bad credentials'), {
        response: { data: { detail: 'Invalid email or password' } },
      })
      mockPost.mockRejectedValueOnce(axiosError)

      const wrapper = createWrapper()
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Invalid email or password')
    })

    it('shows general error if detail is absent', async () => {
      const { default: axios } = await import('axios')
      const axiosError = new axios.AxiosError('Network Error')
      mockPost.mockRejectedValueOnce(axiosError)

      const wrapper = createWrapper()
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Server connection error')
    })
  })

  describe('loading state', () => {
    it('button shows "Logging in..." during request', async () => {
      mockPost.mockReturnValueOnce(new Promise(() => {}))

      const wrapper = createWrapper()
      await wrapper.find('form').trigger('submit')

      expect(wrapper.find('button[type="submit"]').text()).toBe('Logging in...')
    })

    it('кнопка задізейблена під час завантаження', async () => {
      mockPost.mockReturnValueOnce(new Promise(() => {}))

      const wrapper = createWrapper()
      await wrapper.find('form').trigger('submit')

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    })

    it('button becomes active after finishing request', async () => {
      mockPost.mockResolvedValueOnce({ data: { role: 'manager' } })

      const wrapper = createWrapper()
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
    })
  })

  describe('API call', () => {
    it('sends email and password on /auth/login', async () => {
      mockPost.mockResolvedValueOnce({ data: { role: 'manager' } })
      const wrapper = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('test@example.com')
      await inputs.at(1)!.setValue('secret')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockPost).toHaveBeenCalledWith('/auth/login', {
        email: 'test@example.com',
        password: 'secret',
      })
    })
  })
})
