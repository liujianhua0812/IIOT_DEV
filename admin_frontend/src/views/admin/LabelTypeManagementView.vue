<script setup>
import { onMounted, reactive, ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  fetchLabelTypes,
  createLabelType,
  updateLabelType,
  deleteLabelType,
  fetchApplications,
} from '@/services/api'

const loading = ref(false)
const errorMessage = ref('')
const labelTypes = ref([])
const applications = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const formMode = ref('create')
const formRef = ref(null)
const fileList = ref([])

const defaultImage = './data/labels/label.png'
const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10060'
const uploadAction = `${apiBaseURL}/api/laptop-label-types/upload`
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

const formData = reactive({
  id: null,
  name: '',
  label_type: '',
  length_mm: null,
  width_mm: null,
  image_path: '',
  application_id: null,
  description: '',
})

const updateFileList = () => {
  if (formData.image_path) {
    fileList.value = [
      {
        name: formData.name || '标签图片',
        url: resolveImageSrc(formData.image_path, formData.id),
      },
    ]
  } else {
    fileList.value = []
  }
}

const rules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  label_type: [{ required: true, message: '请输入标签类型', trigger: 'blur' }],
  image_path: [{ required: true, message: '请上传标签图片', trigger: 'change' }],
}

const applicationOptions = computed(() => [
  { label: '未绑定', value: null },
  ...applications.value.map((app) => ({ label: app.name, value: app.id })),
])

const applicationMap = computed(() => {
  const map = {}
  applications.value.forEach((app) => {
    map[app.id] = app.name
  })
  return map
})

const resolveImageSrc = (path, id = null) => {
  const finalPath = path || defaultImage
  if (!finalPath) return ''
  if (/^https?:\/\//i.test(finalPath) || finalPath.startsWith('data:')) {
    return finalPath
  }
  if (id) {
    return `${apiBaseURL}/api/laptop-label-types/${id}/image`
  }
  if (finalPath.startsWith('/')) {
    return `${apiBaseURL}${finalPath}`
  }
  return `${apiBaseURL}/${finalPath.replace(/^\.\//, '')}`
}

const getImageSrc = (row) => {
  if (!row) return ''
  const path = row.image_path || defaultImage
  if (!path) return ''
  return resolveImageSrc(path, row.id)
}

const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.label_type = ''
  formData.length_mm = null
  formData.width_mm = null
  formData.image_path = ''
  formData.application_id = null
  formData.description = ''
  updateFileList()
}

const loadLabelTypes = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await fetchLabelTypes()
    labelTypes.value = response.data.label_types || []
    currentPage.value = 1
  } catch (error) {
    console.error(error)
    errorMessage.value = '加载标签类型失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const paginatedLabelTypes = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return labelTypes.value.slice(start, start + pageSize.value)
})

const loadApplications = async () => {
  try {
    const response = await fetchApplications()
    applications.value = response.data.applications || []
  } catch (error) {
    console.error(error)
    ElMessage.error('加载应用列表失败')
  }
}

const handleCreate = () => {
  formMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  formMode.value = 'edit'
  formData.id = row.id
  formData.name = row.name
  formData.label_type = row.label_type
  formData.length_mm = row.length_mm
  formData.width_mm = row.width_mm
  formData.image_path = row.image_path || defaultImage
  formData.application_id = row.application_id
  formData.description = row.description
  updateFileList()
  dialogVisible.value = true
}

const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    try {
      const payload = {
        name: formData.name,
        label_type: formData.label_type,
        length_mm: formData.length_mm,
        width_mm: formData.width_mm,
        image_path: formData.image_path,
        application_id: formData.application_id,
        description: formData.description,
      }
      if (formMode.value === 'create') {
        await createLabelType(payload)
        ElMessage.success('创建成功')
      } else {
        await updateLabelType(formData.id, payload)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      await loadLabelTypes()
    } catch (error) {
      console.error(error)
      ElMessage.error(formMode.value === 'create' ? '创建失败' : '更新失败')
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除标签「${row.name}」吗？`, '提示', {
    type: 'warning',
  })
    .then(async () => {
      try {
        await deleteLabelType(row.id)
        ElMessage.success('删除成功')
        await loadLabelTypes()
      } catch (error) {
        console.error(error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

const beforeUpload = (file) => {
  const isAllowed = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isAllowed) {
    ElMessage.error('仅支持上传 PNG/JPG/GIF/SVG/WebP 图片')
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
  }
  return isAllowed && isLt5M
}

const handleUploadSuccess = (response) => {
  if (response?.path) {
    formData.image_path = response.path
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error('上传响应异常')
  }
}

const handleUploadError = () => {
  ElMessage.error('图片上传失败，请重试')
}

const handleUploadRemove = () => {
  formData.image_path = ''
}

onMounted(() => {
  loadLabelTypes()
  loadApplications()
})

watch(
  () => formData.image_path,
  () => {
    updateFileList()
  }
)
updateFileList()
</script>

<template>
  <div class="label-type-management panel">
    <header class="panel-header">
      <div>
        <h1>标签类型管理</h1>
        <p>维护笔记本贴标类型及其尺寸、图片等信息。共 {{ labelTypes.length }} 种标签类型</p>
      </div>
      <button class="action" @click="handleCreate">新增标签类型</button>
    </header>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="errorMessage" class="state error">{{ errorMessage }}</div>
    <div v-else class="table-wrapper">
      <el-table :data="paginatedLabelTypes" border style="width: 100%">
        <el-table-column type="index" width="60" label="序号" />
        <el-table-column prop="name" label="标签名称" min-width="160" />
        <el-table-column prop="label_type" label="类型标识" min-width="140" />
        <el-table-column label="尺寸 (mm)" min-width="160">
          <template #default="{ row }">
            <span>{{ row.length_mm ?? '--' }} × {{ row.width_mm ?? '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="图片" min-width="160">
          <template #default="{ row }">
            <el-image
              v-if="getImageSrc(row)"
              :src="getImageSrc(row)"
              style="width: 80px; height: 80px;"
              fit="contain"
              :preview-src-list="[getImageSrc(row)]"
              :preview-teleported="true"
              :initial-index="0"
            />
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column label="所属应用" min-width="160">
          <template #default="{ row }">
            {{ row.application_id ? applicationMap[row.application_id] || `#${row.application_id}` : '未绑定' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="240" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper" v-if="labelTypes.length > pageSize">
        <el-pagination
          background
          layout="prev, pager, next, jumper"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="labelTypes.length"
          @current-change="(val) => (currentPage = val)"
        />
      </div>
    </div>

    <el-dialog :title="formMode === 'create' ? '新增标签类型' : '编辑标签类型'" v-model="dialogVisible" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="formData.name" placeholder="例如：Intel Core Ultra" />
        </el-form-item>
        <el-form-item label="标签类型" prop="label_type">
          <el-input v-model="formData.label_type" placeholder="例如：CPU_PERFORMANCE" />
        </el-form-item>
        <el-form-item label="标签尺寸">
          <div class="size-inputs">
            <el-input-number v-model="formData.length_mm" :min="0" :precision="2" :step="0.5" placeholder="长度" />
            <span class="size-sep">×</span>
            <el-input-number v-model="formData.width_mm" :min="0" :precision="2" :step="0.5" placeholder="宽度" />
          </div>
        </el-form-item>
        <el-form-item label="标签图片" prop="image_path">
          <el-upload
            class="image-uploader"
            :action="uploadAction"
            name="file"
            list-type="picture-card"
            :headers="uploadHeaders"
            :file-list="fileList"
            :limit="1"
            :auto-upload="true"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :on-remove="handleUploadRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 png/jpg/gif/webp/svg，大小不超过 5MB</div>
        </el-form-item>
        <el-form-item label="所属应用">
          <el-select v-model="formData.application_id" placeholder="选择应用，可为空">
            <el-option v-for="option in applicationOptions" :key="option.label + option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="描述此标签适用场景" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">保存</el-button>
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

.label-type-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.state {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.state.error {
  color: #f56c6c;
}

.table-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
}

.size-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.size-sep {
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.image-uploader :global(.el-upload) {
  border: 1px dashed #d9d9d9;
}

.upload-tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
</style>

