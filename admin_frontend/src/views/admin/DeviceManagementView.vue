<script setup>
import { ref, onMounted, computed } from 'vue'
import { fetchDevices } from '../../services/api'

const devices = ref([])
const loading = ref(false)
const error = ref('')
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const statusFilter = ref('')

const statusClassMap = {
  '在线': 'online',
  '运行中': 'online',
  '正常': 'online',
  '告警': 'warning',
  '警告': 'warning',
  '异常': 'warning',
  '离线': 'offline',
  '故障': 'offline',
  '维护中': 'offline',
}

const healthStatusMap = {
  '良好': 'good',
  '正常': 'good',
  '需关注': 'warning',
  '警告': 'warning',
  '维护中': 'maintenance',
  '故障': 'error',
}

const loadDevices = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const response = await fetchDevices(params)
    devices.value = response.data.devices || []
    total.value = response.data.total || 0
  } catch (err) {
    error.value = '加载设备数据失败，请稍后重试'
    console.error('加载设备失败:', err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadDevices()
}

const handleStatusFilter = () => {
  page.value = 1
  loadDevices()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getStatusText = (status) => {
  return status || '未知'
}

const getHealthStatusText = (health) => {
  return health || '-'
}

onMounted(() => {
  loadDevices()
})
</script>

<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1>设备管理</h1>
        <p>统一管理平台已接入的工业设备资产，实时掌握设备状态与健康度。共 {{ total }} 台设备</p>
      </div>
      <button class="action">新增设备</button>
    </header>

    <div class="filters">
      <div class="filter-group">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索设备名称或编码..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
      <div class="filter-group">
        <select v-model="statusFilter" class="status-select" @change="handleStatusFilter">
          <option value="">全部状态</option>
          <option value="在线">在线</option>
          <option value="运行中">运行中</option>
          <option value="告警">告警</option>
          <option value="离线">离线</option>
          <option value="维护中">维护中</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="devices.length === 0" class="empty">暂无设备数据</div>
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>设备编号</th>
            <th>设备名称</th>
            <th>设备类型</th>
            <th>状态</th>
            <th>健康状况</th>
            <th>IP地址</th>
            <th>最后心跳</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="device in devices" :key="device.id">
            <td>{{ device.code }}</td>
            <td>{{ device.name }}</td>
            <td>{{ device.type }}</td>
            <td>
              <span :class="['badge', statusClassMap[device.status] || 'default']">
                {{ getStatusText(device.status) }}
              </span>
            </td>
            <td>
              <span :class="['health-badge', healthStatusMap[device.health_status] || 'default']">
                {{ getHealthStatusText(device.health_status) }}
              </span>
            </td>
            <td>{{ device.ip_address || '-' }}</td>
            <td>{{ formatDate(device.last_heartbeat) }}</td>
            <td>
              <button class="action-btn">查看</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="total > pageSize">
        <button
          class="page-btn"
          :disabled="page === 1"
          @click="page--; loadDevices()"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ page }} 页，共 {{ Math.ceil(total / pageSize) }} 页
        </span>
        <button
          class="page-btn"
          :disabled="page >= Math.ceil(total / pageSize)"
          @click="page++; loadDevices()"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px 36px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #303133;
  font-weight: 600;
}

.panel-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.action {
  padding: 10px 24px;
  border-radius: 6px;
  border: none;
  background: #409eff;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.action:hover {
  background: #66b1ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.data-table th,
.data-table td {
  padding: 16px 18px;
  text-align: left;
  border-bottom: 1px solid #e4e7ed;
  color: #606266;
}

.data-table thead th {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.data-table tbody tr:hover {
  background: #f5f7fa;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
  font-weight: 500;
}

.badge.online {
  background: #f0f9ff;
  color: #67c23a;
  border: 1px solid #b3e19d;
}

.badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.badge.offline {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.badge.default {
  background: #f5f7fa;
  color: #909399;
  border: 1px solid #dcdfe6;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  width: 300px;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
}

.search-btn {
  padding: 8px 16px;
  background: #409eff;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.search-btn:hover {
  background: #66b1ff;
}

.status-select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.status-select:focus {
  outline: none;
  border-color: #409eff;
}

.loading,
.error,
.empty {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.table-container {
  overflow-x: auto;
}

.health-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
  font-weight: 500;
}

.health-badge.good {
  background: #f0f9ff;
  color: #67c23a;
  border: 1px solid #b3e19d;
}

.health-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.health-badge.maintenance {
  background: #f4f4f5;
  color: #909399;
  border: 1px solid #dcdfe6;
}

.health-badge.error {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.health-badge.default {
  background: #f5f7fa;
  color: #909399;
  border: 1px solid #dcdfe6;
}

.action-btn {
  padding: 6px 12px;
  background: #ecf5ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.action-btn:hover {
  background: #409eff;
  color: #ffffff;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px;
}

.page-btn {
  padding: 8px 16px;
  background: #ffffff;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #606266;
  font-size: 14px;
}
</style>

