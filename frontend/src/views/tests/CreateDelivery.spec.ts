import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'

const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(),
}))

vi.mock('@/api/axios', () => ({
  default: { post: mockPost },
}))

import CreateDelivery from '../CreateDelivery.vue'

const createWrapper = () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/dashboard', component: { template: '<div />' } },
    ],
  })

  return { wrapper: mount(CreateDelivery, { global: { plugins: [router] } }), router }
}

describe('CreateDelivery', () => {
  beforeEach(() => vi.clearAllMocks())

  describe('rendering', () => {
    it('displays the page heading', () => {
      const { wrapper } = createWrapper()
      expect(wrapper.find('h1').text()).toBe('Create New Delivery')
    })

    it('renders the title input field', () => {
      const { wrapper } = createWrapper()
      expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    })

    it('renders the weight input field', () => {
      const { wrapper } = createWrapper()
      expect(wrapper.find('input[type="number"]').exists()).toBe(true)
    })

    it('renders the description textarea', () => {
      const { wrapper } = createWrapper()
      expect(wrapper.find('textarea').exists()).toBe(true)
    })

    it('submit button shows "Create Shipment" by default', () => {
      const { wrapper } = createWrapper()
      expect(wrapper.find('button[type="submit"]').text()).toContain('Create Shipment')
    })

    it('renders the Cancel button', () => {
      const { wrapper } = createWrapper()
      expect(wrapper.find('button[type="button"]').text()).toContain('Cancel')
    })
  })

  describe('successful order creation', () => {
    it('sends POST to /orders/ with form data', async () => {
      mockPost.mockResolvedValueOnce({ data: { id: 1 } })
      const { wrapper } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Electronics to Kyiv') // title
      await inputs.at(1)!.setValue('5.5') // weight

      await wrapper.find('textarea').setValue('Fragile items')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockPost).toHaveBeenCalledWith('/orders/', {
        title: 'Electronics to Kyiv',
        description: 'Fragile items',
        weight: 5.5,
        is_template: false,
      })
    })

    it('redirects to /recipient/orders on success', async () => {
      mockPost.mockResolvedValueOnce({ data: { id: 1 } })
      const { wrapper, router } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Test order')
      await inputs.at(1)!.setValue('1.0')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/recipient/orders')
    })
  })

  describe('error handling', () => {
    it('does not redirect if request fails', async () => {
      mockPost.mockRejectedValueOnce(new Error('Network Error'))
      const { wrapper, router } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Title')
      await inputs.at(1)!.setValue('1.0')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/')
    })

    it('re-enables the submit button after a failed request', async () => {
      mockPost.mockRejectedValueOnce(new Error('Network Error'))
      const { wrapper } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Title')
      await inputs.at(1)!.setValue('1.0')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
    })
  })

  describe('loading state', () => {
    it('shows "Creating..." while request is pending', async () => {
      mockPost.mockReturnValueOnce(new Promise(() => {}))
      const { wrapper } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Title')
      await inputs.at(1)!.setValue('1.0')

      await wrapper.find('form').trigger('submit')

      expect(wrapper.find('button[type="submit"]').text()).toContain('Creating...')
    })

    it('disables the submit button while loading', async () => {
      mockPost.mockReturnValueOnce(new Promise(() => {}))
      const { wrapper } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Title')
      await inputs.at(1)!.setValue('1.0')

      await wrapper.find('form').trigger('submit')

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    })

    it('re-enables the submit button after request completes', async () => {
      mockPost.mockResolvedValueOnce({ data: {} })
      const { wrapper } = createWrapper()

      const inputs = wrapper.findAll('input')
      await inputs.at(0)!.setValue('Title')
      await inputs.at(1)!.setValue('1.0')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
    })
  })
})
