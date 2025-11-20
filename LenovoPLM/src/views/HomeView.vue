<script setup>
import { onMounted, ref } from 'vue'
import MetricsGrid from '../components/home/MetricsGrid.vue'
import { fetchHomeOverview } from '../services/api'

const metrics = ref({})
const loading = ref(true)
const errorMessage = ref('')

const topologyNodes = [
  { id: 'switch', label: 'TSN交换机', x: 18, y: 46, color: '#4cc9f0', type: 'switch' },
  { id: 'edge', label: '工控机', x: 36, y: 38, color: '#4361ee', type: 'monitor' },
  { id: 'camera', label: '工业相机', x: 28, y: 68, color: '#3a0ca3', type: 'camera' },
  { id: 'plc', label: 'PLC', x: 52, y: 60, color: '#f72585', type: 'plc' },
  { id: 'robot', label: '机械臂控制器', x: 61, y: 33, color: '#ffba08', type: 'robot' },
  { id: 'gateway', label: '可信网关', x: 77, y: 48, color: '#06d6a0', type: 'shield' },
  { id: 'blockchain', label: '区块链节点', x: 90, y: 44, color: '#ff6b6b', type: 'chain' },
]

const topologyLinks = [
  ['camera', 'switch'],
  ['plc', 'switch'],
  ['robot', 'edge'],
  ['switch', 'edge'],
  ['edge', 'gateway'],
  ['gateway', 'blockchain'],
]

const deviceIcons = {
  plc: '/plc.svg',
  switch: '/switch.svg',
  camera: '/camera.svg',
  monitor: '/monitor.svg',
  robot: '/robot.svg',
  shield: '/indicator.svg',
  chain: '⛓',
}

const isSvgPath = (icon) => typeof icon === 'string' && icon.endsWith('.svg')

const getNodeStyle = (node) => ({
  left: `${node.x}%`,
  top: `${node.y}%`,
  '--node-color': node.color,
})

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const overviewResponse = await fetchHomeOverview()
    metrics.value = overviewResponse.data
  } catch (error) {
    errorMessage.value = '数据加载出现波动，请稍后重试。'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="home-view">
    <MetricsGrid :metrics="metrics" />

    <section class="blockchain-section">
      <div class="section-header">
        <div>
          <h2>生产数据上链可视化</h2>
          <p>生产线设备通过可信网关实时上传数据，形成区块链可信账本</p>
        </div>
        <div class="section-tag">实时上链</div>
      </div>
      <div class="line-visual">
        <div class="line-background"></div>
        <svg class="topology-overlay" viewBox="0 0 100 70" preserveAspectRatio="xMidYMid meet">
          <defs>
            <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L6,3 L0,6 z" fill="#93c5fd" />
            </marker>
          </defs>
          <line
            v-for="(link, index) in topologyLinks"
            :key="`link-${index}`"
            :x1="topologyNodes.find((n) => n.id === link[0]).x"
            :y1="topologyNodes.find((n) => n.id === link[0]).y"
            :x2="topologyNodes.find((n) => n.id === link[1]).x"
            :y2="topologyNodes.find((n) => n.id === link[1]).y"
            stroke="#93c5fd"
            stroke-width="1.2"
            stroke-dasharray="3 2"
            marker-end="url(#arrow)"
            opacity="0.7"
          />
        </svg>
        <div
          v-for="node in topologyNodes"
          :key="node.id"
          class="device-node"
          :style="getNodeStyle(node)"
        >
          <div class="device-node-icon">
            <img
              v-if="isSvgPath(deviceIcons[node.type])"
              :src="deviceIcons[node.type]"
              alt=""
            />
            <span v-else>{{ deviceIcons[node.type] || '●' }}</span>
          </div>
          <span class="device-node-label">{{ node.label }}</span>
        </div>
        <div class="blockchain-stack">
          <div class="chain-layer" v-for="i in 4" :key="i" :style="{ transform: `translateZ(${i * 6}px)` }"></div>
          <div class="chain-label">
            <span>区块链账本</span>
            <p>跨企业可信共享</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="loading" class="loading">数据加载中...</section>
    <section v-else-if="errorMessage" class="error">{{ errorMessage }}</section>
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 26px;
  color: #ffffff;
}

.section-header p {
  margin: 6px 0 0;
  color: rgba(214, 232, 255, 0.7);
  letter-spacing: 0.4px;
}

.section-tag {
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  color: #80d6ff;
  font-size: 13px;
  letter-spacing: 1px;
}

.blockchain-section {
  padding: 32px;
  background: linear-gradient(135deg, rgba(10, 32, 51, 0.9), rgba(5, 18, 30, 0.92));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.28);
}

.line-visual {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  min-height: 360px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.line-background {
  position: absolute;
  inset: 0;
  background-image: url('/product_line.png');
  background-size: cover;
  background-position: center;
  filter: saturate(1.1) brightness(0.9);
  opacity: 0.85;
}

.topology-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.device-node {
  position: absolute;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #e2e8f0;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.device-node-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: 1px solid var(--node-color, rgba(255, 255, 255, 0.3));
  background: rgba(10, 20, 35, 0.8);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
}

.device-node-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
}

.device-node-icon span {
  font-size: 20px;
}

.device-node-label {
  font-size: 13px;
  letter-spacing: 0.5px;
}

.blockchain-stack {
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  perspective: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.chain-layer {
  width: 110px;
  height: 44px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.9), rgba(255, 175, 113, 0.9));
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(255, 135, 135, 0.35);
  opacity: 0.9;
}

.chain-label {
  text-align: center;
  color: #ffe5e0;
  letter-spacing: 1px;
}

.chain-label span {
  font-size: 16px;
  font-weight: 600;
}

.chain-label p {
  margin: 4px 0 0;
  font-size: 13px;
  color: rgba(255, 229, 224, 0.8);
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
</style>

