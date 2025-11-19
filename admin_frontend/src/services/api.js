import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:10060',
  timeout: 10000,
})

export const fetchHomeOverview = () => apiClient.get('/api/home/overview')

export const fetchHomeDeployments = () => apiClient.get('/api/home/deployments')

export const fetchDevices = (params = {}) => apiClient.get('/api/devices', { params })
export const fetchDevice = (deviceId) => apiClient.get(`/api/devices/${deviceId}`)
export const createDevice = (data) => apiClient.post('/api/devices', data)
export const updateDevice = (deviceId, data) => apiClient.put(`/api/devices/${deviceId}`, data)

// 设备类型管理 API
export const fetchDeviceTypes = () => apiClient.get('/api/device-types')
export const createDeviceType = (data) => apiClient.post('/api/device-types', data)
export const updateDeviceType = (id, data) => apiClient.put(`/api/device-types/${id}`, data)
export const deleteDeviceType = (id) => apiClient.delete(`/api/device-types/${id}`)

export const fetchChinaGeoJson = () => apiClient.get('/api/map/china-geojson')

export const login = (credentials) => apiClient.post('/api/auth/login', credentials)

export const register = (userData) => apiClient.post('/api/auth/register', userData)

export const fetchUserProfile = () => apiClient.get('/api/auth/profile')

export const updateUserProfile = (userData) => apiClient.put('/api/auth/profile', userData)

// 应用管理 API
export const fetchApplications = () => apiClient.get('/api/applications')

// 标签类型管理 API
export const fetchLabelTypes = (params = {}) => apiClient.get('/api/laptop-label-types', { params })
export const createLabelType = (data) => apiClient.post('/api/laptop-label-types', data)
export const updateLabelType = (id, data) => apiClient.put(`/api/laptop-label-types/${id}`, data)
export const deleteLabelType = (id) => apiClient.delete(`/api/laptop-label-types/${id}`)

// 网络拓扑管理 API
export const fetchApplicationTopology = (applicationId) => apiClient.get(`/api/applications/${applicationId}/topology`)
export const createTopologyConnection = (applicationId, data) => apiClient.post(`/api/applications/${applicationId}/topology`, data)
export const updateTopologyConnection = (topologyId, data) => apiClient.put(`/api/topology/${topologyId}`, data)
export const deleteTopologyConnection = (topologyId) => apiClient.delete(`/api/topology/${topologyId}`)

// 添加 token 到请求头
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default apiClient

