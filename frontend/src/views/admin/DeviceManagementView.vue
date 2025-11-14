<script setup>
const devices = [
  {
    id: 'EQ-001',
    name: '高精度数控机床',
    status: '在线',
    health: '良好',
    modal: '振动 / 温度 / 声学',
    location: '华北核心节点',
  },
  {
    id: 'EQ-032',
    name: '智能焊接机器人',
    status: '告警',
    health: '需关注',
    modal: '视觉 / 温度',
    location: '华东边缘节点',
  },
  {
    id: 'EQ-018',
    name: '能源侧传感集群',
    status: '离线',
    health: '维护中',
    modal: '电磁 / 压力',
    location: '华南协同中心',
  },
]

const statusClassMap = {
  在线: 'online',
  告警: 'warning',
  离线: 'offline',
}
</script>

<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1>设备管理</h1>
        <p>统一管理平台已接入的工业设备资产，实时掌握设备状态与健康度。</p>
      </div>
      <button class="action">新增设备</button>
    </header>

    <table class="data-table">
      <thead>
        <tr>
          <th>设备编号</th>
          <th>设备名称</th>
          <th>状态</th>
          <th>健康状况</th>
          <th>覆盖模态</th>
          <th>部署位置</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="device in devices" :key="device.id">
          <td>{{ device.id }}</td>
          <td>{{ device.name }}</td>
          <td>
            <span :class="['badge', statusClassMap[device.status]]">{{ device.status }}</span>
          </td>
          <td>{{ device.health }}</td>
          <td>{{ device.modal }}</td>
          <td>{{ device.location }}</td>
        </tr>
      </tbody>
    </table>
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
</style>

