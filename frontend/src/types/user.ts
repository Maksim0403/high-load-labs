import type { Vehicle } from './vehicle'

export type UserRole = 'client' | 'manager' | 'driver'

export interface User {
  id: number
  email: string
  role: UserRole
  full_name: string | null
  phone_number: string
  created_at: string
  vehicle?: Vehicle | null
}
