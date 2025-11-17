<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>DDoS检测 · 系统状态</h1>
      <p>概览系统运行健康度与关键性能指标，辅助判定 DDoS 风险。</p>
    </header>

    <div class="top-actions">
      <button class="btn btn-grad btn-accent back-btn" @click="goBack">返回</button>
    </div>

    <div class="alert-box">
      <div
        v-for="a in alerts"
        :key="a.id"
        class="alert"
        :class="`alert-${a.type}`"
      >
        <span class="close" @click="dismissAlert(a.id)">&times;</span>
        <h4>{{ a.title }}</h4>
        <p>{{ a.message }}</p>
        <small>{{ a.time }}</small>
      </div>
    </div>

    <section class="grid status-grid">
      <article class="card panel">
        <h2>📊 系统状态</h2>
        <ul class="stats">
          <li><span class="label">运行时间</span><span class="value">{{ formattedUptime }}</span></li>
          <li><span class="label">总处理流量序列</span><span class="value">{{ totalTraffic }} 条</span></li>
          <li><span class="label">良性流量记录</span><span class="value success">{{ benignTraffic }} 条</span></li>
          <li><span class="label">攻击流量记录</span><span class="value danger">{{ attackTraffic }} 条</span></li>
          <li><span class="label">活跃流量记录</span><span class="value">{{ activeFlows }} 条</span></li>
          <li class="mode">
            <span class="label">检测模式</span>
            <span class="value">
              <span class="dot" :class="{ on: detectEnabled }"></span>
              {{ detectEnabled ? '已启用' : '未启用' }}
            </span>
          </li>
        </ul>
      </article>

      <article class="card panel">
        <h2>🛡️ 防御控制</h2>
        <div class="actions">
          <button class="action btn btn-grad btn-primary" @click="configureBasic">🔧 配置初级防御</button>
          <button class="action btn btn-grad btn-success" @click="enableDetect">✅ 启用检测模式</button>
          <button class="action btn btn-grad btn-warning" @click="disableDetect">⏸️ 禁用检测模式</button>
          <!-- <button class="action btn btn-grad btn-danger" @click="clearBlacklist">🗑️ 清空黑名单</button> -->
        </div>
        <p class="hint">先配置初始化防御，再启用检测模式</p>
      </article>

      <article class="card panel">
        <h2>🚫 黑名单 ({{ blacklist.length }})</h2>
        <div v-if="blacklist.length === 0" class="empty">暂无黑名单 IP</div>
        <ul v-else class="blacklist">
          <li v-for="ip in blacklist" :key="ip">{{ ip }}</li>
        </ul>
      </article>
    </section>

    <!-- 设备传输数据组件按要求移除 -->

    <section class="logs-section">
      <article class="card logs">
        <h2>🪵 系统日志（最近100行）</h2>
        <pre class="log-area">{{ logsText }}</pre>
        <p class="refresh-info">自动刷新，每3秒更新一次</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
function goBack() {
  router.push({ name: 'security' })
}

// 使用后端返回的 uptime_minutes 直接展示
const uptimeMinutes = ref(0)

onMounted(() => {
  boot()
})
onUnmounted(() => {
  // 仅清理轮询定时器数组
  clearAllIntervals()
})

// formattedUptime 直接显示 uptime_minutes（无需前端再计算秒数）
const formattedUptime = computed(() => {
  // 保留1位小数
  return `${uptimeMinutes.value.toFixed(1)} 分钟`
})

const totalTraffic = ref(0)
const benignTraffic = ref(0)
const attackTraffic = ref(0)
const activeFlows = ref(0)
const detectEnabled = ref(false)
const blacklist = ref([])

const logsText = ref('等待日志...')

// Alerts
const alerts = ref([])
function showAlert(type, title, message, duration = 5000) {
  const id = `${Date.now()}_${Math.random().toString(36).slice(2)}`
  alerts.value.push({ id, type, title, message, time: new Date().toLocaleString() })
  setTimeout(() => {
    const idx = alerts.value.findIndex(a => a.id === id)
    if (idx !== -1) alerts.value.splice(idx, 1)
  }, duration)
}
function dismissAlert(id) {
  const idx = alerts.value.findIndex(a => a.id === id)
  if (idx !== -1) alerts.value.splice(idx, 1)
}
function handleAlert(data) {
  let type = 'danger'
  let title = '告警'
  if (data?.type === 'primary_defense') {
    title = '⚠️ 初级防御触发'
    type = 'warning'
  } else if (data?.type === 'ddos_detected') {
    title = '🚨 DDoS攻击检测'
    type = 'danger'
  } else if (data?.type === 'blacklist_add') {
    title = '🚫 黑名单更新'
    type = 'warning'
  } else {
    type = 'info'
  }
  showAlert(type, title, data?.message ?? '收到系统告警', 10000)
}

// API + Polling
const API_BASE = 'http://localhost:12345/api'
const pollers = []
function clearAllIntervals() {
  while (pollers.length) {
    const id = pollers.pop()
    clearInterval(id)
  }
}
async function updateStatus() {
  try {
    const res = await fetch(`${API_BASE}/status`)
    const data = await res.json()
    const uptimeMin = Number(data.uptime_minutes ?? 0)
    // 直接使用后端返回的分钟数
    uptimeMinutes.value = uptimeMin
    totalTraffic.value = Number(data.total_processed ?? 0)
    benignTraffic.value = Number(data.benign_flows ?? 0)
    attackTraffic.value = Number(data.ddos_flows ?? 0)
    activeFlows.value = Number(data.active_flows ?? 0)
    detectEnabled.value = Boolean(data.detection_enabled)
  } catch (e) {}
}
async function updateLogs() {
  try {
    const res = await fetch(`${API_BASE}/logs?lines=100`)
    const data = await res.json()
    if (data?.logs !== undefined) {
      logsText.value = String(data.logs)
    }
  } catch (e) {}
}
async function updateBlacklist() {
  try {
    const res = await fetch(`${API_BASE}/blacklist`)
    const data = await res.json()
    blacklist.value = Array.isArray(data?.blacklist) ? data.blacklist : []
  } catch (e) {}
}

// Actions
async function enableDetect() {
  try {
    const res = await fetch(`${API_BASE}/detection_mode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable: true }),
    })
    const data = await res.json()
    if (data?.status === 'success') {
      showAlert('success', '✅ 检测模式已启用', '系统正在监控网络流量')
      await updateStatus()
    } else {
      showAlert('danger', '❌ 操作失败', data?.message ?? '启用检测模式失败')
    }
  } catch (e) {
    showAlert('danger', '❌ 请求失败', e.message ?? String(e))
  }
}
async function disableDetect() {
  try {
    const res = await fetch(`${API_BASE}/detection_mode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable: false }),
    })
    const data = await res.json()
    if (data?.status === 'success') {
      showAlert('warning', '⏸️ 检测模式已禁用', '系统已停止监控')
      await updateStatus()
    } else {
      showAlert('danger', '❌ 操作失败', data?.message ?? '禁用检测模式失败')
    }
  } catch (e) {
    showAlert('danger', '❌ 请求失败', e.message ?? String(e))
  }
}
async function clearBlacklist() {
  try {
    const res = await fetch(`${API_BASE}/blacklist/clear`, { method: 'POST' })
    const data = await res.json()
    if (data?.status === 'success') {
      showAlert('success', '🗑️ 黑名单已清空', '所有IP已从黑名单移除')
      await updateBlacklist()
    } else {
      showAlert('danger', '❌ 操作失败', data?.message ?? '清空黑名单失败')
    }
  } catch (e) {
    showAlert('danger', '❌ 请求失败', e.message ?? String(e))
  }
}
async function configureBasic() {
  showAlert('info', '⏳ 正在配置', '初级防御配置中，请稍候...')
  try {
    const res = await fetch(`${API_BASE}/primary_defense`, { method: 'POST' })
    const data = await res.json()
    if (data?.status === 'success') {
      showAlert('success', '✅ 配置完成', data?.message ?? '已完成初始化配置')
    } else if (data?.status === 'partial') {
      showAlert('warning', '⚠️ 部分完成', data?.message ?? '部分步骤失败，请检查')
    } else {
      showAlert('danger', '❌ 配置失败', data?.message ?? '请稍后重试')
    }
  } catch (e) {
    showAlert('danger', '❌ 请求失败', e.message ?? String(e))
  }
}

// Boot & Socket
async function boot() {
  updateStatus()
  updateLogs()
  updateBlacklist()
  pollers.push(setInterval(updateStatus, 2000))
  pollers.push(setInterval(updateLogs, 3000))
  pollers.push(setInterval(updateBlacklist, 5000))
  if (!(window && window.io)) {
    await loadSocketIo()
  }
  if (window && window.io) {
    const socket = window.io('http://localhost:12345')
    socket.on('connect', () => {
      showAlert('info', '系统连接', '已成功连接到DDoS控制器')
    })
    socket.on('disconnect', () => {
      showAlert('warning', '系统断开', '与DDoS控制器的连接已断开')
    })
    socket.on('alert', (data) => {
      handleAlert(data)
    })
  }
}
function loadSocketIo() {
  return new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://cdn.socket.io/4.5.4/socket.io.min.js'
    script.async = true
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.head.appendChild(script)
  })
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

.grid {
  margin-top: 32px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.card {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
}

.card h2,
.card h3 {
  font-size: 22px;
  margin-bottom: 14px;
}

.card p {
  color: rgba(214, 232, 255, 0.75);
  line-height: 1.7;
}

.radar {
  background: linear-gradient(135deg, rgba(14, 54, 88, 0.95), rgba(4, 28, 48, 0.9));
  border: 1px solid rgba(73, 197, 255, 0.28);
}

.alert-box {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 420px;
  z-index: 1000;
}
.alert {
  background: rgba(255, 255, 255, 0.98);
  color: #333;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 10px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
  border-left: 4px solid #5aaaff;
}
.alert h4 {
  margin-bottom: 4px;
  font-size: 15px;
}
.alert p {
  margin: 0;
  color: #555;
  font-size: 13px;
}
.alert .close {
  float: right;
  cursor: pointer;
  font-size: 18px;
  color: #888;
  line-height: 1;
}
.alert-info { border-color: #5aaaff; }
.alert-success { border-color: #4cd07d; }
.alert-warning { border-color: #f39c12; background: #fff8e6; }
.alert-danger { border-color: #e74c3c; background: #fff0f0; }

.status-grid .panel h2 {
  margin-bottom: 16px;
}
.stats {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stats li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(128, 214, 255, 0.08);
}
.stats .label {
  color: rgba(214, 232, 255, 0.86);
}
.stats .value {
  color: #e6f1ff;
  font-weight: 600;
}
.stats .value.success {
  color: #5ee07a;
}
.stats .value.danger {
  color: #ff6b6b;
}
.stats .mode .value {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f45b69;
  box-shadow: 0 0 8px rgba(244, 91, 105, 0.6);
}
.dot.on {
  background: #4cd07d;
  box-shadow: 0 0 8px rgba(76, 208, 125, 0.6);
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.actions .el-button.action,
.actions .action.btn {
  width: 100%;
  justify-content: center;
  letter-spacing: 0.6px;
  font-weight: 600;
}
.actions .action.btn {
  padding: 12px 16px;
  border-radius: 999px;
}
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
.btn-success {
  background-image: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}
.btn-warning {
  background-image: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
.btn-danger {
  background-image: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
}
.hint {
  margin-top: 10px;
  color: rgba(214, 232, 255, 0.6);
  font-size: 13px;
}

.empty {
  color: rgba(214, 232, 255, 0.6);
  font-size: 14px;
}
.blacklist {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
}
.blacklist li {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(128, 214, 255, 0.12);
  padding: 8px 10px;
  border-radius: 10px;
}

.logs-section {
  margin-top: 24px;
}
.logs h2 {
  margin-bottom: 12px;
}
.log-area {
  background: #0d1117;
  color: #9cdcfe;
  border-radius: 12px;
  padding: 14px;
  min-height: 220px;
  max-height: 380px;
  overflow: auto;
  line-height: 1.5;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;
  border: 1px solid rgba(88, 178, 255, 0.12);
}

.refresh-info {
  margin-top: 10px;
  color: rgba(214, 232, 255, 0.6);
  font-size: 13px;
  text-align: center;
  font-style: italic;
}
</style>


