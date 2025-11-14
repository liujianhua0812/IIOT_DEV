import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 10000,
})

export const fetchHomeOverview = () => apiClient.get('/api/home/overview')

export const fetchHomeDeployments = () => apiClient.get('/api/home/deployments')

export default apiClient

