<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>DDoS检测 · 设备监控</h1>
      <p>面向边缘与核心设备的状态监控与异常流量追踪。</p>
    </header>

    <div class="top-actions">
      <button class="btn btn-grad btn-accent back-btn" @click="goBack">返回</button>
    </div>

    <section class="monitor">
      <article class="card board">
        <header class="board-header">
          <h2>📡 设备传输数据</h2>
        </header>

        <div class="board-grid">
          <aside class="device-pane">
            <div class="pane-title">设备列表</div>
            <ul class="device-list">
              <li
                v-for="d in devices"
                :key="d.ip"
                :class="['device-item', { active: d.ip === selectedIp }]"
                @click="selectDevice(d.ip)"
              >
                <span class="status-dot" :class="d.status"></span>
                <span class="device-name">{{ d.name || '设备' }}</span>
                <span class="device-ip">{{ d.ip }}</span>
                <span class="badge" :class="d.status">{{ statusText(d.status) }}</span>
              </li>
            </ul>
          </aside>

          <section class="data-pane">
            <pre class="sensor-data">{{ sensorData }}</pre>
            <p class="refresh-info">自动刷新，每5秒更新一次</p>
          </section>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const API_BASE = 'http://47.98.175.223:12345/api'
const router = useRouter()
function goBack() {
  router.push({ name: 'security' })
}

const devices = ref([
  { ip: '10.0.1.1', name: '设备A', status: 'online' },
  { ip: '10.0.2.2', name: '设备B', status: 'warning' },
  { ip: '10.0.3.3', name: '设备C', status: 'offline' },
])
const selectedIp = ref(devices.value[0]?.ip || '')
const sensorData = ref('等待数据...')

let pollers = []
onMounted(() => {
  boot()
})
onUnmounted(() => {
  while (pollers.length) {
    clearInterval(pollers.pop())
  }
})

function selectDevice(ip) {
  selectedIp.value = ip
  updateSensorData()
}

function statusText(status) {
  if (status === true || status === 'online') return '在线'
  if (status === 'warning') return '告警'
  return '离线'
}

async function updateDevices() {
  try {
    const res = await fetch(`${API_BASE}/devices`)
    const data = await res.json()
    if (Array.isArray(data?.devices) && data.devices.length) {
      // 允许后端返回 { ip, name, online } 或 { ip, name, status }
      devices.value = data.devices.map(d => {
        const status = typeof d.status !== 'undefined'
          ? d.status
          : (d.online ? 'online' : 'offline')
        return { name: d.name, ip: d.ip, status }
      })
      if (!devices.value.find(d => d.ip === selectedIp.value)) {
        selectedIp.value = devices.value[0]?.ip || ''
      }
    }
  } catch (e) {
    // 保留示例数据
  }
}

async function updateSensorData() {
  try {
    const q = selectedIp.value ? `&device=${encodeURIComponent(selectedIp.value)}` : ''
    const res = await fetch(`${API_BASE}/sensor_data?lines=100${q}`)
    const data = await res.json()
    if (data?.data !== undefined) {
      sensorData.value = String(data.data)
    } else if (data?.error) {
      sensorData.value = `错误: ${data.error}`
    }
  } catch (e) {
    // ignore
  }
}

function boot() {
  updateDevices()
  updateSensorData()
  pollers.push(setInterval(updateDevices, 5000))
  pollers.push(setInterval(updateSensorData, 5000))
}
</script>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(4, 21, 38, 0.96), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
  position: relative;
}

.page-header h1 {
  font-size: 34px;
  margin-bottom: 12px;
  letter-spacing: 1.4px;
}

.page-header p {
  max-width: 640px;
  color: rgba(214, 232, 255, 0.74);
  line-height: 1.8;
}

.top-actions {
  position: absolute;
  top: 20px;
  right: 64px;
  z-index: 10;
}
.back-btn {
  padding: 8px 14px;
  border-radius: 999px;
}

.monitor {
  margin-top: 24px;
}
.card.board {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 0;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
}
.board-header {
  padding: 18px 22px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.18);
}
.board-header h2 {
  font-size: 20px;
}
.board-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 18px;
  padding: 18px 18px 20px;
}

.device-pane {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(128, 214, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
}
.pane-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #e6f1ff;
}
.device-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.device-item {
  display: grid;
  grid-template-columns: 16px 1fr auto auto;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.12s ease, transform 0.12s ease;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(128, 214, 255, 0.08);
}
.device-item:hover { transform: translateY(-1px); }
.device-item.active {
  background: rgba(128, 214, 255, 0.12);
  border-color: rgba(128, 214, 255, 0.28);
}
.device-name { color: #e6f1ff; }
.device-ip {
  color: rgba(214, 232, 255, 0.65);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.4);
}
.status-dot.online { background: #4cd07d; box-shadow: 0 0 8px rgba(76, 208, 125, 0.6); }
.status-dot.warning { background: #f39c12; box-shadow: 0 0 8px rgba(243, 156, 18, 0.6); }
.status-dot.offline { background: #e74c3c; box-shadow: 0 0 8px rgba(231, 76, 60, 0.6); }

.badge {
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid transparent;
}
.badge.online {
  background: rgba(76, 208, 125, 0.15);
  border-color: rgba(76, 208, 125, 0.35);
  color: #7be0a7;
}
.badge.warning {
  background: rgba(243, 156, 18, 0.15);
  border-color: rgba(243, 156, 18, 0.35);
  color: #f3c776;
}
.badge.offline {
  background: rgba(231, 76, 60, 0.15);
  border-color: rgba(231, 76, 60, 0.35);
  color: #ff9f9f;
}

.data-pane {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(128, 214, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
}
.sensor-data {
  background: rgba(13, 17, 23, 0.9);
  color: #c9d1d9;
  border-radius: 12px;
  padding: 14px;
  min-height: 340px;
  max-height: 460px;
  overflow: auto;
  line-height: 1.5;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  border: 1px solid rgba(88, 178, 255, 0.12);
}
.refresh-info {
  margin-top: 10px;
  color: rgba(214, 232, 255, 0.6);
  font-size: 13px;
  text-align: center;
  font-style: italic;
}

@media (max-width: 920px) {
  .board-grid { grid-template-columns: 1fr; }
}

/* 按钮渐变样式（与系统状态页保持一致） */
.btn-grad {
  border: 0;
  color: #fff;
  transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.2s ease;
}
.btn-grad:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
  filter: brightness(1.03);
}
.btn-primary {
  background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.btn-accent {
  background-image: linear-gradient(135deg, #49c5ff 0%, #3aa0ff 100%);
}
</style>


