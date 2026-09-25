import type { UserRole } from './user'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  phone_number: string
  role: UserRole
}
