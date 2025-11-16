<script setup>
import { computed, onMounted, ref } from 'vue'
import { registerMap } from 'echarts/core'
import VChart from 'vue-echarts'
import { fetchChinaGeoJson } from '@/services/api'

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
    // 从后端 API 获取地图数据（后端会代理请求到阿里云）
    const response = await fetchChinaGeoJson()
    const geoJson = response.data

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
    if (error.response?.data?.fallback || error.response?.status === 503 || error.response?.status === 500) {
      mapError.value = '地图边界数据加载失败，将显示简化视图。'
    } else {
      mapError.value = '地图边界数据加载失败，将显示简化视图。'
    }
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
    // layoutCenter: ['50%', '50%'],
    // layoutSize: '95%',
    // zoom: 1.2,
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
    aspectScale: 0.75,
    layoutCenter: ['50%', '50%'],
    layoutSize: '95%',
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
  position: relative;
  border-radius: 20px;
  padding: 0;
  background: radial-gradient(circle at top, rgba(16, 55, 92, 0.9), rgba(7, 27, 44, 0.95));
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 26px 48px rgba(0, 0, 0, 0.35);
  color: #d6ecff;
  overflow: hidden;
  min-height: 600px;
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

.map-header > div {
  pointer-events: auto;
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
  pointer-events: auto;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: radial-gradient(circle, #80d6ff, #49c5ff);
  box-shadow: 0 0 12px rgba(128, 214, 255, 0.6);
}

.map-view {
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.map-loading,
.map-error {
  width: 100%;
  height: 100%;
  min-height: 600px;
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

