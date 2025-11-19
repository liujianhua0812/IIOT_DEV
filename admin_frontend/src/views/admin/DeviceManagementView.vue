<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDevices, fetchDevice, createDevice, updateDevice, fetchDeviceTypes } from '../../services/api'

const devices = ref([])
const loading = ref(false)
const error = ref('')
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const statusFilter = ref('')

// 对话框相关
const dialogVisible = ref(false)
const isEditMode = ref(false)
const deviceDetail = ref(null)
const deviceTypes = ref([])
const formRef = ref(null)
const formData = ref({
  name: '',
  code: '',
  device_type_id: null,
  application_id: null,
  position_x: null,
  position_y: null,
  serial_number: '',
  longitude: null,
  latitude: null,
  status: '',
  health_status: '',
  description: '',
  parameters: {}
})

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

const loadDeviceTypes = async () => {
  try {
    const response = await fetchDeviceTypes()
    deviceTypes.value = response.data.device_types || []
  } catch (err) {
    console.error('加载设备类型失败:', err)
  }
}

// 监听设备类型变化，初始化参数（用于新增设备时）
watch(() => formData.value.device_type_id, async (newTypeId) => {
  if (newTypeId && isEditMode.value && !deviceDetail.value?.id) {
    // 只在新增模式下（没有 deviceDetail.id）才初始化参数
    const selectedType = deviceTypes.value.find(t => t.id === newTypeId)
    if (selectedType) {
      // 更新 deviceDetail 以便显示参数
      deviceDetail.value = {
        device_type: selectedType
      }
      
      // 初始化参数值
      const parameters = {}
      if (selectedType.parameters) {
        for (const paramDef of selectedType.parameters) {
          if (paramDef.type === 'number') {
            parameters[paramDef.key] = null
          } else if (paramDef.type === 'boolean') {
            parameters[paramDef.key] = false
          } else {
            parameters[paramDef.key] = paramDef.default_value || ''
          }
        }
      }
      formData.value.parameters = parameters
    }
  }
})

const handleView = async (device) => {
  try {
    const response = await fetchDevice(device.id)
    deviceDetail.value = response.data.device
    isEditMode.value = false
    
    // 填充表单数据
    const parameters = {}
    // 首先初始化所有设备类型参数（使用默认值或空值）
    if (deviceDetail.value.device_type?.parameters) {
      for (const paramDef of deviceDetail.value.device_type.parameters) {
        if (deviceDetail.value.parameters && paramDef.key in deviceDetail.value.parameters) {
          // 如果参数值存在，转换类型
          const value = deviceDetail.value.parameters[paramDef.key]
          if (paramDef.type === 'number' && value !== null && value !== undefined) {
            parameters[paramDef.key] = Number(value)
          } else if (paramDef.type === 'boolean' && value !== null && value !== undefined) {
            parameters[paramDef.key] = value === 'true' || value === true || value === 1
          } else {
            parameters[paramDef.key] = value
          }
        } else {
          // 如果参数值不存在，使用默认值或空值
          if (paramDef.type === 'number') {
            parameters[paramDef.key] = null
          } else if (paramDef.type === 'boolean') {
            parameters[paramDef.key] = false
          } else {
            parameters[paramDef.key] = paramDef.default_value || ''
          }
        }
      }
    }
    
    formData.value = {
      name: deviceDetail.value.name || '',
      code: deviceDetail.value.code || '',
      device_type_id: deviceDetail.value.device_type_id || null,
      application_id: deviceDetail.value.application_id || null,
      position_x: deviceDetail.value.position_x || null,
      position_y: deviceDetail.value.position_y || null,
      serial_number: deviceDetail.value.serial_number || '',
      longitude: deviceDetail.value.longitude || null,
      latitude: deviceDetail.value.latitude || null,
      status: deviceDetail.value.status || '',
      health_status: deviceDetail.value.health_status || '',
      description: deviceDetail.value.description || '',
      parameters: parameters
    }
    
    dialogVisible.value = true
  } catch (err) {
    ElMessage.error('获取设备详情失败')
    console.error('获取设备详情失败:', err)
  }
}

const handleAdd = async () => {
  // 重置表单数据
  formData.value = {
    name: '',
    code: '',
    device_type_id: null,
    application_id: null,
    position_x: null,
    position_y: null,
    serial_number: '',
    longitude: null,
    latitude: null,
    status: '在线',
    health_status: '良好',
    description: '',
    parameters: {}
  }
  
  // 创建一个虚拟的 deviceDetail 对象，用于显示设备类型参数
  deviceDetail.value = {
    device_type: null
  }
  
  isEditMode.value = true
  dialogVisible.value = true
  
  // 确保设备类型列表已加载
  if (deviceTypes.value.length === 0) {
    await loadDeviceTypes()
  }
}

const handleEdit = async (device) => {
  await handleView(device)
  isEditMode.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 清理参数值：保留所有有效值（包括 false、0、空字符串）
    const cleanedParameters = {}
    for (const [key, value] of Object.entries(formData.value.parameters)) {
      // 只排除 null 和 undefined，保留其他所有值（包括 false、0、空字符串）
      if (value !== null && value !== undefined) {
        cleanedParameters[key] = value
      }
    }
    
    const submitData = {
      name: formData.value.name,
      code: formData.value.code,
      device_type_id: formData.value.device_type_id,
      application_id: formData.value.application_id,
      position_x: formData.value.position_x,
      position_y: formData.value.position_y,
      serial_number: formData.value.serial_number,
      longitude: formData.value.longitude,
      latitude: formData.value.latitude,
      status: formData.value.status,
      health_status: formData.value.health_status,
      description: formData.value.description,
      parameters: cleanedParameters
    }
    
    console.log('提交的设备数据:', submitData)
    
    let response
    if (isEditMode.value && deviceDetail.value) {
      // 更新现有设备
      response = await updateDevice(deviceDetail.value.id, submitData)
      
      // 更新成功后，刷新设备列表和当前设备详情
      await loadDevices()
      
      // 如果更新后的设备在当前页，更新列表中的对应设备数据
      const updatedDevice = response.data.device
      const deviceIndex = devices.value.findIndex(d => d.id === updatedDevice.id)
      if (deviceIndex !== -1) {
        // 更新列表中的设备数据，确保显示最新状态
        devices.value[deviceIndex] = {
          ...devices.value[deviceIndex],
          status: updatedDevice.status,
          health_status: updatedDevice.health_status,
          name: updatedDevice.name,
          code: updatedDevice.code,
          description: updatedDevice.description,
          // 更新其他可能变化的字段
          ...updatedDevice
        }
      }
      
      ElMessage.success('更新成功')
    } else {
      // 创建新设备
      response = await createDevice(submitData)
      
      // 创建成功后，刷新设备列表
      await loadDevices()
      
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
  } catch (err) {
    if (err !== false) {
      const errorMessage = err.response?.data?.error || err.message || (isEditMode.value ? '更新失败，请稍后重试' : '创建失败，请稍后重试')
      ElMessage.error(errorMessage)
      console.error(isEditMode.value ? '更新设备失败:' : '创建设备失败:', err)
      console.error('错误详情:', err.response?.data)
    }
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  deviceDetail.value = null
  isEditMode.value = false
}

const getParamTypeInput = (param) => {
  if (!param) return 'text'
  switch (param.type) {
    case 'number':
      return 'number'
    case 'boolean':
      return 'checkbox'
    case 'date':
      return 'date'
    default:
      return 'text'
  }
}

onMounted(() => {
  loadDevices()
  loadDeviceTypes()
})
</script>

<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1>设备管理</h1>
        <p>统一管理平台已接入的工业设备资产，实时掌握设备状态与健康度。共 {{ total }} 台设备</p>
      </div>
      <button class="action" @click="handleAdd">新增设备</button>
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
              <button class="action-btn" @click="handleView(device)">查看</button>
              <button class="action-btn edit" @click="handleEdit(device)" style="margin-left: 8px">编辑</button>
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

    <!-- 查看/编辑设备对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑设备' : '查看设备'"
      width="900px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        label-width="120px"
        :disabled="!isEditMode"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备名称" prop="name" :rules="[{ required: true, message: '请输入设备名称', trigger: 'blur' }]">
              <el-input v-model="formData.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备编码" prop="code" :rules="[{ required: true, message: '请输入设备编码', trigger: 'blur' }]">
              <el-input v-model="formData.code" placeholder="请输入设备编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备类型" prop="device_type_id">
              <el-select v-model="formData.device_type_id" placeholder="请选择设备类型" style="width: 100%">
                <el-option
                  v-for="dt in deviceTypes"
                  :key="dt.id"
                  :label="dt.name"
                  :value="dt.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="序列号" prop="serial_number">
              <el-input v-model="formData.serial_number" placeholder="请输入序列号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入设备描述"
          />
        </el-form-item>

        <!-- 位置信息 -->
        <el-divider content-position="left">位置信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="显示X坐标" prop="position_x">
              <el-input-number v-model="formData.position_x" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示Y坐标" prop="position_y">
              <el-input-number v-model="formData.position_y" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="经度" prop="longitude">
              <el-input-number v-model="formData.longitude" :precision="6" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="纬度" prop="latitude">
              <el-input-number v-model="formData.latitude" :precision="6" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 状态信息 -->
        <el-divider content-position="left">状态信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="在线" value="在线" />
                <el-option label="离线" value="离线" />
                <el-option label="告警" value="告警" />
                <el-option label="维护中" value="维护中" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="健康状况" prop="health_status">
              <el-select v-model="formData.health_status" placeholder="请选择健康状况" style="width: 100%">
                <el-option label="良好" value="良好" />
                <el-option label="需关注" value="需关注" />
                <el-option label="警告" value="警告" />
                <el-option label="故障" value="故障" />
                <el-option label="维护中" value="维护中" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 设备类型特有参数 -->
        <el-divider content-position="left" v-if="deviceDetail?.device_type?.parameters?.length > 0">
          设备类型特有参数
        </el-divider>
        <template v-if="deviceDetail?.device_type?.parameters">
          <el-form-item
            v-for="param in deviceDetail.device_type.parameters"
            :key="param.key"
            :label="param.name"
            :prop="`parameters.${param.key}`"
            :rules="param.required && isEditMode ? [{ required: true, message: `请输入${param.name}`, trigger: 'blur' }] : []"
          >
            <template v-if="isEditMode">
              <el-input
                v-if="param.type === 'string'"
                v-model="formData.parameters[param.key]"
                :placeholder="`请输入${param.name}`"
              />
              <el-input-number
                v-else-if="param.type === 'number'"
                v-model="formData.parameters[param.key]"
                :placeholder="`请输入${param.name}`"
                style="width: 100%"
              />
              <el-switch
                v-else-if="param.type === 'boolean'"
                v-model="formData.parameters[param.key]"
              />
              <el-date-picker
                v-else-if="param.type === 'date'"
                v-model="formData.parameters[param.key]"
                type="date"
                :placeholder="`请选择${param.name}`"
                style="width: 100%"
              />
            </template>
            <template v-else>
              <span v-if="param.type === 'boolean'" style="color: #606266">
                {{ formData.parameters[param.key] !== undefined && formData.parameters[param.key] !== null ? (formData.parameters[param.key] ? '是' : '否') : '-' }}
              </span>
              <span v-else style="color: #606266">
                {{ formData.parameters[param.key] !== undefined && formData.parameters[param.key] !== null ? formData.parameters[param.key] : '-' }}
              </span>
            </template>
            <span v-if="param.required" style="color: #f56c6c; margin-left: 8px">*</span>
          </el-form-item>
        </template>

        <!-- 只读信息 -->
        <el-divider content-position="left" v-if="!isEditMode">其他信息</el-divider>
        <template v-if="!isEditMode && deviceDetail">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="最后心跳">
                <span>{{ formatDate(deviceDetail.last_heartbeat) }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="创建时间">
                <span>{{ formatDate(deviceDetail.created_at) }}</span>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="更新时间">
            <span>{{ formatDate(deviceDetail.updated_at) }}</span>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button v-if="isEditMode" type="primary" @click="handleSubmit">保存</el-button>
          <el-button v-else type="primary" @click="isEditMode = true">编辑</el-button>
        </span>
      </template>
    </el-dialog>
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

.action-btn.edit {
  background: #f0f9ff;
  color: #409eff;
  border-color: #b3d8ff;
}

.action-btn.edit:hover {
  background: #409eff;
  color: #ffffff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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

