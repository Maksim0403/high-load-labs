import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Vehicle } from '@/types'

interface User {
  id: number
  email: string
  full_name: string
  role: 'client' | 'manager' | 'driver'
  phone_number: string
  vehicle?: Vehicle
}

export const useAuthStore = defineStore('auth', () => {
  const getInitialUser = (): User | null => {
    try {
      const saved = localStorage.getItem('user')
      return saved ? JSON.parse(saved) : null
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e)
      localStorage.removeItem('user')
      return null
    }
  }

  const user = ref<User | null>(getInitialUser())

  const getInitialTripStats = () => {
    const saved = localStorage.getItem('last_trip_stats')
    return saved ? JSON.parse(saved) : null
  }
  const lastTripStats = ref<{ distance: number; fuel: number; cost: number } | null>(
    getInitialTripStats(),
  )

  const getInitialHistory = () => {
    const saved = localStorage.getItem('trip_history')
    return saved ? JSON.parse(saved) : []
  }
  const tripHistory =
    ref<{ date: string; distance: number; fuel: number; cost: number; routeId: number }[]>(
      getInitialHistory(),
    )

  const isAuthenticated = computed(() => !!user.value)
  const userRole = computed(() => user.value?.role)

  const isClient = computed(() => user.value?.role === 'client')
  const isManager = computed(() => user.value?.role === 'manager')
  const isDriver = computed(() => user.value?.role === 'driver')

  function setLastTripStats(stats: { distance: number; fuel: number; cost: number }) {
    lastTripStats.value = stats
    localStorage.setItem('last_trip_stats', JSON.stringify(stats))
  }

  function addTripToHistory(trip: {
    distance: number
    fuel: number
    cost: number
    routeId: number
  }) {
    const newTrip = { ...trip, date: new Date().toISOString() }
    tripHistory.value = [newTrip, ...tripHistory.value].slice(0, 50) // Keep last 50
    localStorage.setItem('trip_history', JSON.stringify(tripHistory.value))
  }

  function setUser(userData: User | null) {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  function logout() {
    setUser(null)
  }

  return {
    user,
    isAuthenticated,
    userRole,
    isClient,
    isManager,
    isDriver,
    lastTripStats,
    tripHistory,
    setLastTripStats,
    addTripToHistory,
    setUser,
    logout,
  }
})
