import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use((response) => {
  const instanceId = response.headers['x-instance-id']
  if (instanceId) {
    window.dispatchEvent(
      new CustomEvent('logiflow:instance', { detail: instanceId }),
    )
  }
  return response
})

export default apiClient
