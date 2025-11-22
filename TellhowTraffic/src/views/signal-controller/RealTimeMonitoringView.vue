<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 实时数据
const currentPhase = ref({
  id: 1,
  name: '东西直行',
  remainingTime: 25,
  totalTime: 30
})

const directions = ref([
  {
    direction: 'north',
    label: '北向',
    trafficFlow: 450,
    queueLength: 85,
    unit: 'veh/h'
  },
  {
    direction: 'east',
    label: '东向',
    trafficFlow: 520,
    queueLength: 120,
    unit: 'veh/h'
  },
  {
    direction: 'south',
    label: '南向',
    trafficFlow: 380,
    queueLength: 95,
    unit: 'veh/h'
  },
  {
    direction: 'west',
    label: '西向',
    trafficFlow: 410,
    queueLength: 110,
    unit: 'veh/h'
  }
])

const pedestrianStatus = ref({
  waiting: 3,
  requests: [
    { location: '东侧人行道', status: 'waiting', waitTime: 15 },
    { location: '西侧人行道', status: 'waiting', waitTime: 8 },
    { location: '南侧人行道', status: 'requested', waitTime: 0 }
  ]
})

// 策略状态
const currentStrategy = ref({
  name: '工作日白天',
  cycleLength: 120,
  phases: [
    { id: 1, name: '东西直行', greenTime: 30, actualTime: 30 },
    { id: 2, name: '东西左转', greenTime: 25, actualTime: 25 },
    { id: 3, name: '南北直行', greenTime: 30, actualTime: 30 },
    { id: 4, name: '南北左转', greenTime: 25, actualTime: 25 }
  ],
  controlMode: 'adaptive'
})

// 手动干预
const interventions = ref([])

const interventionOptions = [
  { type: 'yellow-flash', label: '临时黄闪', duration: 5 },
  { type: 'all-red', label: '临时全红', duration: 2 },
  { type: 'extend-green', label: '加长当前绿灯', duration: 10, extendTime: 5 },
  { type: 'pedestrian-green', label: '给行人绿灯', duration: 0 }
]

// 定时更新
let updateInterval = null

const updateRealTimeData = () => {
  // 更新相位剩余时间
  if (currentPhase.value.remainingTime > 0) {
    currentPhase.value.remainingTime--
  } else {
    // 切换到下一个相位（模拟）
    const nextPhase = currentStrategy.value.phases.find(p => p.id === currentPhase.value.id + 1) || currentStrategy.value.phases[0]
    currentPhase.value = {
      id: nextPhase.id,
      name: nextPhase.name,
      remainingTime: nextPhase.greenTime,
      totalTime: nextPhase.greenTime
    }
  }

  // 更新车流量和排队长度（模拟随机变化）
  directions.value.forEach(dir => {
    dir.trafficFlow += Math.floor((Math.random() - 0.5) * 20)
    dir.trafficFlow = Math.max(0, dir.trafficFlow)
    dir.queueLength += Math.floor((Math.random() - 0.5) * 5)
    dir.queueLength = Math.max(0, dir.queueLength)
  })

  // 更新干预倒计时
  interventions.value.forEach(intervention => {
    if (intervention.remainingTime > 0) {
      intervention.remainingTime--
    } else if (intervention.remainingTime === 0 && !intervention.completed) {
      intervention.completed = true
      // TODO: 通知后端恢复自动控制
    }
  })
}

const applyIntervention = async (option) => {
  const intervention = {
    id: Date.now(),
    type: option.type,
    label: option.label,
    duration: option.duration,
    remainingTime: option.duration * 60, // 转换为秒
    extendTime: option.extendTime || 0,
    completed: false
  }

  interventions.value.push(intervention)

  // TODO: 调用后端API应用干预
  console.log('应用干预:', intervention)
}

const cancelIntervention = (intervention) => {
  const index = interventions.value.findIndex(i => i.id === intervention.id)
  if (index > -1) {
    interventions.value.splice(index, 1)
    // TODO: 通知后端取消干预
  }
}

const getControlModeLabel = (mode) => {
  const modeMap = {
    'fixed': '定周期',
    'adaptive': '流量自适应',
    'pedestrian': '行人过街触发',
    'bus': '公交优先',
    'yellow-flash': '黄闪',
    'all-red': '全红'
  }
  return modeMap[mode] || mode
}

const getInterventionTypeLabel = (type) => {
  const typeMap = {
    'yellow-flash': '临时黄闪',
    'all-red': '临时全红',
    'extend-green': '加长绿灯',
    'pedestrian-green': '行人绿灯'
  }
  return typeMap[type] || type
}

onMounted(() => {
  updateInterval = setInterval(updateRealTimeData, 1000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<template>
  <div class="monitoring-view">
    <header class="page-header">
      <h1>实时监控 & 手动干预</h1>
      <p>实时查看路口状态并进行手动控制</p>
    </header>

    <div class="monitoring-layout">
      <!-- 左侧：实时数据区 -->
      <section class="realtime-data">
        <h2 class="section-title">实时数据</h2>

        <!-- 当前周期 & 相位 -->
        <div class="phase-card">
          <h3>当前相位</h3>
          <div class="phase-info">
            <div class="phase-name">{{ currentPhase.name }}</div>
            <div class="phase-timer">
              <div class="timer-value">{{ currentPhase.remainingTime }}</div>
              <div class="timer-unit">秒</div>
            </div>
            <div class="phase-progress">
              <div
                class="progress-bar"
                :style="{ width: `${(currentPhase.remainingTime / currentPhase.totalTime) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- 各方向实时数据 -->
        <div class="directions-data">
          <h3>各方向实时数据</h3>
          <div class="direction-cards">
            <div
              v-for="dir in directions"
              :key="dir.direction"
              class="direction-card"
            >
              <div class="direction-label">{{ dir.label }}</div>
              <div class="direction-metrics">
                <div class="metric-item">
                  <span class="metric-label">车流量</span>
                  <span class="metric-value">{{ dir.trafficFlow }}</span>
                  <span class="metric-unit">{{ dir.unit }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">排队长度</span>
                  <span class="metric-value">{{ dir.queueLength }}</span>
                  <span class="metric-unit">米</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 行人状态 -->
        <div class="pedestrian-status">
          <h3>行人等待状态</h3>
          <div class="pedestrian-info">
            <div class="pedestrian-count">
              等待人数：<strong>{{ pedestrianStatus.waiting }}</strong>
            </div>
            <div class="pedestrian-requests">
              <div
                v-for="request in pedestrianStatus.requests"
                :key="request.location"
                class="request-item"
              >
                <span class="request-location">{{ request.location }}</span>
                <span :class="['request-status', request.status]">
                  {{ request.status === 'waiting' ? '等待中' : '已请求' }}
                </span>
                <span v-if="request.waitTime > 0" class="request-time">
                  等待{{ request.waitTime }}秒
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 中间：策略状态区 -->
      <section class="strategy-status">
        <h2 class="section-title">策略状态</h2>

        <div class="strategy-card">
          <h3>当前策略</h3>
          <div class="strategy-name">{{ currentStrategy.name }}</div>
        </div>

        <div class="cycle-info">
          <h3>周期信息</h3>
          <div class="cycle-length">
            <span class="cycle-label">当前周期长度</span>
            <span class="cycle-value">{{ currentStrategy.cycleLength }} 秒</span>
          </div>
        </div>

        <div class="phases-status">
          <h3>各相位实际绿灯时长</h3>
          <div class="phases-list">
            <div
              v-for="phase in currentStrategy.phases"
              :key="phase.id"
              :class="['phase-item', { active: phase.id === currentPhase.id }]"
            >
              <div class="phase-name">{{ phase.name }}</div>
              <div class="phase-times">
                <span class="time-label">计划：</span>
                <span class="time-value">{{ phase.greenTime }}s</span>
                <span class="time-label">实际：</span>
                <span class="time-value actual">{{ phase.actualTime }}s</span>
              </div>
            </div>
          </div>
        </div>

        <div class="control-mode">
          <h3>控制模式</h3>
          <div class="mode-badge">
            {{ getControlModeLabel(currentStrategy.controlMode) }}
          </div>
        </div>
      </section>

      <!-- 右侧：手动干预区 -->
      <section class="manual-intervention">
        <h2 class="section-title">手动干预</h2>

        <div class="intervention-options">
          <button
            v-for="option in interventionOptions"
            :key="option.type"
            class="intervention-btn"
            @click="applyIntervention(option)"
          >
            <span class="btn-label">{{ option.label }}</span>
            <span v-if="option.duration > 0" class="btn-duration">
              {{ option.duration }}分钟
            </span>
          </button>
        </div>

        <div v-if="interventions.length > 0" class="active-interventions">
          <h3>进行中的干预</h3>
          <div class="interventions-list">
            <div
              v-for="intervention in interventions"
              :key="intervention.id"
              class="intervention-item"
            >
              <div class="intervention-info">
                <div class="intervention-label">
                  {{ getInterventionTypeLabel(intervention.type) }}
                </div>
                <div v-if="intervention.remainingTime > 0" class="intervention-countdown">
                  剩余 {{ Math.floor(intervention.remainingTime / 60) }}:{{ String(intervention.remainingTime % 60).padStart(2, '0') }}
                </div>
                <div v-else-if="intervention.completed" class="intervention-status completed">
                  已完成
                </div>
              </div>
              <button
                class="cancel-btn"
                @click="cancelIntervention(intervention)"
                v-if="!intervention.completed"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.monitoring-view {
  padding: 32px 48px;
  min-height: calc(100vh - 80px);
  background: radial-gradient(circle at top, rgba(5, 26, 43, 0.95), rgba(3, 13, 23, 0.96));
  color: #e6f1ff;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #d6ecff;
}

.page-header p {
  color: rgba(214, 232, 255, 0.7);
  font-size: 14px;
}

.monitoring-layout {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
  height: calc(100vh - 200px);
}

section {
  background: rgba(7, 27, 44, 0.7);
  border: 1px solid rgba(88, 178, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  overflow-y: auto;
}

.section-title {
  font-size: 20px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
  color: #58b2ff;
}

/* 实时数据区 */
.phase-card {
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.phase-card h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: rgba(214, 232, 255, 0.9);
}

.phase-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.phase-name {
  font-size: 18px;
  font-weight: 600;
  color: #58b2ff;
}

.phase-timer {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.timer-value {
  font-size: 48px;
  font-weight: 700;
  color: #5be3ff;
}

.timer-unit {
  font-size: 18px;
  color: rgba(214, 232, 255, 0.7);
}

.phase-progress {
  height: 8px;
  background: rgba(88, 178, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #58b2ff, #5be3ff);
  transition: width 1s linear;
}

.directions-data h3,
.pedestrian-status h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: rgba(214, 232, 255, 0.9);
}

.direction-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.direction-card {
  padding: 16px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 10px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.direction-label {
  font-size: 14px;
  font-weight: 600;
  color: #58b2ff;
  margin-bottom: 12px;
}

.direction-metrics {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.metric-label {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.7);
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: #5be3ff;
}

.metric-unit {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}

.pedestrian-status {
  margin-top: 24px;
}

.pedestrian-info {
  padding: 16px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 10px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.pedestrian-count {
  font-size: 16px;
  margin-bottom: 16px;
  color: rgba(214, 232, 255, 0.9);
}

.pedestrian-count strong {
  font-size: 24px;
  color: #5be3ff;
}

.pedestrian-requests {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.request-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(88, 178, 255, 0.05);
  border-radius: 8px;
}

.request-location {
  flex: 1;
  font-size: 14px;
}

.request-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.request-status.waiting {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.request-status.requested {
  background: rgba(67, 194, 58, 0.2);
  color: #67c23a;
}

.request-time {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}

/* 策略状态区 */
.strategy-card {
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.strategy-card h3 {
  font-size: 14px;
  margin-bottom: 8px;
  color: rgba(214, 232, 255, 0.7);
}

.strategy-name {
  font-size: 20px;
  font-weight: 600;
  color: #58b2ff;
}

.cycle-info {
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.cycle-info h3 {
  font-size: 14px;
  margin-bottom: 12px;
  color: rgba(214, 232, 255, 0.7);
}

.cycle-length {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cycle-label {
  font-size: 14px;
  color: rgba(214, 232, 255, 0.7);
}

.cycle-value {
  font-size: 24px;
  font-weight: 600;
  color: #5be3ff;
}

.phases-status h3 {
  font-size: 14px;
  margin-bottom: 16px;
  color: rgba(214, 232, 255, 0.7);
}

.phases-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.phase-item {
  padding: 16px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 10px;
  border: 1px solid rgba(88, 178, 255, 0.1);
  transition: all 0.3s;
}

.phase-item.active {
  background: rgba(88, 178, 255, 0.15);
  border-color: #58b2ff;
}

.phase-item .phase-name {
  font-size: 14px;
  font-weight: 600;
  color: #58b2ff;
  margin-bottom: 8px;
}

.phase-times {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.time-label {
  color: rgba(214, 232, 255, 0.6);
}

.time-value {
  font-weight: 600;
  color: rgba(214, 232, 255, 0.9);
}

.time-value.actual {
  color: #5be3ff;
}

.control-mode {
  margin-top: 24px;
  padding: 20px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.control-mode h3 {
  font-size: 14px;
  margin-bottom: 12px;
  color: rgba(214, 232, 255, 0.7);
}

.mode-badge {
  display: inline-block;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.2), rgba(91, 227, 255, 0.2));
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #58b2ff;
}

/* 手动干预区 */
.intervention-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.intervention-btn {
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  background: rgba(88, 178, 255, 0.1);
  color: #58b2ff;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.intervention-btn:hover {
  background: rgba(88, 178, 255, 0.2);
  border-color: #58b2ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.2);
}

.btn-label {
  font-size: 15px;
  font-weight: 600;
}

.btn-duration {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.7);
}

.active-interventions h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: rgba(214, 232, 255, 0.9);
}

.interventions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.intervention-item {
  padding: 16px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 10px;
  border: 1px solid rgba(88, 178, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.intervention-info {
  flex: 1;
}

.intervention-label {
  font-size: 15px;
  font-weight: 600;
  color: #58b2ff;
  margin-bottom: 6px;
}

.intervention-countdown {
  font-size: 13px;
  color: #5be3ff;
}

.intervention-status.completed {
  font-size: 13px;
  color: rgba(214, 232, 255, 0.6);
}

.cancel-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 77, 79, 0.3);
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background: rgba(255, 77, 79, 0.2);
}
</style>

