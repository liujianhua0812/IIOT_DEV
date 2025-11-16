<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1>设备类型管理</h1>
        <p>管理平台支持的设备类型，配置每种设备类型的特有参数。共 {{ deviceTypes.length }} 种设备类型</p>
      </div>
      <button class="action" @click="handleAdd">新增设备类型</button>
    </header>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="device-types-container">
      <div
        v-for="deviceType in deviceTypes"
        :key="deviceType.id"
        class="device-type-card"
      >
        <div class="card-header">
          <div class="type-info">
            <h3>{{ deviceType.name }}</h3>
            <span class="type-code">{{ deviceType.code }}</span>
          </div>
          <div class="card-actions">
            <button class="action-btn edit" @click="handleEdit(deviceType)">编辑</button>
            <button class="action-btn delete" @click="handleDelete(deviceType)">删除</button>
          </div>
        </div>
        <div class="card-body">
          <p class="description">{{ deviceType.description || '暂无描述' }}</p>
          <div class="params-section">
            <h4>类型特有参数：</h4>
            <div v-if="deviceType.parameters && deviceType.parameters.length > 0" class="params-list">
              <div
                v-for="param in deviceType.parameters"
                :key="param.key"
                class="param-item"
              >
                <span class="param-key">{{ param.name }} ({{ param.key }})</span>
                <span class="param-type">{{ getParamTypeLabel(param.type) }}</span>
                <span v-if="param.required" class="param-required">必填</span>
                <span v-else class="param-optional">可选</span>
              </div>
            </div>
            <div v-else class="no-params">暂无特有参数</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingType ? '编辑设备类型' : '新增设备类型'"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入设备类型名称" />
        </el-form-item>
        <el-form-item label="类型代码" prop="code">
          <el-input
            v-model="formData.code"
            placeholder="请输入类型代码（英文，唯一标识）"
            :disabled="!!editingType"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入设备类型描述"
          />
        </el-form-item>
        <el-form-item label="类型特有参数">
          <div class="params-editor">
            <div 
              ref="paramsListRef"
              class="params-list-container"
            >
              <div
                v-for="(param, index) in formData.parameters"
                :key="param._id || param.key || `param-${index}`"
                class="param-editor-item"
                :data-index="index"
              >
                <div class="param-drag-handle">
                  <el-icon><Rank /></el-icon>
                </div>
                <el-input
                  v-model="param.name"
                  placeholder="参数名称"
                  style="width: 200px"
                />
                <el-input
                  v-model="param.key"
                  placeholder="参数键（英文）"
                  style="width: 150px"
                />
                <el-select
                  v-model="param.type"
                  placeholder="参数类型"
                  style="width: 120px"
                >
                  <el-option label="字符串" value="string" />
                  <el-option label="数字" value="number" />
                  <el-option label="布尔值" value="boolean" />
                  <el-option label="日期" value="date" />
                </el-select>
                <el-checkbox v-model="param.required">必填</el-checkbox>
                <div class="param-actions">
                  <el-button
                    v-if="index > 0"
                    type="text"
                    size="small"
                    @click="moveParamUp(index)"
                    title="上移"
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </el-button>
                  <el-button
                    v-if="index < formData.parameters.length - 1"
                    type="text"
                    size="small"
                    @click="moveParamDown(index)"
                    title="下移"
                  >
                    <el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeParam(index)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            <el-button
              type="primary"
              plain
              @click="addParam"
              style="margin-top: 10px"
            >
              添加参数
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Rank, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import {
  fetchDeviceTypes,
  createDeviceType,
  updateDeviceType,
  deleteDeviceType
} from '../../services/api'

const deviceTypes = ref([])
const loading = ref(false)
const error = ref('')
const dialogVisible = ref(false)
const editingType = ref(null)
const formRef = ref(null)
const paramsListRef = ref(null)
let sortableInstance = null

const formData = ref({
  name: '',
  code: '',
  description: '',
  parameters: []
})

const formRules = {
  name: [
    { required: true, message: '请输入设备类型名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入类型代码', trigger: 'blur' },
    { pattern: /^[a-z_][a-z0-9_]*$/, message: '类型代码只能包含小写字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ]
}

const getParamTypeLabel = (type) => {
  const typeMap = {
    string: '字符串',
    number: '数字',
    boolean: '布尔值',
    date: '日期'
  }
  return typeMap[type] || type
}

const loadDeviceTypes = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await fetchDeviceTypes()
    deviceTypes.value = response.data.device_types || []
  } catch (err) {
    error.value = '加载设备类型数据失败，请稍后重试'
    console.error('加载设备类型失败:', err)
  } finally {
    loading.value = false
  }
}


const handleEdit = (deviceType) => {
  editingType.value = deviceType
  // 确保参数按 sort_order 排序，并为每个参数生成唯一ID
  const sortedParams = deviceType.parameters 
    ? [...deviceType.parameters].sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
        .map(p => ({
          ...p,
          _id: p._id || `param_${p.key || Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        }))
    : []
  formData.value = {
    name: deviceType.name,
    code: deviceType.code,
    description: deviceType.description || '',
    parameters: sortedParams
  }
  dialogVisible.value = true
  // 初始化拖拽排序
  nextTick(() => {
    initSortable()
  })
}

const handleAdd = () => {
  editingType.value = null
  formData.value = {
    name: '',
    code: '',
    description: '',
    parameters: []
  }
  dialogVisible.value = true
  // 初始化拖拽排序
  nextTick(() => {
    initSortable()
  })
}

const handleDelete = async (deviceType) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除设备类型"${deviceType.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteDeviceType(deviceType.id)
    ElMessage.success('删除成功')
    loadDeviceTypes()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败，请稍后重试')
      console.error('删除设备类型失败:', err)
    }
  }
}

const addParam = () => {
  const maxSortOrder = formData.value.parameters.length > 0
    ? Math.max(...formData.value.parameters.map(p => p.sort_order || 0))
    : -1
  // 为每个新参数生成唯一ID
  const uniqueId = `param_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  formData.value.parameters.push({
    _id: uniqueId, // 用于 Vue key 的唯一标识
    name: '',
    key: '',
    type: 'string',
    required: false,
    sort_order: maxSortOrder + 1
  })
}

const removeParam = (index) => {
  formData.value.parameters.splice(index, 1)
  // 重新分配排序值
  updateSortOrders()
}

const moveParamUp = (index) => {
  if (index > 0) {
    const temp = formData.value.parameters[index]
    formData.value.parameters[index] = formData.value.parameters[index - 1]
    formData.value.parameters[index - 1] = temp
    updateSortOrders()
  }
}

const moveParamDown = (index) => {
  if (index < formData.value.parameters.length - 1) {
    const temp = formData.value.parameters[index]
    formData.value.parameters[index] = formData.value.parameters[index + 1]
    formData.value.parameters[index + 1] = temp
    updateSortOrders()
  }
}

const updateSortOrders = () => {
  // 确保使用响应式更新
  formData.value.parameters.forEach((param, index) => {
    if (param.sort_order !== index) {
      param.sort_order = index
    }
  })
  // 强制触发响应式更新
  formData.value.parameters = [...formData.value.parameters]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 确保每个参数都有 sort_order
    const parameters = formData.value.parameters
      .filter(p => p.name && p.key)
      .map((p, index) => ({
        ...p,
        sort_order: p.sort_order !== undefined ? p.sort_order : index
      }))
    
    const submitData = {
      name: formData.value.name,
      code: formData.value.code,
      description: formData.value.description,
      parameters: parameters
    }
    
    if (editingType.value) {
      await updateDeviceType(editingType.value.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createDeviceType(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadDeviceTypes()
  } catch (err) {
    if (err !== false) {
      ElMessage.error(editingType.value ? '更新失败，请稍后重试' : '创建失败，请稍后重试')
      console.error('提交失败:', err)
    }
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  editingType.value = null
  // 销毁拖拽实例
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
}

const initSortable = () => {
  // 如果已存在实例，先销毁
  if (sortableInstance) {
    sortableInstance.destroy()
  }
  
  if (!paramsListRef.value) {
    return
  }
  
  sortableInstance = Sortable.create(paramsListRef.value, {
    handle: '.param-drag-handle',
    animation: 150,
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    dragClass: 'sortable-drag',
    onEnd: (evt) => {
      const { oldIndex, newIndex } = evt
      if (oldIndex !== newIndex && oldIndex !== null && newIndex !== null) {
        // 创建新数组以避免响应式问题
        const newParams = [...formData.value.parameters]
        const movedItem = newParams.splice(oldIndex, 1)[0]
        newParams.splice(newIndex, 0, movedItem)
        
        // 更新数组
        formData.value.parameters = newParams
        
        // 更新排序值
        nextTick(() => {
          updateSortOrders()
        })
      }
    }
  })
}

// 监听对话框打开，初始化拖拽
watch(dialogVisible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      initSortable()
    })
  } else {
    // 对话框关闭时销毁拖拽实例
    if (sortableInstance) {
      sortableInstance.destroy()
      sortableInstance = null
    }
  }
})

onMounted(() => {
  loadDeviceTypes()
})
</script>

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

.loading,
.error {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.device-types-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.device-type-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.device-type-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.type-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.type-code {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.25s ease;
}

.action-btn.edit {
  background: #ecf5ff;
  color: #409eff;
  border-color: #b3d8ff;
}

.action-btn.edit:hover {
  background: #409eff;
  color: #ffffff;
}

.action-btn.delete {
  background: #fef0f0;
  color: #f56c6c;
  border-color: #fbc4c4;
}

.action-btn.delete:hover {
  background: #f56c6c;
  color: #ffffff;
}

.card-body {
  color: #606266;
}

.description {
  margin: 0 0 16px 0;
  color: #909399;
  font-size: 14px;
}

.params-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
}

.param-key {
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.param-type {
  color: #909399;
  font-size: 12px;
}

.param-required {
  color: #f56c6c;
  font-size: 12px;
  font-weight: 500;
}

.param-optional {
  color: #909399;
  font-size: 12px;
}

.no-params {
  color: #c0c4cc;
  font-size: 13px;
  font-style: italic;
}

.params-editor {
  width: 100%;
}

.params-list-container {
  margin-bottom: 10px;
}

.param-editor-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.param-editor-item:hover {
  background: #ecf5ff;
}

.param-drag-handle {
  cursor: move;
  color: #909399;
  display: flex;
  align-items: center;
  padding: 0 5px;
  user-select: none;
}

.param-drag-handle:hover {
  color: #409eff;
}

.sortable-ghost {
  opacity: 0.4;
  background: #f0f0f0;
}

.sortable-chosen {
  cursor: move;
}

.sortable-drag {
  opacity: 0.8;
}

.param-actions {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-left: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

