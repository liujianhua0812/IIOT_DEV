import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:10060',
  timeout: 10000,
})

export const fetchHomeOverview = () => apiClient.get('/api/home/overview')

export const fetchHomeDeployments = () => apiClient.get('/api/home/deployments')

export const fetchDevices = (params = {}) => apiClient.get('/api/devices', { params })

// 地图和设备相关 API（TellhowTraffic 使用相对路径）
export const fetchIntersections = (params = {}) => apiClient.get('/intersections', { params })
export const fetchMapDevices = (params = {}) => apiClient.get('/map/devices', { params })
export const fetchDeviceVideoStream = (deviceId) => apiClient.get(`/video-streams/device/${deviceId}`)

export const fetchChinaGeoJson = () => apiClient.get('/api/map/china-geojson')

export const login = (credentials) => apiClient.post('/api/auth/login', credentials)

export const register = (userData) => apiClient.post('/api/auth/register', userData)

export const fetchUserProfile = () => apiClient.get('/api/auth/profile')

export const updateUserProfile = (userData) => apiClient.put('/api/auth/profile', userData)

// 添加 token 到请求头
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default apiClient

