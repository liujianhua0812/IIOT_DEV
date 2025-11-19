.order-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}

.log-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #ffffff;
}

.log-panel-header p {
  margin: 4px 0 0;
  color: rgba(214, 232, 255, 0.65);
  font-size: 13px;
}

.log-total {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(73, 197, 255, 0.2);
  color: #49c5ff;
  font-weight: 600;
}

.log-section {
  margin-top: 24px;
  background: rgba(7, 27, 44, 0.85);
  border-radius: 16px;
  border: 1px solid rgba(88, 178, 255, 0.15);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 450px;
  max-height: 450px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  box-sizing: border-box;
}

.log-list::-webkit-scrollbar {
  width: 6px;
}

.log-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.log-list::-webkit-scrollbar-thumb {
  background: rgba(88, 178, 255, 0.3);
  border-radius: 3px;
}

.log-list::-webkit-scrollbar-thumb:hover {
  background: rgba(88, 178, 255, 0.5);
}

.log-item {
  border: 1px solid rgba(88, 178, 255, 0.08);
  border-radius: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
  min-height: fit-content;
}

.log-line {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #e6f1ff;
  line-height: 1.5;
  word-break: break-all;
}

.log-formatted {
  display: block;
  white-space: pre-wrap;
}

.log-top {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.log-stage {
  color: #ffd04b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.log-time {
  color: rgba(214, 232, 255, 0.6);
}

.log-message {
  font-size: 13px;
  color: #e6f1ff;
}

.log-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}

@media (max-width: 1200px) {
  .machine-content {
    flex-direction: column;
  }

  .side-panels {
    width: 100%;
  }
}
<script setup>
import { onMounted, onUnmounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import MetricsGrid from '../components/home/MetricsGrid.vue'
import FlexibleLabelingMachine from '../components/home/FlexibleLabelingMachine.vue'
import {
  fetchHomeDeployments,
  fetchHomeOverview,
  fetchInProgressOrders,
} from '../services/api'

const router = useRouter()

const metrics = ref({})
const deployments = ref([])
const loading = ref(true)
const errorMessage = ref('')
const orderLoading = ref(true)
const orderError = ref('')
const inProgressOrders = ref([])
const simulationLogs = ref([])
const simulationError = ref('')
let socket = null

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''
  orderError.value = ''
  orderLoading.value = true

  try {
    const [overviewResponse, deploymentsResponse, orderResponse] = await Promise.all([
      fetchHomeOverview(),
      fetchHomeDeployments(),
      fetchInProgressOrders(),
    ])

    metrics.value = overviewResponse.data
    deployments.value = deploymentsResponse.data.deployments || []
    inProgressOrders.value = orderResponse.data.orders || []
  } catch (error) {
    errorMessage.value = '数据加载出现波动，请稍后重试。'
    orderError.value = '订单数据加载失败'
    console.error(error)
  } finally {
    loading.value = false
    orderLoading.value = false
  }
}

const connectWebSocket = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10060'
  
  // Connect to WebSocket
  socket = io(`${apiBaseUrl}/simulation`, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5,
  })

  socket.on('connect', () => {
    console.log('WebSocket connected')
    simulationError.value = ''
  })

  socket.on('disconnect', () => {
    console.log('WebSocket disconnected')
    simulationError.value = 'WebSocket 连接已断开'
  })

  socket.on('connect_error', (error) => {
    console.error('WebSocket connection error:', error)
    simulationError.value = 'WebSocket 连接失败'
  })

  // Receive initial events
  socket.on('initial_events', (data) => {
    if (data.events && Array.isArray(data.events)) {
      // Limit to latest 20 events
      simulationLogs.value = data.events.slice(0, 20)
    }
  })

  // Receive real-time simulation events
  socket.on('simulation_event', (event) => {
    console.log('Received simulation event:', event)
    // Create a new array to ensure Vue reactivity
    const newLogs = [event, ...simulationLogs.value]
    // Keep only the latest 20 events
    simulationLogs.value = newLogs.slice(0, 20)
  })
}

const disconnectWebSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

const formatLogTime = (value) => {
  if (!value) return '--:--:--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--:--:--'
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

const getOrderProgress = (order) => {
  if (!order?.quantity) return 0
  const pct = (order.completed / order.quantity) * 100
  return Math.min(Math.max(Math.round(pct), 0), 100)
}

const pendingCount = (order) => {
  if (!order) return 0
  return order.pending ?? Math.max((order.quantity || 0) - (order.completed || 0), 0)
}

onMounted(() => {
  loadData()
  connectWebSocket()
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<template>
  <div class="home-view">


    
    <MetricsGrid :metrics="metrics" />
    <section class="machine-section">
      <div class="section-header">
        <h2>柔性贴标生产线</h2>
        <p>实时监控生产流程各环节设备状态</p>
      </div>
      <div class="machine-content">
        <div class="machine-container">
          <FlexibleLabelingMachine />
        </div>
        <aside class="side-panels">
          <div class="panel-block order-panel">
            <div class="order-panel-header">
              <div>
                <h3>执行中订单</h3>
                <p>当前状态为 In Progress 的订单</p>
              </div>
              <span class="order-total">{{ inProgressOrders.length }}</span>
            </div>
            <div v-if="orderLoading" class="panel-state">订单数据加载中...</div>
            <div v-else-if="orderError" class="panel-state error-state">{{ orderError }}</div>
            <div v-else-if="!inProgressOrders.length" class="panel-state">暂无执行中的生产订单</div>
            <div v-else class="order-list">
              <div v-for="order in inProgressOrders" :key="order.order_id" class="order-card">
                <div class="order-card-header">
                  <div>
                    <div class="order-code">{{ order.order_code || '未命名订单' }}</div>
                    <div class="order-product">{{ order.product_name }} · {{ order.product_code }}</div>
                  </div>
                  <div class="order-delivery">{{ formatDate(order.delivery_date) }}</div>
                </div>
                <div class="order-progress">
                  <div class="progress-bar">
                    <span class="progress-fill" :style="{ width: `${getOrderProgress(order)}%` }"></span>
                  </div>
                  <div class="progress-stats">
                    <span>已完成 {{ order.completed }}</span>
                    <span>待完成 {{ pendingCount(order) }}</span>
                  </div>
                </div>
                <div class="order-meta">
                  <span>计划量：{{ order.quantity }}</span>
                  <span>排产：{{ formatDate(order.scheduled_date) }}</span>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
      <div class="log-section">
        <div class="log-panel-header">
          <div>
            <h3>日志</h3>
            <p>生产执行过程实时反馈</p>
          </div>
          <span class="log-total">{{ simulationLogs.length }}</span>
        </div>
        <div v-if="simulationError" class="panel-state error-state">{{ simulationError }}</div>
        <div v-else-if="!simulationLogs.length" class="panel-state">暂无仿真事件</div>
        <div v-else class="log-list" style="height: 450px; max-height: 450px; overflow-y: auto; overflow-x: hidden;">
          <div v-for="log in simulationLogs" :key="log.id" class="log-item">
            <div class="log-line">
              <span v-if="log.log_line" class="log-formatted">{{ log.log_line }}</span>
              <span v-else class="log-formatted">{{ formatLogTime(log.timestamp) }} | [{{ log.level || 'INFO' }}] [{{ log.source || 'System' }}] | {{ log.message }}</span>
            </div>
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
  0%,
  100% {
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

.machine-section {
  padding: 32px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.08);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
}

.section-header {
  text-align: center;
  margin-bottom: 32px;
}

.section-header h2 {
  font-size: 28px;
  margin-bottom: 8px;
  letter-spacing: 1.2px;
  color: #ffffff;
}

.section-header p {
  font-size: 14px;
  color: rgba(214, 232, 255, 0.7);
  letter-spacing: 0.5px;
}

.machine-content {
  display: flex;
  gap: 24px;
  align-items: stretch;
}

.machine-container {
  flex: 1;
  background: rgba(4, 16, 27, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  overflow: hidden;
  min-height: 600px;
}

.side-panels {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-block {
  background: rgba(7, 27, 44, 0.85);
  border-radius: 16px;
  border: 1px solid rgba(88, 178, 255, 0.15);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.order-panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #ffffff;
}

.order-panel-header p {
  margin: 4px 0 0;
  color: rgba(214, 232, 255, 0.65);
  font-size: 13px;
}

.order-total {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  font-weight: 700;
  font-size: 18px;
  color: #0b2338;
}

.panel-state {
  padding: 18px;
  text-align: center;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  color: rgba(214, 232, 255, 0.75);
  font-size: 14px;
}

.panel-state.error-state {
  color: #ff9a9e;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 4px;
}

.order-card {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(88, 178, 255, 0.12);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.order-code {
  font-weight: 600;
  letter-spacing: 0.5px;
}

.order-product {
  font-size: 13px;
  color: rgba(214, 232, 255, 0.65);
}

.order-delivery {
  font-size: 13px;
  color: #ffd04b;
}

.order-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  display: block;
  height: 100%;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  border-radius: 999px;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(214, 232, 255, 0.75);
}

.order-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}
</style>

