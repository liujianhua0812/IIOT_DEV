<template>
  <div class="topology-management">
    <div class="panel">
      <header class="panel-header">
        <div>
          <h1>网络拓扑管理</h1>
          <p>管理各应用的设备网络拓扑连接关系</p>
        </div>
      </header>

      <!-- 应用选择 -->
      <div class="filter-section">
        <el-select
          v-model="selectedApplicationId"
          placeholder="请选择应用"
          style="width: 300px"
          @change="handleApplicationChange"
        >
          <el-option
            v-for="app in applications"
            :key="app.id"
            :label="`${app.name} (${app.english_name || 'N/A'})`"
            :value="app.id"
          />
        </el-select>
        <el-button
          v-if="selectedApplicationId"
          type="primary"
          @click="handleAddConnection"
          style="margin-left: 16px"
        >
          添加连接
        </el-button>
      </div>

      <!-- 拓扑信息展示 -->
      <div v-if="selectedApplicationId && topologyData" class="topology-content">
        <div class="info-section">
          <h3>应用信息</h3>
          <p><strong>应用名称：</strong>{{ topologyData.application.name }}</p>
          <p><strong>英文名：</strong>{{ topologyData.application.english_name || 'N/A' }}</p>
          <p><strong>设备数量：</strong>{{ topologyData.devices.length }}</p>
          <p><strong>连接数量：</strong>{{ topologyData.topology.length }}</p>
        </div>

        <!-- 设备列表 -->
        <div class="devices-section">
          <h3>设备列表</h3>
          <el-table :data="topologyData.devices" border style="width: 100%">
            <el-table-column prop="code" label="设备编码" width="150" />
            <el-table-column prop="name" label="设备名称" />
            <el-table-column prop="type" label="设备类型" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '在线' ? 'success' : 'info'">
                  {{ row.status || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 拓扑连接列表 -->
        <div class="topology-section">
          <h3>网络拓扑连接</h3>
          <el-table :data="topologyData.topology" border style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="源设备" width="150">
              <template #default="{ row }">
                {{ getDeviceName(row.source_device_code) }}
                <br />
                <small style="color: #909399">{{ row.source_device_code }}</small>
              </template>
            </el-table-column>
            <el-table-column label="目标设备" width="150">
              <template #default="{ row }">
                {{ getDeviceName(row.target_device_code) }}
                <br />
                <small style="color: #909399">{{ row.target_device_code }}</small>
              </template>
            </el-table-column>
            <el-table-column prop="connection_type" label="连接类型" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditConnection(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteConnection(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="selectedApplicationId && !loading" class="empty-state">
        <p>该应用暂无设备或拓扑数据</p>
      </div>
    </div>

    <!-- 添加/编辑连接对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑连接' : '添加连接'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="源设备" prop="source_device_code">
          <el-select
            v-model="formData.source_device_code"
            placeholder="请选择源设备"
            style="width: 100%"
            :disabled="isEditMode"
          >
            <el-option
              v-for="device in topologyData?.devices || []"
              :key="device.code"
              :label="`${device.name} (${device.code})`"
              :value="device.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标设备" prop="target_device_code">
          <el-select
            v-model="formData.target_device_code"
            placeholder="请选择目标设备"
            style="width: 100%"
            :disabled="isEditMode"
          >
            <el-option
              v-for="device in topologyData?.devices || []"
              :key="device.code"
              :label="`${device.name} (${device.code})`"
              :value="device.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="连接类型" prop="connection_type">
          <el-select
            v-model="formData.connection_type"
            placeholder="请选择连接类型"
            style="width: 100%"
          >
            <el-option label="网络连接" value="network" />
            <el-option label="控制连接" value="control" />
            <el-option label="数据连接" value="data" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入连接描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  fetchApplications,
  fetchApplicationTopology,
  createTopologyConnection,
  updateTopologyConnection,
  deleteTopologyConnection
} from '../../services/api'

const applications = ref([])
const selectedApplicationId = ref(null)
const topologyData = ref(null)
const loading = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref(null)
const currentTopologyId = ref(null)

const formData = ref({
  source_device_code: '',
  target_device_code: '',
  connection_type: 'network',
  description: ''
})

const formRules = {
  source_device_code: [
    { required: true, message: '请选择源设备', trigger: 'change' }
  ],
  target_device_code: [
    { required: true, message: '请选择目标设备', trigger: 'change' }
  ],
  connection_type: [
    { required: true, message: '请选择连接类型', trigger: 'change' }
  ]
}

const loadApplications = async () => {
  try {
    const response = await fetchApplications()
    applications.value = response.data.applications || []
  } catch (err) {
    ElMessage.error('加载应用列表失败')
    console.error('加载应用列表失败:', err)
  }
}

const loadTopology = async () => {
  if (!selectedApplicationId.value) {
    topologyData.value = null
    return
  }

  loading.value = true
  try {
    const response = await fetchApplicationTopology(selectedApplicationId.value)
    topologyData.value = response.data
  } catch (err) {
    ElMessage.error('加载拓扑数据失败')
    console.error('加载拓扑数据失败:', err)
    topologyData.value = null
  } finally {
    loading.value = false
  }
}

const handleApplicationChange = () => {
  loadTopology()
}

const getDeviceName = (deviceCode) => {
  if (!topologyData.value) return deviceCode
  const device = topologyData.value.devices.find(d => d.code === deviceCode)
  return device ? device.name : deviceCode
}

const handleAddConnection = () => {
  isEditMode.value = false
  currentTopologyId.value = null
  formData.value = {
    source_device_code: '',
    target_device_code: '',
    connection_type: 'network',
    description: ''
  }
  dialogVisible.value = true
}

const handleEditConnection = (row) => {
  isEditMode.value = true
  currentTopologyId.value = row.id
  formData.value = {
    source_device_code: row.source_device_code,
    target_device_code: row.target_device_code,
    connection_type: row.connection_type || 'network',
    description: row.description || ''
  }
  dialogVisible.value = true
}

const handleDeleteConnection = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除连接 "${getDeviceName(row.source_device_code)} -> ${getDeviceName(row.target_device_code)}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteTopologyConnection(row.id)
    ElMessage.success('删除成功')
    loadTopology()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除连接失败:', err)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (isEditMode.value) {
      // 更新连接
      await updateTopologyConnection(currentTopologyId.value, {
        connection_type: formData.value.connection_type,
        description: formData.value.description
      })
      ElMessage.success('更新成功')
    } else {
      // 创建连接
      if (formData.value.source_device_code === formData.value.target_device_code) {
        ElMessage.error('源设备和目标设备不能相同')
        return
      }

      await createTopologyConnection(selectedApplicationId.value, formData.value)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadTopology()
  } catch (err) {
    if (err !== false) {
      const errorMessage = err.response?.data?.error || err.message || '操作失败'
      ElMessage.error(errorMessage)
      console.error('操作失败:', err)
    }
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  formData.value = {
    source_device_code: '',
    target_device_code: '',
    connection_type: 'network',
    description: ''
  }
  isEditMode.value = false
  currentTopologyId.value = null
}

onMounted(() => {
  loadApplications()
})
</script>

<style scoped>
.topology-management {
  padding: 24px;
  background: #f5f5f5;
  min-height: calc(100vh - 64px);
}

.panel {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-header {
  padding: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.panel-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.panel-header p {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

.filter-section {
  padding: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.topology-content {
  padding: 24px;
}

.info-section {
  margin-bottom: 32px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 4px;
}

.info-section h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.info-section p {
  margin: 8px 0;
  color: #595959;
}

.devices-section,
.topology-section {
  margin-bottom: 32px;
}

.devices-section h3,
.topology-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.empty-state {
  padding: 80px 24px;
  text-align: center;
  color: #8c8c8c;
}
</style>

