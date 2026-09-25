import axios from 'axios'

export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    if (Array.isArray(detail)) {
      return 'Please fill all required fields correctly.'
    }

    if (typeof detail === 'string') {
      return detail
    }

    switch (status) {
      case 400:
        return 'Invalid request data.'
      case 401:
        return 'Session expired. Please log in again.'
      case 403:
        return 'You do not have permission to do this.'
      case 404:
        return 'Resource not found.'
      case 409:
        return 'Action conflicts with current state.'
      case 422:
        return 'Validation error. Check your input.'
      case 500:
        return 'Server error. Please try again later.'
    }
  }
  return 'Something went wrong. Please try again.'
}
