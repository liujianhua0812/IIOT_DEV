<template>
  <el-dialog
    v-model="visible"
    title="在地图上选择位置"
    width="800px"
    :close-on-click-modal="false"
    :append-to-body="true"
    :modal="true"
    @close="handleClose"
    @opened="handleDialogOpened"
  >
    <div class="coordinate-picker-container">
      <div class="map-wrapper">
        <div id="coordinate-picker-map" class="map-container"></div>
        <div class="map-tips">
          <p>💡 提示：点击地图选择位置，可以拖拽标记微调位置</p>
        </div>
      </div>
      
      <div class="coordinate-display">
        <el-form label-width="80px" label-position="left">
          <el-form-item label="经度">
            <el-input-number
              v-model="currentLng"
              :precision="6"
              :min="-180"
              :max="180"
              style="width: 100%"
              @change="handleCoordinateChange"
            />
          </el-form-item>
          <el-form-item label="纬度">
            <el-input-number
              v-model="currentLat"
              :precision="6"
              :min="-90"
              :max="90"
              style="width: 100%"
              @change="handleCoordinateChange"
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              plain
              @click="showAddressSearch = !showAddressSearch" 
              style="width: 100%"
            >
              {{ showAddressSearch ? '隐藏地址搜索' : '通过地址搜索位置' }}
            </el-button>
          </el-form-item>
          <el-form-item v-if="showAddressSearch" label="地址">
            <el-input
              v-model="searchAddress"
              placeholder="请输入地址，如：韶山东路与莲城大道交叉口"
              @keyup.enter="searchByAddress"
              clearable
            >
              <template #append>
                <el-button @click="searchByAddress">搜索</el-button>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确认使用此坐标</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  initialLng: {
    type: Number,
    default: 112.927176
  },
  initialLat: {
    type: Number,
    default: 27.87076
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const visible = ref(props.modelValue)
const currentLng = ref(props.initialLng)
const currentLat = ref(props.initialLat)
const searchAddress = ref('')
const showAddressSearch = ref(false)

let map = null
let marker = null
let geocoder = null
let infoWindow = null

// 高德地图API Key（从TellhowTraffic项目中使用相同的key）
const AMAP_KEY = 'b075228d554cb53a8547f722facd0826'

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // 等待对话框完全打开后再初始化地图
    nextTick(() => {
      setTimeout(() => {
        loadAMapScript()
      }, 100)
    })
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

watch(() => props.initialLng, (val) => {
  if (val) currentLng.value = val
})

watch(() => props.initialLat, (val) => {
  if (val) currentLat.value = val
})

const loadAMapScript = () => {
  if (window.AMap) {
    initMap()
    return
  }
  
  // 检查是否已经在加载
  if (document.querySelector(`script[src*="webapi.amap.com"]`)) {
    // 等待加载完成
    const checkInterval = setInterval(() => {
      if (window.AMap) {
        clearInterval(checkInterval)
        initMap()
      }
    }, 100)
    return
  }
  
  // 如果已经加载过高德地图，直接初始化
  if (window.AMap) {
    nextTick(() => {
      initMap()
    })
    return
  }
  
  const script = document.createElement('script')
  const callbackName = `initAMapCallback_${Date.now()}`
  script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&callback=${callbackName}`
  script.async = true
  script.defer = true
  
  // 设置全局回调函数
  window[callbackName] = () => {
    nextTick(() => {
      initMap()
    })
    delete window[callbackName]
  }
  
  script.onerror = () => {
    ElMessage.error('高德地图加载失败，请检查网络连接')
    console.error('Failed to load AMap')
    delete window[callbackName]
  }
  
  document.head.appendChild(script)
}

const initMap = () => {
  if (!document.getElementById('coordinate-picker-map')) {
    return
  }
  
  const AMap = window.AMap
  if (!AMap) {
    ElMessage.error('高德地图未加载')
    return
  }
  
  try {
    // 初始化地图
    map = new AMap.Map('coordinate-picker-map', {
      zoom: 18,
      center: [currentLng.value, currentLat.value],
      viewMode: '3D',
      mapStyle: 'amap://styles/normal',
      zoomEnable: true,
      dragEnable: true,
      resizeEnable: true
    })
    
    // 立即绑定点击事件（不等待complete事件）
    map.on('click', handleMapClick)
    
    // 使用 AMap.plugin() 加载 Geocoder 插件
    AMap.plugin('AMap.Geocoder', () => {
      // 插件加载完成后，初始化地理编码服务
      try {
        geocoder = new AMap.Geocoder({
          city: '湘潭市'
        })
        console.log('Geocoder 插件加载完成')
      } catch (error) {
        console.error('初始化 Geocoder 失败:', error)
        // 不显示错误消息，因为地址搜索功能是可选的
      }
    })
    
    // 地图加载完成后的处理
    map.on('complete', () => {
      console.log('地图加载完成，确保点击事件已绑定')
      
      // 确保点击事件已绑定（可能已经绑定了，这里再次确保）
      map.off('click', handleMapClick)
      map.on('click', handleMapClick)
      
      // 如果有初始坐标，添加标记
      if (currentLng.value && currentLat.value) {
        addMarker(currentLng.value, currentLat.value)
      }
      
      // 触发一次地图渲染，确保地图可以正常交互
      setTimeout(() => {
        if (map) {
          map.resize()
          console.log('地图已调整大小，交互已激活')
        }
      }, 200)
      
      ElMessage.success('地图加载完成，点击地图选择位置')
    })
    
  } catch (error) {
    console.error('初始化地图失败:', error)
    ElMessage.error('初始化地图失败: ' + error.message)
  }
}

const handleMapClick = (e) => {
  console.log('地图被点击:', e)
  
  // 确保事件对象存在
  if (!e || !e.lnglat) {
    console.warn('地图点击事件无效:', e)
    return
  }
  
  const lng = e.lnglat.getLng()
  const lat = e.lnglat.getLat()
  
  console.log('点击位置坐标:', lng, lat)
  
  currentLng.value = lng
  currentLat.value = lat
  
  addMarker(lng, lat)
  
  // 显示信息窗口
  showInfoWindow(lng, lat)
  
  ElMessage.info(`已选择位置：经度 ${lng.toFixed(6)}, 纬度 ${lat.toFixed(6)}`)
}

const addMarker = (lng, lat) => {
  const AMap = window.AMap
  if (!AMap || !map) return
  
  if (marker) {
    marker.setPosition([lng, lat])
  } else {
    marker = new AMap.Marker({
      position: [lng, lat],
      map: map,
      draggable: true,
      cursor: 'move'
    })
    
    // 监听标记拖拽事件
    marker.on('dragend', (e) => {
      const pos = marker.getPosition()
      currentLng.value = pos.getLng()
      currentLat.value = pos.getLat()
      showInfoWindow(currentLng.value, currentLat.value)
    })
    
    // 监听标记点击事件
    marker.on('click', (e) => {
      showInfoWindow(currentLng.value, currentLat.value)
    })
  }
  
  // 将地图中心移到标记位置
  map.setCenter([lng, lat])
}

const showInfoWindow = (lng, lat) => {
  const AMap = window.AMap
  if (!AMap || !map) return
  
  const content = `
    <div style="padding: 10px; min-width: 200px;">
      <p style="margin: 5px 0;"><strong>位置坐标</strong></p>
      <p style="margin: 5px 0;">经度: ${lng.toFixed(6)}</p>
      <p style="margin: 5px 0;">纬度: ${lat.toFixed(6)}</p>
    </div>
  `
  
  // 如果信息窗口已存在，更新内容并重新打开
  if (infoWindow) {
    infoWindow.close()
  }
  
  infoWindow = new AMap.InfoWindow({
    content: content,
    offset: new AMap.Pixel(0, -40),
    closeWhenClickMap: true
  })
  infoWindow.open(map, [lng, lat])
}

const handleCoordinateChange = () => {
  if (currentLng.value && currentLat.value) {
    addMarker(currentLng.value, currentLat.value)
    if (map) {
      map.setCenter([currentLng.value, currentLat.value])
    }
  }
}

const searchByAddress = async () => {
  if (!searchAddress.value.trim()) {
    ElMessage.warning('请输入地址')
    if (!showAddressSearch.value) {
      showAddressSearch.value = true
    }
    return
  }
  
  if (!geocoder) {
    if (!window.AMap || !map) {
      ElMessage.error('地图未加载')
      return
    }
    
    // 使用 AMap.plugin() 加载 Geocoder 插件
    try {
      await new Promise((resolve, reject) => {
        AMap.plugin('AMap.Geocoder', () => {
          try {
            geocoder = new AMap.Geocoder({
              city: '湘潭市'
            })
            console.log('Geocoder 插件加载完成（延迟加载）')
            resolve()
          } catch (error) {
            reject(error)
          }
        })
        
        // 设置超时，避免无限等待
        setTimeout(() => {
          if (!geocoder) {
            reject(new Error('Geocoder 插件加载超时'))
          }
        }, 5000)
      })
    } catch (error) {
      console.error('初始化 Geocoder 失败:', error)
      ElMessage.error('地址搜索功能初始化失败，请稍后重试')
      return
    }
  }
  
  try {
    geocoder.getLocation(searchAddress.value, (status, result) => {
      if (status === 'complete' && result.geocodes && result.geocodes.length > 0) {
        const location = result.geocodes[0].location
        const lng = location.getLng()
        const lat = location.getLat()
        
        currentLng.value = lng
        currentLat.value = lat
        
        addMarker(lng, lat)
        showInfoWindow(lng, lat)
        
        ElMessage.success('地址定位成功')
      } else {
        ElMessage.error('未找到该地址，请尝试更详细的地址')
      }
    })
  } catch (error) {
    console.error('地址搜索失败:', error)
    ElMessage.error('地址搜索失败: ' + error.message)
  }
}

const handleConfirm = () => {
  if (!currentLng.value || !currentLat.value) {
    ElMessage.warning('请先选择位置坐标')
    return
  }
  
  emit('confirm', {
    longitude: currentLng.value,
    latitude: currentLat.value
  })
  
  visible.value = false
}

const handleCancel = () => {
  emit('cancel')
  visible.value = false
}

const handleDialogOpened = () => {
  // 对话框打开后，确保地图可以正常交互
  console.log('对话框已打开，准备初始化地图')
  nextTick(() => {
    if (map) {
      // 如果地图已存在，重新调整大小并绑定事件
      setTimeout(() => {
        map.resize()
        // 重新绑定点击事件
        map.off('click', handleMapClick)
        map.on('click', handleMapClick)
        console.log('地图已存在，重新激活交互')
      }, 100)
    } else {
      // 如果地图还没有初始化，等待一下再初始化
      setTimeout(() => {
        if (!map) {
          if (window.AMap) {
            initMap()
          } else {
            loadAMapScript()
          }
        }
      }, 300)
    }
  })
}

const handleClose = () => {
  // 清理资源
  if (infoWindow) {
    infoWindow.close()
    infoWindow = null
  }
  if (marker) {
    marker.setMap(null)
    marker = null
  }
  if (map) {
    // 移除所有事件监听器
    map.off('click', handleMapClick)
    map.destroy()
    map = null
  }
}

onMounted(() => {
  if (visible.value) {
    // 等待DOM完全渲染后再初始化地图
    nextTick(() => {
      setTimeout(() => {
        loadAMapScript()
      }, 200)
    })
  }
})

onUnmounted(() => {
  handleClose()
})
</script>

<style scoped>
.coordinate-picker-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.map-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.map-container {
  width: 100%;
  height: 400px;
  position: relative;
  z-index: 1;
  pointer-events: auto;
}

.map-tips {
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-top: 1px solid #dcdfe6;
  font-size: 12px;
  color: #606266;
}

.coordinate-display {
  padding: 16px;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.coordinate-display :deep(.el-form-item) {
  margin-bottom: 16px;
}

.coordinate-display :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}
</style>
