<script setup>
import { onMounted, onUnmounted, ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import MetricsGrid from '../components/home/MetricsGrid.vue'
import { 
  fetchHomeDeployments, 
  fetchHomeOverview,
  fetchIntersections,
  fetchMapDevices,
  fetchDeviceVideoStream
} from '../services/api'
import SphericalCameraIcon from '../assets/icons/SphericalCamera.svg?url'
import MonitorCameraIcon from '../assets/icons/MonitorCamera.svg?url'
import SignalControllerIcon from '../assets/icons/signal_controller.svg?url'
import TSNSwitchIcon from '../assets/icons/tsn_switch.svg?url'

const router = useRouter()

const metrics = ref({})
const deployments = ref([])
const loading = ref(true)
const errorMessage = ref('')

// 地图相关状态
const mapContainer = ref(null)
const selectedIntersection = ref(null)
const intersections = ref([])
const showCameras = ref(true)
const showSignalControllers = ref(true)
const showSwitches = ref(false)
const currentCameraInfo = ref(null)
const currentVideoStream = ref(null)
const videoDialogVisible = ref(false)
const videoPlayer = ref(null)
// 保存事件监听器引用，以便后续移除
const videoEventHandlers = ref({
  onLoadedMetadata: null,
  onError: null,
  onLoadStart: null,
  onCanPlay: null
})

let map = null
let markers = []
let hls = null

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const [overviewResponse, deploymentsResponse] = await Promise.all([
      fetchHomeOverview(),
      fetchHomeDeployments(),
    ])

    metrics.value = overviewResponse.data
    deployments.value = deploymentsResponse.data.deployments || []
  } catch (error) {
    errorMessage.value = '数据加载出现波动，请稍后重试。'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadData()
  await loadIntersections()
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
  if (hls) {
    hls.destroy()
  }
})

const loadIntersections = async () => {
  try {
    const response = await fetchIntersections({ per_page: 100 })
    intersections.value = response.data.items || []
  } catch (error) {
    console.error('加载路口列表失败:', error)
  }
}

const loadIntersectionData = async (intersectionId) => {
  if (!intersectionId || !map) return

  try {
    const response = await fetchMapDevices({ intersection_id: intersectionId })
    const data = response.data
    const intersection = data.intersection
    
    map.setCenter([intersection.longitude, intersection.latitude])
    map.setZoom(20)
    
    clearMarkers()
    addIntersectionMarker(intersection)
    
    if (showCameras.value && data.cameras) {
      data.cameras.forEach((camera) => {
        addCameraMarker(camera, intersection)
      })
    }
    
    if (showSignalControllers.value && data.signal_controllers) {
      data.signal_controllers.forEach((signal) => {
        addSignalMarker(signal, intersection)
      })
    }
    
    if (showSwitches.value && data.switches) {
      data.switches.forEach((switchDevice) => {
        addSwitchMarker(switchDevice, intersection)
      })
    }
  } catch (error) {
    console.error('加载路口数据失败:', error)
    errorMessage.value = '加载路口数据失败: ' + (error.response?.data?.error || error.message)
  }
}

const initMap = () => {
  createAMap()
}

const createAMap = () => {
  if (typeof window === 'undefined' || !mapContainer.value) return
  
  if (window.AMap) {
    initAMapInstance()
    return
  }
  
  const script = document.createElement('script')
  script.type = 'text/javascript'
  script.src = `https://webapi.amap.com/maps?v=2.0&key=b075228d554cb53a8547f722facd0826&callback=initAMapCallback`
  script.async = true
  script.charset = 'utf-8'
  
  window.initAMapCallback = () => {
    initAMapInstance()
  }
  
  script.onerror = () => {
    console.error('Failed to load AMap')
    errorMessage.value = '高德地图加载失败，请检查网络连接'
  }
  
  document.head.appendChild(script)
}

const initAMapInstance = () => {
  if (!mapContainer.value) return
  
  const AMap = window.AMap
  if (!AMap) {
    console.error('AMap not loaded')
    return
  }
  
  map = new AMap.Map('map-container', {
    zoom: 20,
    center: [112.927176, 27.87076],
    viewMode: '3D',
    mapStyle: 'amap://styles/darkblue',
    zoomEnable: true,
    dragEnable: true
  })
  
  map.on('complete', () => {
    loadAllDevices()
  })
}

const loadAllDevices = async () => {
  if (!map) return
  
  try {
    const response = await fetchMapDevices()
    const data = response.data
    
    if (!data) {
      return
    }
    
    let centerLng = 112.927176
    let centerLat = 27.87076
    
    if (data.devices && Array.isArray(data.devices) && data.devices.length > 0) {
      const devicesWithLocation = data.devices.filter((d) => {
        return d && typeof d.longitude === 'number' && typeof d.latitude === 'number' && 
               !isNaN(d.longitude) && !isNaN(d.latitude)
      })
      
      if (devicesWithLocation.length > 0) {
        const sumLng = devicesWithLocation.reduce((sum, d) => sum + Number(d.longitude), 0)
        const sumLat = devicesWithLocation.reduce((sum, d) => sum + Number(d.latitude), 0)
        centerLng = sumLng / devicesWithLocation.length
        centerLat = sumLat / devicesWithLocation.length
      }
    }
    
    map.setCenter([centerLng, centerLat])
    map.setZoom(20)
    
    if (data.intersections && Array.isArray(data.intersections)) {
      data.intersections.forEach((intersection) => {
        if (intersection && intersection.longitude && intersection.latitude) {
          addIntersectionMarker(intersection)
        }
      })
    }
    
    if (data.devices && Array.isArray(data.devices)) {
      data.devices.forEach((device) => {
        try {
          if (!device || typeof device.longitude !== 'number' || typeof device.latitude !== 'number' ||
              isNaN(device.longitude) || isNaN(device.latitude)) {
            return
          }
          
          const deviceType = device.device_type || device.type || 'camera'
          
          if (deviceType === 'camera' && showCameras.value) {
            addCameraMarker(device, { longitude: device.longitude, latitude: device.latitude })
          } else if ((deviceType === 'traffic_signal_controller' || deviceType === 'signal_controller') && showSignalControllers.value) {
            addSignalMarker(device, { longitude: device.longitude, latitude: device.latitude })
          } else if (deviceType === 'switch' && showSwitches.value) {
            addSwitchMarker(device, { longitude: device.longitude, latitude: device.latitude })
          }
        } catch (deviceError) {
          console.error('添加设备标记失败:', device, deviceError)
        }
      })
    }
  } catch (error) {
    console.error('加载设备数据失败:', error)
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '未知错误'
    errorMessage.value = '加载设备数据失败: ' + errorMsg
  }
}

const addIntersectionMarker = (intersection) => {
  if (!map) return
  
  const AMap = window.AMap
  if (!AMap) return
  
  const icon = new AMap.Icon({
    size: new AMap.Size(32, 32),
    image: createMarkerIcon('#49c5ff', '路', 32),
    imageSize: new AMap.Size(32, 32),
    imageOffset: new AMap.Pixel(0, 0)
  })
  
  const marker = new AMap.Marker({
    position: [intersection.longitude, intersection.latitude],
    icon: icon,
    title: intersection.name,
    offset: new AMap.Pixel(-16, -16)
  })
  
  const infoWindow = new AMap.InfoWindow({
    content: `<div style="padding: 10px; color: #d6ecff;"><b>${intersection.name}</b><br/>${intersection.address || ''}<br/>状态: ${getStatusText(intersection.status)}</div>`,
    offset: new AMap.Pixel(0, -30)
  })
  
  marker.on('click', () => {
    selectedIntersection.value = intersection.id
    loadIntersectionData(intersection.id)
    infoWindow.open(map, marker.getPosition())
  })
  
  map.add(marker)
  markers.push(marker)
}

const getStatusText = (status) => {
  if (!status) return '未知'
  const map = {
    // 路口状态
    'normal': '正常',
    'abnormal': '异常',
    'maintenance': '维护中',
    // 设备状态
    'online': '在线',
    'offline': '离线',
    'fault': '故障',
    '在线': '在线',
    '离线': '离线',
    '故障': '故障'
  }
  return map[status] || status
}

const getStatusClass = (status) => {
  if (!status) return 'unknown'
  if (status === 'online' || status === '在线' || status === 'normal') return 'active'
  if (status === 'offline' || status === '离线' || status === 'abnormal') return 'inactive'
  if (status === 'fault' || status === '故障') return 'fault'
  if (status === 'maintenance') return 'inactive'
  return 'unknown'
}

const addCameraMarker = (camera, intersection) => {
  if (!map) return
  
  const AMap = window.AMap
  if (!AMap) return
  
  const cameraName = camera.name || ''
  const isCheckpoint = cameraName.includes('卡口')
  const isElectronicPolice = cameraName.includes('电警')
  
  const lat = camera.latitude || intersection?.latitude || 27.87076
  const lng = camera.longitude || intersection?.longitude || 112.927176
  
  let icon
  if (isCheckpoint) {
    icon = new AMap.Icon({
      size: new AMap.Size(48, 48),
      image: SphericalCameraIcon,
      imageSize: new AMap.Size(48, 48),
      imageOffset: new AMap.Pixel(0, 0)
    })
  } else {
    icon = new AMap.Icon({
      size: new AMap.Size(48, 48),
      image: MonitorCameraIcon,
      imageSize: new AMap.Size(48, 48),
      imageOffset: new AMap.Pixel(0, 0)
    })
  }
  
  const statusText = camera.status === 'online' ? '在线' : camera.status === 'offline' ? '离线' : camera.status === 'fault' ? '故障' : '未知'
  
  const marker = new AMap.Marker({
    position: [lng, lat],
    icon: icon,
    title: camera.name,
    offset: new AMap.Pixel(-24, -24)
  })
  
  marker.on('click', async () => {
    // 直接打开统一的设备详情和视频对话框
    showCameraInfo(camera)
    await loadCameraVideo(camera)
  })
  
  map.add(marker)
  markers.push(marker)
}

const addSignalMarker = (signal, intersection) => {
  if (!map) return
  
  const AMap = window.AMap
  if (!AMap) return
  
  const lat = signal.latitude || intersection.latitude || 27.871127
  const lng = signal.longitude || intersection.longitude || 112.927831
  
  const icon = new AMap.Icon({
    size: new AMap.Size(32, 32),
    image: SignalControllerIcon,
    imageSize: new AMap.Size(32, 32),
    imageOffset: new AMap.Pixel(0, 0)
  })
  
  const statusText = signal.status === 'online' ? '在线' : signal.status === 'offline' ? '离线' : '未知'
  
  const marker = new AMap.Marker({
    position: [lng, lat],
    icon: icon,
    title: signal.name,
    offset: new AMap.Pixel(-16, -16)
  })
  
  const infoWindow = new AMap.InfoWindow({
    content: `<div style="padding: 10px; color: #d6ecff;"><b>${signal.name}</b><br/>IP: ${signal.ip_address || 'N/A'}<br/>相位: ${signal.phase_count || 0}个<br/>状态: ${statusText}</div>`,
    offset: new AMap.Pixel(0, -30)
  })
  
  marker.on('click', () => {
    infoWindow.open(map, marker.getPosition())
  })
  
  map.add(marker)
  markers.push(marker)
}

const addSwitchMarker = (switchDevice, intersection) => {
  if (!map) return
  
  const AMap = window.AMap
  if (!AMap) return
  
  const lat = switchDevice.latitude || intersection.latitude || 27.871127
  const lng = switchDevice.longitude || intersection.longitude || 112.927831
  
  const icon = new AMap.Icon({
    size: new AMap.Size(32, 32),
    image: TSNSwitchIcon,
    imageSize: new AMap.Size(32, 32),
    imageOffset: new AMap.Pixel(0, 0)
  })
  
  const statusText = switchDevice.status === 'online' ? '在线' : switchDevice.status === 'offline' ? '离线' : '未知'
  
  const marker = new AMap.Marker({
    position: [lng, lat],
    icon: icon,
    title: switchDevice.name,
    offset: new AMap.Pixel(-16, -16)
  })
  
  const infoWindow = new AMap.InfoWindow({
    content: `<div style="padding: 10px; color: #d6ecff;"><b>${switchDevice.name}</b><br/>IP: ${switchDevice.ip_address || 'N/A'}<br/>端口数: ${switchDevice.port_count || 0}<br/>状态: ${statusText}</div>`,
    offset: new AMap.Pixel(0, -30)
  })
  
  marker.on('click', () => {
    infoWindow.open(map, marker.getPosition())
  })
  
  map.add(marker)
  markers.push(marker)
}

const clearMarkers = () => {
  markers.forEach(marker => {
    if (marker && map && map.remove) {
      map.remove(marker)
    }
  })
  markers = []
}

const createMarkerIcon = (color, text, size) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 2}" fill="${color}" stroke="#fff" stroke-width="2"/>
      <text x="${size/2}" y="${size/2 + size/8}" text-anchor="middle" fill="white" font-size="${size/2.5}" font-weight="bold">${text}</text>
    </svg>
  `
  return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)))
}

const toggleLayer = (type) => {
  if (type === 'cameras') {
    showCameras.value = !showCameras.value
  } else if (type === 'signals') {
    showSignalControllers.value = !showSignalControllers.value
  } else if (type === 'switches') {
    showSwitches.value = !showSwitches.value
  }
  
  if (selectedIntersection.value) {
    loadIntersectionData(selectedIntersection.value)
  } else {
    clearMarkers()
    loadAllDevices()
  }
}

const showCameraInfo = (camera) => {
  currentCameraInfo.value = camera
}

const loadCameraVideo = async (camera) => {
  try {
    errorMessage.value = ''
    const deviceId = typeof camera.id === 'string' ? parseInt(camera.id, 10) : camera.id
    console.log('加载视频流，设备ID:', deviceId)
    
    const response = await fetchDeviceVideoStream(deviceId)
    currentVideoStream.value = response.data
    console.log('获取到视频流信息:', currentVideoStream.value)
    
    // 先打开对话框，让视频元素渲染到 DOM 中
    videoDialogVisible.value = true
    
    // 等待 DOM 更新，确保视频元素已经渲染
    await nextTick()
    // 再等待一帧，确保 ref 已经绑定
    await new Promise(resolve => setTimeout(resolve, 100))
    
    if (!videoPlayer.value) {
      console.error('视频播放器元素不存在，尝试再次等待...')
      // 再等待一下
      await new Promise(resolve => setTimeout(resolve, 200))
      if (!videoPlayer.value) {
        console.error('视频播放器元素仍然不存在')
        errorMessage.value = '视频播放器未初始化'
        return
      }
    }
    
    if (!currentVideoStream.value) {
      console.error('视频流信息不存在')
      errorMessage.value = '未获取到视频流信息'
      return
    }
    
    const streamId = typeof currentVideoStream.value.id === 'string' ? parseInt(currentVideoStream.value.id, 10) : currentVideoStream.value.id
    // 使用完整的 API URL
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10060'
    const videoUrl = `${apiBaseUrl}/video-streams/stream/${streamId}`
    
    console.log('设置视频URL:', videoUrl)
    console.log('视频播放器状态:', {
      readyState: videoPlayer.value.readyState,
      networkState: videoPlayer.value.networkState,
      paused: videoPlayer.value.paused
    })
    
    if (hls) {
      hls.destroy()
      hls = null
    }
    
    // 清除之前的错误状态
    errorMessage.value = ''
    
    // 移除之前的事件监听器（如果存在）
    const oldSrc = videoPlayer.value.src
    if (oldSrc) {
      videoPlayer.value.src = ''
      videoPlayer.value.load()
    }
    
    // 设置新的视频源
    videoPlayer.value.src = videoUrl
    console.log('视频源已设置，开始加载...')
    
    // 移除旧的事件监听器（如果存在）
    if (videoEventHandlers.value.onLoadedMetadata) {
      videoPlayer.value.removeEventListener('loadedmetadata', videoEventHandlers.value.onLoadedMetadata)
    }
    if (videoEventHandlers.value.onError) {
      videoPlayer.value.removeEventListener('error', videoEventHandlers.value.onError)
    }
    if (videoEventHandlers.value.onLoadStart) {
      videoPlayer.value.removeEventListener('loadstart', videoEventHandlers.value.onLoadStart)
    }
    if (videoEventHandlers.value.onCanPlay) {
      videoPlayer.value.removeEventListener('canplay', videoEventHandlers.value.onCanPlay)
    }
    
    // 创建新的事件监听器
    videoEventHandlers.value.onLoadedMetadata = () => {
      console.log('视频元数据加载完成')
      videoPlayer.value?.play().catch((e) => {
        console.error('自动播放失败:', e)
      })
    }
    
    videoEventHandlers.value.onError = (e) => {
      console.error('视频加载错误:', e)
      const error = videoPlayer.value?.error
      if (error) {
        console.error('视频错误详情:', {
          code: error.code,
          message: error.message,
          networkState: videoPlayer.value.networkState,
          readyState: videoPlayer.value.readyState
        })
        errorMessage.value = `视频播放失败: ${error.message || '不支持的视频格式'} (错误代码: ${error.code})`
      }
    }
    
    videoEventHandlers.value.onLoadStart = () => {
      console.log('视频开始加载')
    }
    
    videoEventHandlers.value.onCanPlay = () => {
      console.log('视频可以播放')
    }
    
    // 添加新的事件监听器
    videoPlayer.value.addEventListener('loadedmetadata', videoEventHandlers.value.onLoadedMetadata)
    videoPlayer.value.addEventListener('error', videoEventHandlers.value.onError)
    videoPlayer.value.addEventListener('loadstart', videoEventHandlers.value.onLoadStart)
    videoPlayer.value.addEventListener('canplay', videoEventHandlers.value.onCanPlay)
    
    // 触发加载
    videoPlayer.value.load()
    console.log('已调用 videoPlayer.load()')
    
    // 尝试播放
    videoPlayer.value.play().catch((e) => {
      console.log('自动播放被阻止:', e)
    })
  } catch (error) {
    console.error('加载视频流异常:', error)
    if (error.response?.status === 404) {
      errorMessage.value = '该设备暂无视频流'
      currentVideoStream.value = null
    } else {
      errorMessage.value = '加载视频流失败: ' + (error.response?.data?.error || error.message)
      currentVideoStream.value = null
    }
  }
}

const handleCloseVideo = () => {
  console.log('关闭视频对话框')
  
  // 先移除事件监听器，避免在清理过程中触发错误
  if (videoPlayer.value) {
    // 移除所有事件监听器
    if (videoEventHandlers.value.onLoadedMetadata) {
      videoPlayer.value.removeEventListener('loadedmetadata', videoEventHandlers.value.onLoadedMetadata)
    }
    if (videoEventHandlers.value.onError) {
      videoPlayer.value.removeEventListener('error', videoEventHandlers.value.onError)
    }
    if (videoEventHandlers.value.onLoadStart) {
      videoPlayer.value.removeEventListener('loadstart', videoEventHandlers.value.onLoadStart)
    }
    if (videoEventHandlers.value.onCanPlay) {
      videoPlayer.value.removeEventListener('canplay', videoEventHandlers.value.onCanPlay)
    }
    
    // 停止播放并清理
    try {
      videoPlayer.value.pause()
      videoPlayer.value.src = ''
      videoPlayer.value.load() // 重置视频元素
    } catch (e) {
      console.log('清理视频时出错（可忽略）:', e)
    }
  }
  
  if (hls) {
    try {
      hls.destroy()
    } catch (e) {
      console.log('清理 HLS 时出错（可忽略）:', e)
    }
    hls = null
  }
  
  // 清除错误消息
  errorMessage.value = ''
  
  // 关闭对话框
  videoDialogVisible.value = false
  
  // 清理数据
  currentVideoStream.value = null
  currentCameraInfo.value = null
  
  // 重置事件处理器引用
  videoEventHandlers.value = {
    onLoadedMetadata: null,
    onError: null,
    onLoadStart: null,
    onCanPlay: null
  }
}

watch(videoDialogVisible, (visible) => {
  if (!visible) {
    // 对话框关闭时的清理工作已经在 handleCloseVideo 中完成
    // 这里只做额外的清理（如果需要）
    console.log('对话框已关闭')
  }
})

const handleVideoError = (e) => {
  // 如果对话框已关闭，忽略错误（可能是清理过程中的错误）
  if (!videoDialogVisible.value) {
    console.log('对话框已关闭，忽略视频错误')
    return
  }
  
  // 如果视频元素不存在，忽略错误
  if (!videoPlayer.value) {
    console.log('视频元素不存在，忽略错误')
    return
  }
  
  console.error('视频播放错误:', e)
  const error = videoPlayer.value?.error
  if (error) {
    let errorMsg = '视频播放失败'
    switch (error.code) {
      case 1:
        errorMsg = '视频加载被中止'
        break
      case 2:
        errorMsg = '网络错误，无法加载视频'
        break
      case 3:
        errorMsg = '视频解码失败，可能是不支持的格式'
        break
      case 4:
        errorMsg = '不支持的视频格式'
        break
    }
    errorMessage.value = errorMsg
  }
}

const handleVideoLoadStart = () => {
  console.log('视频开始加载')
}

const handleVideoLoadedData = () => {
  console.log('视频数据加载完成')
  if (videoPlayer.value) {
    videoPlayer.value.play().catch((e) => {
      console.log('自动播放被阻止:', e)
    })
  }
}
</script>

<template>
  <div class="home-view">
   

   

    <!-- 地图可视化区域 -->
    <section class="map-section">
      <header class="map-header">
        <div>
          <h2>路口地图可视化</h2>
          <p>实时查看路口设备分布与视频监控</p>
        </div>
        <div class="map-controls">
          <select 
            v-model="selectedIntersection" 
            @change="loadIntersectionData(selectedIntersection)"
            class="intersection-select"
          >
            <option :value="null">选择路口</option>
            <option 
              v-for="intersection in intersections" 
              :key="intersection.id" 
              :value="intersection.id"
            >
              {{ intersection.name }}
            </option>
          </select>
          <div class="layer-controls">
            <button 
              :class="['layer-btn', { active: showCameras }]"
              @click="toggleLayer('cameras')"
            >
              摄像头
            </button>
            <button 
              :class="['layer-btn', { active: showSignalControllers }]"
              @click="toggleLayer('signals')"
            >
              信号机
            </button>
            <button 
              :class="['layer-btn', { active: showSwitches }]"
              @click="toggleLayer('switches')"
            >
              交换机
            </button>
          </div>
        </div>
      </header>
      <div id="map-container" ref="mapContainer" class="map-view"></div>
      <div class="map-legend">
        <div class="legend-item">
          <span class="legend-icon" style="background: #49c5ff;"></span>
          <span>路口</span>
        </div>
        <div class="legend-item">
          <span class="legend-icon" style="background: #67C23A;"></span>
          <span>卡口摄像头</span>
        </div>
        <div class="legend-item">
          <span class="legend-icon" style="background: #E6A23C;"></span>
          <span>监控摄像头</span>
        </div>
        <div class="legend-item">
          <span class="legend-icon" style="background: #ff6b6b;"></span>
          <span>信号机</span>
        </div>
        <div class="legend-item">
          <span class="legend-icon" style="background: #909399;"></span>
          <span>交换机</span>
        </div>
      </div>
    </section>

    <!-- 设备详情和视频播放对话框 -->
    <div v-if="videoDialogVisible" class="video-dialog-overlay" @click="handleCloseVideo">
      <div class="video-dialog" @click.stop>
        <div class="video-dialog-header">
          <h3>{{ currentCameraInfo ? currentCameraInfo.name : '设备详情' }}</h3>
          <button class="close-btn" @click="handleCloseVideo">×</button>
        </div>
        <div class="video-dialog-body">
          <!-- 设备详情信息 -->
          <div v-if="currentCameraInfo" class="device-info">
            <h4 class="section-title">设备信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">设备ID：</span>
                <span class="info-value">{{ currentCameraInfo.id || currentCameraInfo.code || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">设备名称：</span>
                <span class="info-value">{{ currentCameraInfo.name || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">设备类型：</span>
                <span class="info-value">{{ currentCameraInfo.type || currentCameraInfo.device_type || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">IP地址：</span>
                <span class="info-value">{{ currentCameraInfo.ip_address || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">设备状态：</span>
                <span :class="['status-badge', getStatusClass(currentCameraInfo.status)]">
                  {{ getStatusText(currentCameraInfo.status) }}
                </span>
              </div>
              <div v-if="currentCameraInfo.longitude && currentCameraInfo.latitude" class="info-item">
                <span class="info-label">坐标：</span>
                <span class="info-value">{{ currentCameraInfo.longitude.toFixed(6) }}, {{ currentCameraInfo.latitude.toFixed(6) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 视频流信息 -->
          <div v-if="currentVideoStream" class="video-info">
            <h4 class="section-title">视频流信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">流名称：</span>
                <span class="info-value">{{ currentVideoStream.stream_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">流类型：</span>
                <span class="info-value">{{ currentVideoStream.stream_type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">流状态：</span>
                <span :class="['status-badge', currentVideoStream.status === 'active' ? 'active' : 'inactive']">
                  {{ currentVideoStream.status === 'active' ? '活跃' : '未激活' }}
                </span>
              </div>
            </div>
          </div>
          <div v-else-if="currentCameraInfo" class="no-video">
            <p>该设备暂无视频流</p>
          </div>
          
          <!-- 视频播放器 -->
          <div v-if="currentVideoStream" class="video-container">
            <video
              ref="videoPlayer"
              controls
              autoplay
              muted
              playsinline
              webkit-playsinline
              x5-playsinline
              class="video-player"
              @error="handleVideoError"
              @loadstart="handleVideoLoadStart"
              @loadeddata="handleVideoLoadedData"
            >
              您的浏览器不支持视频播放
            </video>
          </div>
        </div>
      </div>
    </div>
    <MetricsGrid :metrics="metrics" />
    <section v-if="loading && !map" class="loading">数据加载中...</section>
    <section v-if="errorMessage" class="error">{{ errorMessage }}</section>
  </div>
</template>

<style scoped>
.home-view {
  padding: 32px 64px 64px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(5, 26, 43, 0.95), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 48px;
  padding: 42px 48px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.08);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
}

.hero-content h1 {
  font-size: 36px;
  margin-bottom: 18px;
  letter-spacing: 1.6px;
}

.hero-content p {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(214, 232, 255, 0.78);
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-actions .primary,
.hero-actions .secondary {
  padding: 12px 28px;
  border-radius: 999px;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hero-actions .primary {
  border: none;
  color: #0b2338;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  box-shadow: 0 16px 32px rgba(73, 197, 255, 0.25);
}

.hero-actions .primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 38px rgba(73, 197, 255, 0.35);
}

.hero-actions .secondary {
  background: transparent;
  color: #80d6ff;
  border: 1px solid rgba(128, 214, 255, 0.36);
}

.hero-actions .secondary:hover {
  background: rgba(128, 214, 255, 0.18);
}

.hero-visual {
  position: relative;
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-visual .grid {
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  border: 1px solid rgba(128, 214, 255, 0.18);
  background-image: radial-gradient(circle, rgba(128, 214, 255, 0.15) 1px, transparent 1px);
  background-size: 12px 12px;
}

.hero-visual .orb {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(73, 197, 255, 0.65), rgba(11, 38, 66, 0));
  filter: blur(2px);
  animation: orbit 12s linear infinite;
}

.hero-visual .pulse {
  position: relative;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(41, 131, 251, 0.8), rgba(6, 25, 44, 0.1));
  box-shadow: 0 0 30px rgba(41, 131, 251, 0.6);
  animation: pulse 3.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}

@keyframes orbit {
  0% {
    transform: rotate(0deg) translateX(40px) rotate(0deg);
  }
  100% {
    transform: rotate(360deg) translateX(40px) rotate(-360deg);
  }
}

.loading,
.error {
  padding: 18px 24px;
  border-radius: 12px;
  background: rgba(7, 27, 44, 0.8);
  border: 1px solid rgba(88, 178, 255, 0.12);
  font-size: 15px;
  letter-spacing: 0.8px;
}

.error {
  color: #ff9a9e;
}

/* 地图可视化区域样式 */
.map-section {
  position: relative;
  border-radius: 20px;
  padding: 0;
  background: radial-gradient(circle at top, rgba(16, 55, 92, 0.9), rgba(7, 27, 44, 0.95));
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 26px 48px rgba(0, 0, 0, 0.35);
  color: #d6ecff;
  overflow: hidden;
  min-height: 700px;
}

.map-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px;
  background: linear-gradient(to bottom, rgba(16, 55, 92, 0.95), rgba(16, 55, 92, 0.7), transparent);
  z-index: 100;
  pointer-events: none;
}

.map-header > div:first-child {
  pointer-events: auto;
}

.map-header h2 {
  font-size: 22px;
  letter-spacing: 1px;
  margin-bottom: 6px;
  color: #d6ecff;
}

.map-header p {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
  color: rgba(214, 232, 255, 0.78);
}

.map-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  pointer-events: auto;
}

.intersection-select {
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(7, 27, 44, 0.9);
  border: 1px solid rgba(88, 178, 255, 0.3);
  color: #d6ecff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.intersection-select:hover {
  border-color: rgba(88, 178, 255, 0.5);
  background: rgba(7, 27, 44, 1);
}

.intersection-select:focus {
  outline: none;
  border-color: #49c5ff;
  box-shadow: 0 0 0 2px rgba(73, 197, 255, 0.2);
}

.layer-controls {
  display: flex;
  gap: 8px;
}

.layer-btn {
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(7, 27, 44, 0.6);
  border: 1px solid rgba(88, 178, 255, 0.2);
  color: rgba(214, 232, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.layer-btn:hover {
  background: rgba(7, 27, 44, 0.8);
  border-color: rgba(88, 178, 255, 0.4);
  color: #d6ecff;
}

.layer-btn.active {
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  border-color: #49c5ff;
  color: #0b2338;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(73, 197, 255, 0.3);
}

.map-view {
  width: 100%;
  height: 700px;
  border-radius: 0 0 20px 20px;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  left: 28px;
  display: flex;
  gap: 20px;
  padding: 12px 20px;
  background: rgba(7, 27, 44, 0.85);
  border: 1px solid rgba(88, 178, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(214, 232, 255, 0.85);
}

.legend-icon {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* 视频对话框样式 */
.video-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.video-dialog {
  width: 90%;
  max-width: 900px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.95), rgba(6, 25, 44, 0.98));
  border: 1px solid rgba(88, 178, 255, 0.2);
  border-radius: 20px;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.video-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
  background: rgba(7, 27, 44, 0.6);
}

.video-dialog-header h3 {
  margin: 0;
  font-size: 18px;
  color: #d6ecff;
  letter-spacing: 0.5px;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #d6ecff;
  border-radius: 50%;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.video-dialog-body {
  padding: 24px 28px;
}

.device-info,
.video-info {
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(7, 27, 44, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #d6ecff;
  letter-spacing: 0.5px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(214, 232, 255, 0.9);
}

.info-label {
  font-weight: 600;
  color: rgba(214, 232, 255, 0.7);
  min-width: 80px;
}

.info-value {
  color: rgba(214, 232, 255, 0.95);
  word-break: break-word;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: rgba(67, 194, 58, 0.2);
  color: #67c23a;
  border: 1px solid rgba(67, 194, 58, 0.4);
}

.status-badge.inactive {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
  border: 1px solid rgba(144, 147, 153, 0.4);
}

.no-video {
  text-align: center;
  padding: 40px;
  color: rgba(214, 232, 255, 0.6);
}

.video-container {
  width: 100%;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  max-height: 500px;
  display: block;
}
</style>