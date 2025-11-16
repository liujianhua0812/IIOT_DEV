<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import apiClient from '@/services/api'

// 运行状态
const runStatus = ref('RUN') // RUN, IDLE, STOP
const currentTime = ref(new Date())
const productionLine = ref('柔性贴标产线-01')

// 更新时间的定时器
let timeInterval = null
onMounted(() => {
  timeInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
  // 加载设备数据
  loadDevices()
})
onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

// 格式化时间
const formattedTime = computed(() => {
  return currentTime.value.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

// 状态颜色
const statusColor = computed(() => {
  switch (runStatus.value) {
    case 'RUN': return '#67c23a'
    case 'IDLE': return '#e6a23c'
    case 'STOP': return '#f56c6c'
    default: return '#909399'
  }
})

// 流程步骤（直线运动：读码 → 贴标 → 质检）
const processSteps = ref([
  { id: 'read', name: '读码', active: true },
  { id: 'label', name: '贴标', active: false },
  { id: 'qc', name: '质检', active: false }
])

// 设备数据加载状态
const devicesLoaded = ref(false)

// 显示/隐藏设备和网络拓扑
const showDevicesAndTopology = ref(false)

// 统计数据
const stats = ref({
  cycleTime: 12.5, // 秒
  passed: 1250,
  failed: 23,
  trend: [120, 125, 118, 130, 128, 135, 132] // 最近7个节拍的趋势
})

// 设备数据（从 API 加载）
const devices = ref({
  read: [],
  label: [],
  pick: [],
  qc: [],
  network: []
})

// 设备连接信息（从 API 加载）
const connections = ref([])

// 确保设备数据始终有默认值
const getDevices = () => {
  return devices.value || {
    read: [],
    label: [],
    pick: [],
    qc: [],
    network: []
  }
}

// 加载设备数据
const loadDevices = async () => {
  try {
    const response = await apiClient.get('/api/lenovofms/devices')
    if (response.data && response.data.devices) {
      // 确保所有工位都有数组
      const loadedDevices = {
        read: response.data.devices.read || [],
        label: response.data.devices.label || [],
        pick: response.data.devices.pick || [],
        qc: response.data.devices.qc || [],
        network: response.data.devices.network || []
      }
      
      // 直接赋值给 ref，Vue 会自动处理响应式更新
      devices.value = loadedDevices
      
      // 加载连接信息
      if (response.data.connections) {
        connections.value = response.data.connections || []
      }
      
      devicesLoaded.value = true
    } else {
      devicesLoaded.value = false
    }
  } catch (error) {
    console.error('加载设备数据失败:', error)
    // 如果 API 失败，使用备份数据
    if (devices_backup) {
      devices.value = {
        read: devices_backup.read || [],
        label: devices_backup.label || [],
        pick: devices_backup.pick || [],
        qc: devices_backup.qc || [],
        network: devices_backup.network || []
      }
      devicesLoaded.value = true
    } else {
      devices.value = {
        read: [],
        label: [],
        pick: [],
        qc: [],
        network: []
      }
      devicesLoaded.value = false
    }
  }
}

// 切换设备和网络拓扑显示
const toggleDevicesAndTopology = () => {
  if (devicesLoaded.value) {
    showDevicesAndTopology.value = !showDevicesAndTopology.value
  }
}



// 根据设备 code 查找设备及其工位
const findDeviceByCode = (deviceCode) => {
  if (!deviceCode) return { device: null, station: null }
  
  const stations = ['read', 'label', 'pick', 'qc', 'network']
  for (const station of stations) {
    const device = (devices.value[station] || []).find(d => d.id === deviceCode)
    if (device) {
      return { device, station }
    }
  }
  return { device: null, station: null }
}

// 获取连接线的起点和终点坐标
const getConnectionStartX = (conn) => {
  const { device, station } = findDeviceByCode(conn.source)
  return getDeviceSvgPosition(device, station)?.x || 0
}

const getConnectionStartY = (conn) => {
  const { device, station } = findDeviceByCode(conn.source)
  return getDeviceSvgPosition(device, station)?.y || 0
}

const getConnectionEndX = (conn) => {
  const { device, station } = findDeviceByCode(conn.target)
  return getDeviceSvgPosition(device, station)?.x || 0
}

const getConnectionEndY = (conn) => {
  const { device, station } = findDeviceByCode(conn.target)
  return getDeviceSvgPosition(device, station)?.y || 0
}

// 获取设备在SVG中的坐标（用于绘制连线）
const getDeviceSvgPosition = (device, station) => {
  if (!device) {
    // 静默返回，不输出警告（因为设备可能还未加载）
    return { x: 0, y: 0 }
  }
  if (!device.position) {
    console.warn('getDeviceSvgPosition: 设备位置数据缺失', { device: device.id || device.name, station })
    return { x: 0, y: 0 }
  }
  
  // 调整工位位置，整体向下移动，减少底部空白
  const stationPositions = {
    read: { baseX: 100, baseY: 200, width: 200, height: 100 },
    label: { baseX: 400, baseY: 200, width: 200, height: 100 },
    pick: { baseX: 500, baseY: 330, width: 120, height: 80 },
    qc: { baseX: 700, baseY: 200, width: 200, height: 100 },
    network: { baseX: 400, baseY: 100, width: 200, height: 60 }
  }
  
  const pos = stationPositions[station] || { baseX: 0, baseY: 0, width: 200, height: 100 }
  
  // 设备位置是相对于工位的百分比（允许超出0-100范围）
  // 计算 SVG 绝对坐标
  const svgX = pos.baseX + (device.position.x / 100) * pos.width
  const svgY = pos.baseY + (device.position.y / 100) * pos.height
  
  return {
    x: svgX,
    y: svgY
  }
}

// 获取设备图标的定位样式（用于HTML覆盖层）
const getDeviceIconStyle = (device, station) => {
  if (!device || !device.position) {
    console.warn('getDeviceIconStyle: 设备或位置数据缺失', { device, station })
    return { left: '0%', top: '0%' }
  }
  const svgPos = getDeviceSvgPosition(device, station)
  // SVG viewBox 是 "0 0 1000 500"
  const style = {
    left: `${(svgPos.x / 1000) * 100}%`,
    top: `${(svgPos.y / 500) * 100}%`
  }
  return style
}

// 选中的设备
const selectedDevice = ref(null)
const hoveredDevice = ref(null)

// 拖拽相关状态
const draggedDevice = ref(null)
const dragOffset = ref({ x: 0, y: 0 })

// 开始拖拽设备
const startDrag = (device, event) => {
  draggedDevice.value = device
  const rect = event.currentTarget.getBoundingClientRect()
  const svgContainer = event.currentTarget.closest('.svg-container')
  const svgRect = svgContainer.getBoundingClientRect()
  const svg = svgContainer.querySelector('svg')
  const svgViewBox = svg.viewBox.baseVal
  
  // 计算设备在SVG中的当前位置
  const stationPositions = {
    read: { baseX: 100, baseY: 200, width: 200, height: 100 },
    label: { baseX: 400, baseY: 200, width: 200, height: 100 },
    pick: { baseX: 500, baseY: 330, width: 120, height: 80 },
    qc: { baseX: 700, baseY: 200, width: 200, height: 100 },
    network: { baseX: 400, baseY: 100, width: 200, height: 60 }
  }
  const pos = stationPositions[device.station] || { baseX: 0, baseY: 0, width: 200, height: 100 }
  const deviceSvgX = pos.baseX + (device.position.x / 100) * pos.width
  const deviceSvgY = pos.baseY + (device.position.y / 100) * pos.height
  
  // 计算鼠标相对于SVG的坐标
  const mouseX = ((event.clientX - svgRect.left) / svgRect.width) * svgViewBox.width
  const mouseY = ((event.clientY - svgRect.top) / svgRect.height) * svgViewBox.height
  
  dragOffset.value = {
    x: mouseX - deviceSvgX,
    y: mouseY - deviceSvgY
  }
  
  event.preventDefault()
}

// 拖拽设备
const dragDevice = (event) => {
  if (!draggedDevice.value) return
  
  // 在全局事件中，直接查找 SVG 容器
  const svgContainer = document.querySelector('.svg-container')
  if (!svgContainer) return
  
  const svgRect = svgContainer.getBoundingClientRect()
  const svg = svgContainer.querySelector('svg')
  const svgViewBox = svg.viewBox.baseVal
  
  // 计算鼠标在SVG中的坐标
  const mouseX = ((event.clientX - svgRect.left) / svgRect.width) * svgViewBox.width
  const mouseY = ((event.clientY - svgRect.top) / svgRect.height) * svgViewBox.height
  
  // 计算设备在工位内的相对位置（百分比）
  const stationPositions = {
    read: { baseX: 100, baseY: 200, width: 200, height: 100 },
    label: { baseX: 400, baseY: 200, width: 200, height: 100 },
    pick: { baseX: 500, baseY: 330, width: 120, height: 80 },
    qc: { baseX: 700, baseY: 200, width: 200, height: 100 },
    network: { baseX: 400, baseY: 100, width: 200, height: 60 }
  }
  const pos = stationPositions[draggedDevice.value.station] || { baseX: 0, baseY: 0, width: 200, height: 100 }
  
  const deviceSvgX = mouseX - dragOffset.value.x
  const deviceSvgY = mouseY - dragOffset.value.y
  
  // 转换为百分比位置（移除范围限制，允许在整个SVG区域内移动）
  const newX = ((deviceSvgX - pos.baseX) / pos.width) * 100
  const newY = ((deviceSvgY - pos.baseY) / pos.height) * 100
  
  // 移除范围限制，允许设备在整个SVG区域内自由移动
  draggedDevice.value.position.x = newX
  draggedDevice.value.position.y = newY
}

// 结束拖拽
const endDrag = () => {
  draggedDevice.value = null
  dragOffset.value = { x: 0, y: 0 }
}

// 打印所有设备位置
const printDevicePositions = () => {
  console.log('========== 设备位置信息 ==========')
  Object.keys(devices.value).forEach(station => {
    const stationName = station === 'read' ? '读码区' : station === 'label' ? '贴标区' : station === 'pick' ? '取标签区' : station === 'qc' ? '质检区' : '网络区域'
    console.log(`\n【${stationName}】`)
    devices.value[station].forEach(device => {
      const positionStr = `${device.name} (${device.id}): x=${device.position.x.toFixed(2)}, y=${device.position.y.toFixed(2)}, type=${device.type}`
      console.log(positionStr)
    })
  })
  console.log('\n========== 设备位置信息结束 ==========')
  
  // 同时输出为纯文本格式，方便复制
  let textOutput = '========== 设备位置信息 ==========\n'
  Object.keys(devices.value).forEach(station => {
    const stationName = station === 'read' ? '读码区' : station === 'label' ? '贴标区' : station === 'pick' ? '取标签区' : station === 'qc' ? '质检区' : '网络区域'
    textOutput += `\n【${stationName}】\n`
    devices.value[station].forEach(device => {
      textOutput += `${device.name} (${device.id}): x=${device.position.x.toFixed(2)}, y=${device.position.y.toFixed(2)}, type=${device.type}\n`
    })
  })
  textOutput += '\n========== 设备位置信息结束 =========='
  console.log('\n--- 纯文本格式（方便复制） ---')
  console.log(textOutput)
}

// 工件位置（用于动画）
const workpiecePosition = ref({ x: 0, y: 0 })

// 标签位置（用于动画）
const labelPosition = ref({ x: 560, y: 320 }) // 取标签区中心位置
const labelVisible = ref(false)

// ========== 动画参数配置 ==========
// 前进速度（像素/秒，基于SVG viewBox坐标）
const transitSpeed = 100 // 可调整：200像素/秒

// 贴标时长（秒）
const stickLabelTime = 2.0 // 可调整：2秒

// ========== 路径配置 ==========
const surfaceY = 180 // 工位上表面y坐标（已向下移动50像素）
const startX = 100 // 起点x坐标
const labelCenterX = 500 // 贴标区中心x坐标
const endX = 900 // 终点x坐标

// 计算路径距离
const distanceToLabel = labelCenterX - startX // 400像素
const distanceFromLabel = endX - labelCenterX // 400像素
const totalDistance = distanceToLabel + distanceFromLabel // 800像素

// 计算移动时间（秒）
const timeToLabel = distanceToLabel / transitSpeed // 移动到贴标区的时间
const timeFromLabel = distanceFromLabel / transitSpeed // 从贴标区到终点的时间
const totalAnimationTime = timeToLabel + stickLabelTime + timeFromLabel // 总动画时间

// 工件流动动画
let animationFrame = null
let animationStartTime = null

const startWorkpieceAnimation = () => {
  animationStartTime = performance.now() / 1000 // 记录开始时间（秒）
  
  const animate = () => {
    const currentTime = performance.now() / 1000
    const elapsedTime = (currentTime - animationStartTime) % totalAnimationTime // 循环时间
    
    let currentX = startX
    let currentStatus = 'read'
    
    if (elapsedTime < timeToLabel) {
      // 阶段1：从起点移动到贴标区中心（匀速）
      const progress = elapsedTime / timeToLabel
      currentX = startX + progress * distanceToLabel
      currentStatus = 'read'
      labelVisible.value = false
    } else if (elapsedTime < timeToLabel + stickLabelTime) {
      // 阶段2：在贴标区中心暂停（贴标中）
      currentX = labelCenterX
      currentStatus = 'label'
      
      // 标签动画：从取标签区移动到贴标区
      const labelProgress = (elapsedTime - timeToLabel) / stickLabelTime
      if (labelProgress < 0.3) {
        // 标签从取标签区移动到贴标区（前30%时间）
        const moveProgress = labelProgress / 0.3
        labelPosition.value = {
          x: 560 - moveProgress * 60, // 从取标签区(560)移动到贴标区中间(500)
          y: 320 - moveProgress * 190  // 从取标签区(320)移动到贴标区(130)
        }
        labelVisible.value = true
      } else if (labelProgress < 0.7) {
        // 标签在贴标区，正在贴标（中间40%时间）
        labelPosition.value = { x: labelCenterX, y: surfaceY }
        labelVisible.value = true
      } else {
        // 标签完成，隐藏（后30%时间）
        labelVisible.value = false
      }
    } else {
      // 阶段3：从贴标区中心移动到终点（匀速）
      const progress = (elapsedTime - timeToLabel - stickLabelTime) / timeFromLabel
      currentX = labelCenterX + progress * distanceFromLabel
      currentStatus = 'qc'
      labelVisible.value = false
    }
    
    // 更新工件位置
    workpiecePosition.value = { x: currentX, y: surfaceY }
    
    // 更新流程步骤状态
    processSteps.value.forEach(s => s.active = s.id === currentStatus)
    
    animationFrame = requestAnimationFrame(animate)
  }
  animate()
}

onMounted(() => {
  startWorkpieceAnimation()
  // 添加全局鼠标事件监听
  document.addEventListener('mousemove', dragDevice)
  document.addEventListener('mouseup', endDrag)
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  // 移除全局鼠标事件监听
  document.removeEventListener('mousemove', dragDevice)
  document.removeEventListener('mouseup', endDrag)
})

// 设备图标映射（SVG文件路径）
const deviceIcons = {
  plc: '/plc.svg',
  switch: '/switch.svg',
  servo: '/servomotor.svg',
  camera: '/camera.svg',
  light: '💡', // 补光灯，保持emoji
  indicator: '/indicator.svg', // 指示灯
  robot: '/robot.svg',
  tray: '📦', // 标签盘，保持emoji
  monitor: '/monitor.svg', // 工控机
  server: '🖥️' // 服务器（MES/MBI），保持emoji
}

// 判断是否为SVG路径
const isSvgPath = (icon) => {
  return typeof icon === 'string' && icon.endsWith('.svg')
}

// 处理设备点击
const handleDeviceClick = (device) => {
  selectedDevice.value = device
}

// 关闭设备详情
const closeDeviceInfo = () => {
  selectedDevice.value = null
}

</script>

<template>
  <div class="flexible-labeling-machine">
    <!-- 顶部标题栏 -->
    <div class="header-bar">
      <div class="header-left">
        <h2 class="title">柔性贴标工位生产示意图</h2>
      </div>
      <div class="header-right">
        <button 
          class="print-btn" 
          @click="printDevicePositions" 
          title="打印设备位置到控制台"
          :disabled="!devicesLoaded"
        >
          📋 打印设备位置
        </button>
        <button 
          class="toggle-btn" 
          @click="toggleDevicesAndTopology" 
          :title="showDevicesAndTopology ? '隐藏设备和网络拓扑' : '显示设备和网络拓扑'"
          :disabled="!devicesLoaded"
          :class="{ active: showDevicesAndTopology }"
        >
          {{ showDevicesAndTopology ? '👁️ 隐藏设备' : '👁️‍🗨️ 显示设备' }}
        </button>
        <span class="divider">|</span>
        <span class="production-line">{{ productionLine }}</span>
        <span class="divider">|</span>
        <span class="current-time">{{ formattedTime }}</span>
        <span class="divider">|</span>
        <span class="status-badge" :style="{ color: statusColor }">
          <span class="status-dot" :style="{ backgroundColor: statusColor }"></span>
          {{ runStatus }}
        </span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧面板：流程 & 状态 -->
      <div class="left-panel">
        <div class="panel-section">
          <h3 class="section-title">流程步骤</h3>
          <div class="process-steps">
            <div
              v-for="(step, index) in processSteps"
              :key="step.id"
              class="step-item"
              :class="{ active: step.active, completed: index < processSteps.findIndex(s => s.active) }"
            >
              <div class="step-indicator">
                <span class="step-number">{{ index + 1 }}</span>
              </div>
              <span class="step-name">{{ step.name }}</span>
              <div v-if="index < processSteps.length - 1" class="step-connector"></div>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3 class="section-title">生产统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">当前节拍</div>
              <div class="stat-value">{{ stats.cycleTime }}s</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">通过数量</div>
              <div class="stat-value success">{{ stats.passed }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">不良数量</div>
              <div class="stat-value error">{{ stats.failed }}</div>
            </div>
          </div>
          
          <div class="trend-chart">
            <div class="chart-title">节拍趋势</div>
            <div class="chart-container">
              <svg viewBox="0 0 200 60" class="trend-svg">
                <polyline
                  :points="stats.trend.map((v, i) => `${i * 30},${60 - (v - 100) * 0.3}`).join(' ')"
                  fill="none"
                  stroke="#409eff"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间区域：SVG 3D场景 -->
      <div class="center-panel">
        <div class="svg-container">
          <svg viewBox="0 0 1000 500" class="scene-svg">
            <!-- 定义渐变和阴影 -->
            <defs>
              <linearGradient id="readGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#87CEEB;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#4682B4;stop-opacity:0.6" />
              </linearGradient>
              <linearGradient id="labelGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#90EE90;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#32CD32;stop-opacity:0.6" />
              </linearGradient>
              <linearGradient id="pickGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#FFA500;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#FF8C00;stop-opacity:0.6" />
              </linearGradient>
              <linearGradient id="qcGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#DDA0DD;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#BA55D3;stop-opacity:0.6" />
              </linearGradient>
              <filter id="shadow">
                <feDropShadow dx="3" dy="3" stdDeviation="3" flood-opacity="0.3"/>
              </filter>
            </defs>

            <!-- 读码区（3D长方体效果） -->
            <g 
              class="station-group read-station"
            >
              <!-- 顶面 -->
              <polygon
                points="100,200 300,200 320,180 120,180"
                fill="url(#readGradient)"
                filter="url(#shadow)"
              />
              <!-- 前面 -->
              <polygon
                points="100,200 300,200 300,300 100,300"
                fill="url(#readGradient)"
                filter="url(#shadow)"
              />
              <!-- 右侧面 -->
              <polygon
                points="300,200 320,180 320,280 300,300"
                fill="url(#readGradient)"
                opacity="0.7"
              />
              <!-- 工位标签 -->
              <text x="200" y="195" text-anchor="middle" fill="#fff" font-size="16" font-weight="bold">读码区</text>
              <!-- 入口箭头 -->
              <path
                d="M 80 250 L 100 250 L 95 245 M 100 250 L 95 255"
                stroke="#409eff"
                stroke-width="2"
                fill="none"
              />
            </g>

            <!-- 贴标区 -->
            <g 
              class="station-group label-station"
            >
              <!-- 顶面 -->
              <polygon
                points="400,200 600,200 620,180 420,180"
                fill="url(#labelGradient)"
                filter="url(#shadow)"
              />
              <!-- 前面 -->
              <polygon
                points="400,200 600,200 600,300 400,300"
                fill="url(#labelGradient)"
                filter="url(#shadow)"
              />
              <!-- 右侧面 -->
              <polygon
                points="600,200 620,180 620,280 600,300"
                fill="url(#labelGradient)"
                opacity="0.7"
              />
              <!-- 工位标签 -->
              <text x="500" y="195" text-anchor="middle" fill="#fff" font-size="16" font-weight="bold">贴标区</text>
            </g>

            <!-- 取标签区（在贴标区后面） -->
            <g 
              class="station-group pick-station"
            >
              <!-- 顶面 -->
              <polygon
                points="500,330 620,330 630,320 510,320"
                fill="url(#pickGradient)"
                filter="url(#shadow)"
              />
              <!-- 前面 -->
              <polygon
                points="500,330 620,330 620,410 500,410"
                fill="url(#pickGradient)"
                filter="url(#shadow)"
              />
              <!-- 右侧面 -->
              <polygon
                points="620,330 630,320 630,400 620,410"
                fill="url(#pickGradient)"
                opacity="0.7"
              />
              <!-- 工位标签 -->
              <text x="560" y="325" text-anchor="middle" fill="#fff" font-size="14" font-weight="bold">取标签区</text>
              <!-- 标签卷（使用 SVG 文件） -->
              <image
                href="/spool.svg"
                x="545"
                y="332"
                width="30"
                height="30"
                preserveAspectRatio="xMidYMid meet"
                opacity="0.8"
              />
              <!-- 连接线（从取标签区到贴标区） -->
              <path
                d="M 560 330 Q 560 270 500 250"
                stroke="#FFA500"
                stroke-width="2"
                stroke-dasharray="5,5"
                fill="none"
                opacity="0.6"
              />
            </g>

            <!-- 质检区 -->
            <g 
              class="station-group qc-station"
            >
              <!-- 顶面 -->
              <polygon
                points="700,200 900,200 920,180 720,180"
                fill="url(#qcGradient)"
                filter="url(#shadow)"
              />
              <!-- 前面 -->
              <polygon
                points="700,200 900,200 900,300 700,300"
                fill="url(#qcGradient)"
                filter="url(#shadow)"
              />
              <!-- 右侧面 -->
              <polygon
                points="900,200 920,180 920,280 900,300"
                fill="url(#qcGradient)"
                opacity="0.7"
              />
              <!-- 工位标签 -->
              <text x="800" y="195" text-anchor="middle" fill="#fff" font-size="16" font-weight="bold">质检区</text>
            </g>

            <!-- 工件流动动画 -->
            <g 
              class="workpiece-group"
              :transform="`translate(${workpiecePosition.x}, ${workpiecePosition.y})`"
            >
              <!-- 笔记本电脑图片 -->
              <image
                href="/laptop.png"
                x="-25"
                y="-20"
                width="50"
                height="35"
                class="laptop-icon"
                preserveAspectRatio="xMidYMid meet"
                filter="url(#shadow)"
              />
            </g>

            <!-- 标签流动动画 -->
            <g 
              v-if="labelVisible"
              class="label-group"
              :transform="`translate(${labelPosition.x}, ${labelPosition.y})`"
            >
              <!-- 标签图片 -->
              <image
                href="/label.png"
                x="-12"
                y="-12"
                width="24"
                height="24"
                class="label-icon"
                preserveAspectRatio="xMidYMid meet"
                filter="url(#shadow)"
              />
            </g>

            <!-- 传送带连接线（在工位上表面） -->
            <line x1="300" y1="180" x2="400" y2="180" stroke="#666" stroke-width="3" stroke-dasharray="5,5" opacity="0.5"/>
            <line x1="600" y1="180" x2="700" y2="180" stroke="#666" stroke-width="3" stroke-dasharray="5,5" opacity="0.5"/>

            <!-- 网络拓扑连线（从数据库动态加载） -->
            <g v-if="showDevicesAndTopology && devicesLoaded" class="network-topology" stroke="#FFD700" stroke-width="2.5" opacity="0.8" fill="none">
              <line
                v-for="(conn, index) in connections"
                :key="`connection-${conn.source}-${conn.target}-${index}`"
                :x1="getConnectionStartX(conn)"
                :y1="getConnectionStartY(conn)"
                :x2="getConnectionEndX(conn)"
                :y2="getConnectionEndY(conn)"
                :stroke-dasharray="conn.type === 'network' && (conn.source.includes('switch') || conn.target.includes('switch')) ? '3,3' : undefined"
                stroke="#FFD700"
              />
            </g>
          </svg>

          <!-- 设备图标覆盖层（HTML元素，定位在SVG上方） -->
          <div v-if="showDevicesAndTopology && devicesLoaded" class="device-icons-overlay">
            <!-- 读码区设备 -->
            <div
              v-for="device in (devices.read || [])"
              :key="device.id"
              class="device-icon"
              :class="{ 
                active: selectedDevice?.id === device.id,
                hovered: hoveredDevice?.id === device.id,
                dragging: draggedDevice?.id === device.id,
                [device.type]: true
              }"
              :style="getDeviceIconStyle(device, 'read')"
              @click.stop="handleDeviceClick(device)"
              @mouseenter="hoveredDevice = device"
              @mouseleave="hoveredDevice = null"
              @mousedown.stop="startDrag(device, $event)"
            >
              <div class="device-icon-inner">
                <img 
                  v-if="isSvgPath(deviceIcons[device.type])"
                  :src="deviceIcons[device.type]"
                  :alt="device.name"
                  class="device-svg-icon"
                />
                <span v-else class="device-emoji">{{ deviceIcons[device.type] }}</span>
              </div>
              <div class="device-tooltip" v-if="hoveredDevice?.id === device.id">
                <div class="tooltip-name">{{ device.name }}</div>
                <div class="tooltip-status" :class="device.status">
                  {{ device.status === 'online' ? '在线' : '离线' }}
            </div>
          </div>
        </div>

            <!-- 贴标区设备 -->
            <div
              v-for="device in (devices.label || [])"
              :key="device.id"
              class="device-icon"
              :class="{ 
                active: selectedDevice?.id === device.id,
                hovered: hoveredDevice?.id === device.id,
                dragging: draggedDevice?.id === device.id,
                [device.type]: true
              }"
              :style="getDeviceIconStyle(device, 'label')"
              @click.stop="handleDeviceClick(device)"
              @mouseenter="hoveredDevice = device"
              @mouseleave="hoveredDevice = null"
              @mousedown.stop="startDrag(device, $event)"
            >
              <div class="device-icon-inner">
                <img 
                  v-if="isSvgPath(deviceIcons[device.type])"
                  :src="deviceIcons[device.type]"
                  :alt="device.name"
                  class="device-svg-icon"
                />
                <span v-else class="device-emoji">{{ deviceIcons[device.type] }}</span>
            </div>
              <div class="device-tooltip" v-if="hoveredDevice?.id === device.id">
                <div class="tooltip-name">{{ device.name }}</div>
                <div class="tooltip-status" :class="device.status">
                  {{ device.status === 'online' ? '在线' : '离线' }}
          </div>
              </div>
            </div>

            <!-- 取标签区设备 -->
            <div
              v-for="device in (devices.pick || [])"
              :key="device.id"
                class="device-icon"
              :class="{ 
                active: selectedDevice?.id === device.id,
                hovered: hoveredDevice?.id === device.id,
                dragging: draggedDevice?.id === device.id,
                [device.type]: true
              }"
                :style="getDeviceIconStyle(device, 'pick')"
              @click.stop="handleDeviceClick(device)"
              @mouseenter="hoveredDevice = device"
              @mouseleave="hoveredDevice = null"
              @mousedown.stop="startDrag(device, $event)"
            >
              <div class="device-icon-inner">
                <img 
                  v-if="isSvgPath(deviceIcons[device.type])"
                  :src="deviceIcons[device.type]"
                  :alt="device.name"
                  class="device-svg-icon"
                />
                <span v-else class="device-emoji">{{ deviceIcons[device.type] }}</span>
              </div>
              <div class="device-tooltip" v-if="hoveredDevice?.id === device.id">
                <div class="tooltip-name">{{ device.name }}</div>
                <div class="tooltip-status" :class="device.status">
                  {{ device.status === 'online' ? '在线' : '离线' }}
            </div>
          </div>
        </div>

            <!-- 质检区设备 -->
            <div
              v-for="device in (devices.qc || [])"
              :key="device.id"
              class="device-icon"
              :class="{ 
                active: selectedDevice?.id === device.id,
                hovered: hoveredDevice?.id === device.id,
                dragging: draggedDevice?.id === device.id,
                [device.type]: true
              }"
              :style="getDeviceIconStyle(device, 'qc')"
              @click.stop="handleDeviceClick(device)"
              @mouseenter="hoveredDevice = device"
              @mouseleave="hoveredDevice = null"
              @mousedown.stop="startDrag(device, $event)"
            >
              <div class="device-icon-inner">
                <img 
                  v-if="isSvgPath(deviceIcons[device.type])"
                  :src="deviceIcons[device.type]"
                  :alt="device.name"
                  class="device-svg-icon"
                />
                <span v-else class="device-emoji">{{ deviceIcons[device.type] }}</span>
              </div>
              <div class="device-tooltip" v-if="hoveredDevice?.id === device.id">
                <div class="tooltip-name">{{ device.name }}</div>
                <div class="tooltip-status" :class="device.status">
                  {{ device.status === 'online' ? '在线' : '离线' }}
                </div>
              </div>
            </div>

            <!-- 网络区域设备（贴标区上方） -->
            <div
              v-for="device in (devices.network || [])"
              :key="device.id"
              class="device-icon"
              :class="{ 
                active: selectedDevice?.id === device.id,
                hovered: hoveredDevice?.id === device.id,
                dragging: draggedDevice?.id === device.id,
                [device.type]: true
              }"
              :style="getDeviceIconStyle(device, 'network')"
              @click.stop="handleDeviceClick(device)"
              @mouseenter="hoveredDevice = device"
              @mouseleave="hoveredDevice = null"
              @mousedown.stop="startDrag(device, $event)"
            >
              <div class="device-icon-inner">
                <img 
                  v-if="isSvgPath(deviceIcons[device.type])"
                  :src="deviceIcons[device.type]"
                  :alt="device.name"
                  class="device-svg-icon"
                />
                <span v-else class="device-emoji">{{ deviceIcons[device.type] }}</span>
              </div>
              <div class="device-tooltip" v-if="hoveredDevice?.id === device.id">
                <div class="tooltip-name">{{ device.name }}</div>
                <div class="tooltip-status" :class="device.status">
                  {{ device.status === 'online' ? '在线' : '离线' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    getDetailLabel(key) {
      const labels = {
        ip: 'IP地址',
        program: '程序版本',
        port: '端口',
        model: '型号',
        speed: '转速',
        torque: '扭矩',
        exposure: '曝光时间',
        resolution: '分辨率',
        brightness: '亮度',
        color: '色温',
        power: '功率',
        payload: '负载',
        reach: '工作半径',
        capacity: '容量',
        remaining: '剩余',
        type: '类型',
        status: '状态',
        cpu: 'CPU',
        port: '端口'
      }
      return labels[key] || key
    }
  }
}
</script>

<style scoped>
.flexible-labeling-machine {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.95), rgba(6, 25, 44, 0.98));
  color: #e6f1ff;
  border-radius: 12px;
  overflow: hidden;
}

/* 顶部标题栏 */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.9), rgba(6, 25, 44, 0.9));
  border-bottom: 1px solid rgba(88, 178, 255, 0.2);
}

.header-left .title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
}

.print-btn,
.toggle-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
  margin-right: 8px;
}

.print-btn:hover:not(:disabled),
.toggle-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #66b1ff, #409EFF);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.print-btn:active:not(:disabled),
.toggle-btn:active:not(:disabled) {
  transform: translateY(0);
}

.print-btn:disabled,
.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.toggle-btn.active:hover:not(:disabled) {
  background: linear-gradient(135deg, #85ce61, #67C23A);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.production-line {
  color: #80d6ff;
  font-weight: 500;
}

.divider {
  color: rgba(128, 214, 255, 0.3);
}

.current-time {
  color: rgba(214, 232, 255, 0.8);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  font-weight: 600;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.panel-section {
  background: rgba(4, 16, 27, 0.6);
  border: 1px solid rgba(88, 178, 255, 0.12);
  border-radius: 12px;
  padding: 16px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

/* 流程步骤 */
.process-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.step-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(128, 214, 255, 0.2);
  border: 2px solid rgba(128, 214, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.step-item.active .step-indicator {
  background: #409eff;
  border-color: #409eff;
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.6);
}

.step-item.completed .step-indicator {
  background: #67c23a;
  border-color: #67c23a;
}

.step-number {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.step-name {
  flex: 1;
  font-size: 14px;
  color: rgba(214, 232, 255, 0.8);
}

.step-item.active .step-name {
  color: #ffffff;
  font-weight: 600;
}

.step-connector {
  position: absolute;
  left: 16px;
  top: 40px;
  width: 2px;
  height: 20px;
  background: rgba(128, 214, 255, 0.2);
}

.step-item.completed .step-connector {
  background: #67c23a;
}

/* 生产统计 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  background: rgba(88, 178, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
}

.stat-label {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.7);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.error {
  color: #f56c6c;
}

.trend-chart {
  margin-top: 16px;
}

.chart-title {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.7);
  margin-bottom: 8px;
}

.chart-container {
  height: 60px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 8px;
}

.trend-svg {
  width: 100%;
  height: 100%;
}

/* 中间区域：SVG场景 */
.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(4, 16, 27, 0.6);
  border: 1px solid rgba(88, 178, 255, 0.12);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.svg-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.scene-svg {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(4, 16, 27, 0.8), rgba(2, 8, 14, 0.9));
}

.station-group {
  cursor: pointer;
  transition: all 0.3s ease;
}

.station-group:hover polygon {
  opacity: 0.9;
}

/* 工件图标样式 */
.workpiece-group {
  transition: transform 0.1s ease-out;
}

.laptop-icon {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
  animation: laptopFloat 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes laptopFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-1px);
  }
}


/* 标签图标样式 */
.label-group {
  transition: transform 0.1s ease-out;
  z-index: 5;
}

.label-icon {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
  animation: labelFloat 1.5s ease-in-out infinite;
  pointer-events: none;
}

@keyframes labelFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-2px) rotate(5deg);
  }
}

/* 设备图标覆盖层 */
.device-icons-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.device-icon {
  position: absolute;
  width: 40px;
  height: 40px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  pointer-events: all;
  z-index: 10;
  transition: all 0.3s ease;
}

.device-icon:hover {
  transform: translate(-50%, -50%) scale(1.2);
  z-index: 20;
}

.device-icon.active {
  transform: translate(-50%, -50%) scale(1.3);
  z-index: 15;
}

.device-icon-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  border: 2px solid rgba(64, 158, 255, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 20px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.device-icon-inner .device-svg-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.device-icon.dragging {
  cursor: grabbing !important;
  z-index: 1000;
  opacity: 0.9;
  transform: scale(1.1);
}

.device-icon.dragging .device-icon-inner {
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
  border: 2px solid #FFD700;
}

.device-icon:hover .device-icon-inner,
.device-icon.active .device-icon-inner {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-color: #ffffff;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4), 0 0 30px rgba(64, 158, 255, 0.6);
}

.device-emoji {
  font-size: 20px;
}

.device-svg-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
  display: block;
}

.device-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  background: rgba(0, 0, 0, 0.9);
  color: #ffffff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 30;
}

.device-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid rgba(0, 0, 0, 0.9);
}

.tooltip-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.tooltip-status {
  font-size: 11px;
  color: #67c23a;
}

.tooltip-status.offline {
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .left-panel {
    width: 240px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    max-height: 200px;
  }
  
  .center-panel {
    min-height: 400px;
  }
}
</style>