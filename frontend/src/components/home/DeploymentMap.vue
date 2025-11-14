<script setup>
import { computed, onMounted, ref } from 'vue'
import { registerMap } from 'echarts/core'
import VChart from 'vue-echarts'

const props = defineProps({
  deployments: {
    type: Array,
    default: () => [],
  },
})

const mapReady = ref(false)
const mapError = ref('')

const loadMap = async () => {
  if (mapReady.value) {
    return
  }

  try {
    // 尝试从阿里云加载地图数据
    const response = await fetch('https://geo.datav.aliyun.com/areas/bound/geojson?code=100000_full', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // 添加超时控制
      signal: AbortSignal.timeout(10000), // 10秒超时
    })

    // 检查响应状态
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 先读取响应文本
    const text = await response.text()
    
    // 检查内容类型
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      console.warn('响应不是 JSON:', text.substring(0, 200))
      throw new Error('响应不是 JSON 格式，可能是 HTML 错误页面')
    }

    // 解析 JSON
    let geoJson
    try {
      geoJson = JSON.parse(text)
    } catch (parseError) {
      console.warn('JSON 解析失败:', parseError)
      throw new Error('无法解析 JSON 响应')
    }
    
    // 验证是否是有效的 GeoJSON
    if (!geoJson || !geoJson.type) {
      throw new Error('无效的 GeoJSON 数据')
    }

    registerMap('china', geoJson)
    mapReady.value = true
    mapError.value = ''
  } catch (error) {
    console.error('加载地图数据失败', error)
    // 如果加载失败，仍然允许显示散点图（使用地理坐标系但不显示地图边界）
    mapError.value = '地图边界数据加载失败，将显示简化视图。'
    mapReady.value = true
  }
}

onMounted(loadMap)

const chartOptions = computed(() => {
  // 如果地图数据加载成功且没有错误，使用完整地图
  // 否则使用简化的地理坐标系（只显示散点，不显示地图边界）
  const hasMapData = mapReady.value && !mapError.value
  
  const geoConfig = hasMapData ? {
    map: 'china',
    roam: false,
    aspectScale: 0.8,
    label: {
      show: false,
      color: '#a0c4ff',
    },
    itemStyle: {
      areaColor: '#0c243f',
      borderColor: '#285477',
      shadowColor: 'rgba(0, 0, 0, 0.4)',
      shadowBlur: 16,
    },
    emphasis: {
      itemStyle: {
        areaColor: '#2b6cb0',
      },
    },
  } : {
    // 如果地图数据未加载，使用地理坐标系但不显示地图边界
    roam: true,
    aspectScale: 0.8,
    layoutCenter: ['50%', '50%'],
    layoutSize: '80%',
    silent: true, // 不响应鼠标事件
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(12, 26, 44, 0.92)',
      borderColor: '#49c5ff',
      textStyle: {
        color: '#d6ecff',
      },
      formatter: (params) => {
        const data = params.data || {}
        return `
          <div style="min-width:160px;">
            <div style="font-weight:600;margin-bottom:6px;color:#49c5ff;">${data.name || '-'}</div>
            <div>接入设备：<strong>${data.devices ?? '--'}</strong></div>
            <div>运行状态：${data.status ?? '--'}</div>
          </div>
        `
      },
    },
    geo: geoConfig,
  series: [
    {
      name: '部署节点',
      type: 'effectScatter',
      coordinateSystem: 'geo',
      rippleEffect: {
        brushType: 'stroke',
        scale: 5,
      },
      symbolSize: (val, params) => {
        const devices = params.data.devices ?? 0
        return Math.max(12, Math.min(devices / 25, 36))
      },
      itemStyle: {
        color: '#49c5ff',
        shadowBlur: 18,
        shadowColor: 'rgba(73, 197, 255, 0.45)',
      },
      data: props.deployments,
    },
  ],
  }
})

</script>

<template>
  <section class="map-card">
    <header class="map-header">
      <div>
        <h2>系统部署全景</h2>
        <p>实时洞察各区域部署节点与运行状态</p>
      </div>
      <div class="legend">
        <span class="legend-dot"></span>
        <span>节点规模</span>
      </div>
    </header>
    <VChart v-if="mapReady" class="map-view" :option="chartOptions" autoresize />
    <div v-else class="map-loading">地图载入中...</div>
    <div v-if="mapError" class="map-warning">{{ mapError }}</div>
  </section>
</template>

<style scoped>
.map-card {
  border-radius: 20px;
  padding: 28px;
  background: radial-gradient(circle at top, rgba(16, 55, 92, 0.9), rgba(7, 27, 44, 0.95));
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 26px 48px rgba(0, 0, 0, 0.35);
  color: #d6ecff;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-header h2 {
  font-size: 22px;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.map-header p {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
}

.legend {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  opacity: 0.85;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: radial-gradient(circle, #80d6ff, #49c5ff);
  box-shadow: 0 0 12px rgba(128, 214, 255, 0.6);
}

.map-view {
  height: 520px;
}

.map-loading,
.map-error {
  height: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(214, 232, 255, 0.78);
  font-size: 15px;
  letter-spacing: 0.8px;
}

.map-error {
  color: #ff9a9e;
}

.map-warning {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: rgba(255, 199, 92, 0.2);
  border: 1px solid rgba(255, 199, 92, 0.4);
  border-radius: 6px;
  font-size: 12px;
  color: #ffc75c;
  z-index: 10;
}
</style>

