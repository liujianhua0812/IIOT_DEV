<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchDevices, fetchDevice, createDevice, updateDevice, fetchDeviceTypes, saveDeviceIcon } from '../../services/api'
import CoordinatePicker from '../../components/CoordinatePicker.vue'

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
const showCoordinatePicker = ref(false)
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

// 图标显示设置（仅摄像头设备）
const iconRotation = ref(0)
const iconFlipHorizontal = ref(false)
const iconFlipVertical = ref(false)

// 计算图标变换样式
const iconTransformStyle = computed(() => {
  const transforms = []
  if (iconRotation.value !== 0) {
    transforms.push(`rotate(${iconRotation.value}deg)`)
  }
  if (iconFlipHorizontal.value) {
    transforms.push('scaleX(-1)')
  }
  if (iconFlipVertical.value) {
    transforms.push('scaleY(-1)')
  }
  return {
    transform: transforms.length > 0 ? transforms.join(' ') : 'none'
  }
})

// 图标预览容器样式
const iconPreviewStyle = computed(() => ({
  width: '100px',
  height: '100px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  border: '2px dashed #dcdfe6',
  borderRadius: '8px',
  backgroundColor: '#f5f7fa',
  position: 'relative'
}))

// 获取原始 SVG 内容（根据摄像头类型）
const getOriginalSvgContent = (isCheckpoint = false) => {
  if (isCheckpoint) {
    // 球型摄像头（卡口）- 绿色圆形图标
    return `<svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
  <path d="M521.728 777.216c176.128 0 319.488-147.968 319.488-329.216 0-181.76-143.36-329.216-319.488-329.216S202.24 266.752 202.24 448c0 181.76 143.36 329.216 319.488 329.216z m0-601.6c144.896 0 262.656 122.368 262.656 272.384 0 150.016-117.76 272.384-262.656 272.384-144.896 0-262.656-122.368-262.656-272.384 0-150.016 117.76-272.384 262.656-272.384z m0 0" fill="#67C23A"/>
  <path d="M791.552 715.776c-13.824-5.632-29.696 0-36.352 12.8-7.168 13.312-2.56 29.696 9.728 37.376 19.456 10.24 24.064 18.432 24.576 19.968-1.536 18.432-94.72 61.952-267.776 61.952-170.496 0-266.24-44.032-267.776-61.952 0-1.536 4.608-9.216 23.552-19.456 13.312-7.68 17.92-24.576 10.752-38.4-7.168-13.312-24.064-18.944-37.888-11.776-44.032 23.552-53.248 50.688-53.248 69.632 0 81.92 168.448 119.296 324.608 119.296 156.672 0 324.608-37.376 324.608-119.296 0.512-18.432-9.216-46.08-54.784-70.144zM521.728 602.624c55.296 0 106.496-29.184 133.632-77.312 27.648-47.616 27.648-106.496 0-154.624-27.648-47.616-78.848-77.312-133.632-77.312-85.504 0-154.624 69.12-154.624 154.624s69.12 154.624 154.624 154.624zM468.48 321.536c34.816 0 62.976 28.16 62.976 62.976s-28.16 62.976-62.976 62.976-62.976-28.16-62.976-62.976 28.16-62.976 62.976-62.976z m0 0" fill="#67C23A"/>
</svg>`
  } else {
    // 监控摄像头（电警等）- 黄色摄像头图标
    return `<svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
  <path d="M954.066 439.7a181.176 181.176 0 0 1-49.844 64.146 25.936 25.936 0 0 1 5.917 30.043l-87.854 188.377a25.985 25.985 0 0 1-34.531 12.566l-74.657-34.81a77.974 77.974 0 0 1-88.605 16.023l-149.2-69.564-50.517 101.011a77.534 77.534 0 0 1-69.729 43.083H223.391v25.982a78.036 78.036 0 0 1-77.952 77.943h-51.97a25.982 25.982 0 0 1-25.984-25.98V608.707a25.983 25.983 0 0 1 25.983-25.982h51.969a78.076 78.076 0 0 1 73.485 51.964h87.941l27.067-54.118L200.593 518.4c-64.927-30.273-93.118-107.718-62.841-172.637l65.89-141.284c30.277-64.919 107.731-93.1 172.655-62.835l565.2 263.523a25.985 25.985 0 0 1 12.569 34.533zM145.439 634.687h-25.985v207.85h25.983a26.012 26.012 0 0 0 25.985-25.982V660.669a26.012 26.012 0 0 0-25.983-25.982z m640.727 42.071l65.894-141.282-2.421-1.127a182 182 0 0 1-59.26 10.429L739.067 654.8z m-463.246 9.89h-99.529v51.962h131.655a25.845 25.845 0 0 0 23.246-14.36l49.884-99.742-47.128-21.973-34.887 69.752a25.984 25.984 0 0 1-23.241 14.361zM217.795 297.083l-32.944 70.641a78.03 78.03 0 0 0 37.7 103.581L646.455 668.95a25.972 25.972 0 0 0 34.53-12.566l55.683-119.4a184.083 184.083 0 0 1-24.326-9.311z m136.539-108.344a78.041 78.041 0 0 0-103.593 37.7l-10.981 23.548 494.544 230.584a130.038 130.038 0 0 0 159.336-40.378z m266.985 411.155l-94.2-43.921a25.982 25.982 0 1 1 21.966-47.094l94.2 43.921a25.982 25.982 0 1 1-21.966 47.094z m-271.626-129.32a25.982 25.982 0 1 1 25.984-25.981 25.983 25.983 0 0 1-25.984 25.981z m-94.184-43.926a25.982 25.982 0 1 1 25.984-25.982 25.984 25.984 0 0 1-25.984 25.982z" fill="#E6A23C"/>
</svg>`
  }
}

// 生成最终 SVG（已应用所有变换）
const generateFinalSvg = (rotationAngle = 0, flipHorizontal = false, flipVertical = false) => {
  const cameraName = formData.value.name || ''
  const isCheckpoint = cameraName.includes('卡口')
  
  // 获取原始 SVG 内容
  const originalSvgContent = getOriginalSvgContent(isCheckpoint)
  
  // 构建 transform 字符串
  const transforms = []
  const centerX = 512
  const centerY = 512
  
  // 应用翻转变换
  if (flipHorizontal || flipVertical) {
    transforms.push(`translate(-${centerX}, -${centerY})`)
    if (flipHorizontal && flipVertical) {
      transforms.push('scale(-1, -1)')
    } else if (flipHorizontal) {
      transforms.push('scaleX(-1)')
    } else if (flipVertical) {
      transforms.push('scaleY(-1)')
    }
    transforms.push(`translate(${centerX}, ${centerY})`)
  }
  
  // 应用旋转变换（在翻转之后）
  if (rotationAngle !== 0 && rotationAngle !== null && rotationAngle !== undefined) {
    transforms.push(`rotate(${rotationAngle} ${centerX} ${centerY})`)
  }
  
  // 提取 SVG 内部内容
  let svgInnerContent = originalSvgContent
  svgInnerContent = svgInnerContent.replace(/<svg[^>]*>\s*/i, '')
  svgInnerContent = svgInnerContent.replace(/\s*<\/svg>\s*$/i, '')
  svgInnerContent = svgInnerContent.trim()
  
  // 如果不需要变换，直接返回原始 SVG
  if (transforms.length === 0) {
    return originalSvgContent
  }
  
  // 创建包含 transform 的新 SVG
  const transformAttr = transforms.length > 0 ? ` transform="${transforms.join(' ')}"` : ''
  const finalSvg = `<svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="1024" height="1024"><g${transformAttr}>${svgInnerContent}</g></svg>`
  
  return finalSvg
}

// 获取摄像头图标路径（用于预览，使用内联 SVG 数据 URL）
const getCameraIconSrc = () => {
  const cameraName = formData.value.name || ''
  const isCheckpoint = cameraName.includes('卡口')
  const svgContent = getOriginalSvgContent(isCheckpoint)
  return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgContent)))
}

// 更新图标预览（当参数改变时）
const updateIconPreview = () => {
  // 更新设备参数
  if (formData.value.parameters) {
    formData.value.parameters.icon_rotation_angle = iconRotation.value
    formData.value.parameters.icon_flip_horizontal = iconFlipHorizontal.value
    formData.value.parameters.icon_flip_vertical = iconFlipVertical.value
  }
}

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
      
      // 如果是摄像头设备，重置图标显示设置
      if (selectedType.code === 'camera') {
        iconRotation.value = parameters.icon_rotation_angle || parameters.rotation_angle || 0
        iconFlipHorizontal.value = parameters.icon_flip_horizontal || parameters.flip_horizontal || false
        iconFlipVertical.value = parameters.icon_flip_vertical || parameters.flip_vertical || false
      } else {
        // 重置为非摄像头设备的默认值
        iconRotation.value = 0
        iconFlipHorizontal.value = false
        iconFlipVertical.value = false
      }
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
    
    // 加载所有其他参数（包括自定义的图标显示设置参数）
    // 这些参数可能在设备类型定义中（如果后端自动创建了），也可能不在
    // 我们确保所有参数都被加载，并且图标显示设置参数被正确转换类型
    if (deviceDetail.value.parameters) {
      for (const [key, value] of Object.entries(deviceDetail.value.parameters)) {
        // 检查参数是否已经在 parameters 中（来自设备类型定义的处理）
        if (!(key in parameters)) {
          // 如果参数不在设备类型定义中，也加载它（如图标显示设置）
          const isInDeviceTypeParams = deviceDetail.value.device_type?.parameters?.some(
            param => param.key === key
          )
          if (!isInDeviceTypeParams) {
            // 处理自定义参数的值类型转换
            if (key === 'icon_rotation_angle' || key === 'rotation_angle') {
              parameters[key] = value !== null && value !== undefined && value !== '' ? Number(value) : 0
            } else if (key === 'icon_flip_horizontal' || key === 'flip_horizontal') {
              parameters[key] = value === 'true' || value === true || value === 1 || value === '1'
            } else if (key === 'icon_flip_vertical' || key === 'flip_vertical') {
              parameters[key] = value === 'true' || value === true || value === 1 || value === '1'
            } else {
              parameters[key] = value
            }
          }
        } else {
          // 如果参数已经在 parameters 中（来自设备类型定义的处理），需要检查是否为图标显示设置参数并转换类型
          if (key === 'icon_rotation_angle' || key === 'rotation_angle') {
            // 确保旋转角度是数字
            parameters[key] = parameters[key] !== null && parameters[key] !== undefined && parameters[key] !== '' 
              ? Number(parameters[key]) || 0 
              : 0
          } else if (key === 'icon_flip_horizontal' || key === 'flip_horizontal') {
            // 确保水平翻转是布尔值
            const val = parameters[key]
            parameters[key] = val === 'true' || val === true || val === 1 || val === '1'
          } else if (key === 'icon_flip_vertical' || key === 'flip_vertical') {
            // 确保垂直翻转是布尔值
            const val = parameters[key]
            parameters[key] = val === 'true' || val === true || val === 1 || val === '1'
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
    
    // 加载图标显示设置（如果是摄像头设备）
    console.log('检查设备类型:', {
      deviceDetail: deviceDetail.value,
      deviceType: deviceDetail.value.device_type,
      deviceTypeCode: deviceDetail.value.device_type?.code,
      allParameters: parameters
    })
    
    if (deviceDetail.value.device_type?.code === 'camera') {
      // 从 parameters 中读取图标显示设置，支持多种键名
      const rotationValue = parameters.icon_rotation_angle || parameters.rotation_angle
      const flipHorizontalValue = parameters.icon_flip_horizontal !== undefined ? parameters.icon_flip_horizontal : 
                                   (parameters.flip_horizontal !== undefined ? parameters.flip_horizontal : undefined)
      const flipVerticalValue = parameters.icon_flip_vertical !== undefined ? parameters.icon_flip_vertical :
                                (parameters.flip_vertical !== undefined ? parameters.flip_vertical : undefined)
      
      // 转换旋转角度（确保是数字）
      if (rotationValue !== null && rotationValue !== undefined && rotationValue !== '') {
        iconRotation.value = Number(rotationValue) || 0
      } else {
        iconRotation.value = 0
      }
      
      // 转换水平翻转（确保是布尔值）
      if (flipHorizontalValue !== null && flipHorizontalValue !== undefined && flipHorizontalValue !== '') {
        iconFlipHorizontal.value = flipHorizontalValue === 'true' || flipHorizontalValue === true || flipHorizontalValue === 1 || flipHorizontalValue === '1'
      } else {
        iconFlipHorizontal.value = false
      }
      
      // 转换垂直翻转（确保是布尔值）
      if (flipVerticalValue !== null && flipVerticalValue !== undefined && flipVerticalValue !== '') {
        iconFlipVertical.value = flipVerticalValue === 'true' || flipVerticalValue === true || flipVerticalValue === 1 || flipVerticalValue === '1'
      } else {
        iconFlipVertical.value = false
      }
      
      // 调试输出
      console.log('加载图标显示设置:', {
        deviceTypeCode: deviceDetail.value.device_type?.code,
        rotationValue,
        flipHorizontalValue,
        flipVerticalValue,
        iconRotation: iconRotation.value,
        iconFlipHorizontal: iconFlipHorizontal.value,
        iconFlipVertical: iconFlipVertical.value,
        allParameters: parameters,
        deviceParameters: deviceDetail.value.parameters,
        parametersKeys: Object.keys(parameters)
      })
    } else {
      // 重置为非摄像头设备的默认值
      console.log('设备不是摄像头，重置图标显示设置:', {
        deviceTypeCode: deviceDetail.value.device_type?.code,
        deviceType: deviceDetail.value.device_type
      })
      iconRotation.value = 0
      iconFlipHorizontal.value = false
      iconFlipVertical.value = false
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
  
  // 重置图标显示设置
  iconRotation.value = 0
  iconFlipHorizontal.value = false
  iconFlipVertical.value = false
  
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
    
    // 如果是摄像头设备，确保图标显示设置被保存到参数中
    if (deviceDetail.value?.device_type?.code === 'camera') {
      formData.value.parameters.icon_rotation_angle = iconRotation.value
      formData.value.parameters.icon_flip_horizontal = iconFlipHorizontal.value
      formData.value.parameters.icon_flip_vertical = iconFlipVertical.value
    }
    
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
    let deviceId = null
    
    if (isEditMode.value && deviceDetail.value && deviceDetail.value.id) {
      // 更新现有设备
      deviceId = deviceDetail.value.id
      response = await updateDevice(deviceId, submitData)
      
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
      deviceId = response.data.device.id
      
      // 创建成功后，刷新设备列表
      await loadDevices()
      
      ElMessage.success('创建成功')
    }
    
    // 如果是摄像头设备且有图标显示设置，保存生成的 SVG 文件
    if (deviceId && deviceDetail.value?.device_type?.code === 'camera' && submitData.code) {
      try {
        const cameraName = formData.value.name || ''
        const isCheckpoint = cameraName.includes('卡口')
        
        // 生成最终的 SVG（已应用所有变换）
        const finalSvg = generateFinalSvg(iconRotation.value, iconFlipHorizontal.value, iconFlipVertical.value)
        
        // 如果有变换，保存 SVG 文件
        if (iconRotation.value !== 0 || iconFlipHorizontal.value || iconFlipVertical.value) {
          await saveDeviceIcon(deviceId, finalSvg)
          console.log('设备图标 SVG 保存成功:', submitData.code)
        }
      } catch (iconError) {
        console.error('保存设备图标 SVG 失败:', iconError)
        // 不阻止保存流程，只记录错误
      }
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

const openCoordinatePicker = () => {
  showCoordinatePicker.value = true
}

const handleCoordinateSelected = (coordinates) => {
  formData.value.longitude = coordinates.longitude
  formData.value.latitude = coordinates.latitude
  showCoordinatePicker.value = false
  ElMessage.success(`坐标已设置：经度 ${coordinates.longitude.toFixed(6)}, 纬度 ${coordinates.latitude.toFixed(6)}`)
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
              <div style="display: flex; gap: 8px; align-items: center;">
                <el-input-number 
                  v-model="formData.longitude" 
                  :precision="6" 
                  :min="-180"
                  :max="180"
                  style="flex: 1" 
                />
                <el-button 
                  type="primary" 
                  plain 
                  size="small"
                  @click="openCoordinatePicker"
                  title="在地图上选择位置"
                >
                  地图选择
                </el-button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="纬度" prop="latitude">
              <el-input-number 
                v-model="formData.latitude" 
                :precision="6" 
                :min="-90"
                :max="90"
                style="width: 100%" 
              />
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

        <!-- 图标显示设置（仅摄像头设备） -->
        <template v-if="deviceDetail?.device_type?.code === 'camera'">
          <el-divider content-position="left">图标显示设置</el-divider>
          
          <el-row :gutter="20">
            <el-col :span="16">
              <!-- 旋转角度 -->
              <el-form-item label="旋转角度" prop="iconRotation">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <el-slider
                    v-model="iconRotation"
                    :min="0"
                    :max="360"
                    :step="1"
                    show-input
                    :show-input-controls="false"
                    style="flex: 1"
                    @input="updateIconPreview"
                  />
                  <span style="min-width: 60px; text-align: right;">{{ iconRotation }}°</span>
                </div>
              </el-form-item>
              
              <!-- 镜面翻转 -->
              <el-form-item label="镜面翻转">
                <div style="display: flex; gap: 16px;">
                  <el-checkbox v-model="iconFlipHorizontal" @change="updateIconPreview">
                    水平翻转
                  </el-checkbox>
                  <el-checkbox v-model="iconFlipVertical" @change="updateIconPreview">
                    垂直翻转
                  </el-checkbox>
                </div>
              </el-form-item>
            </el-col>
            
            <el-col :span="8">
              <!-- 图标预览 -->
              <el-form-item label="预览效果">
                <div 
                  class="icon-preview-container"
                  :style="iconPreviewStyle"
                >
                  <img
                    :src="getCameraIconSrc()"
                    alt="摄像头图标"
                    class="icon-preview"
                    :style="iconTransformStyle"
                  />
                </div>
              </el-form-item>
            </el-col>
          </el-row>
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
    
    <!-- 坐标拾取器对话框 -->
    <CoordinatePicker
      v-model="showCoordinatePicker"
      :initial-lng="formData.longitude || 112.927176"
      :initial-lat="formData.latitude || 27.87076"
      @confirm="handleCoordinateSelected"
      @cancel="showCoordinatePicker = false"
    />
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

/* 图标预览样式 */
.icon-preview-container {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  background-color: #f5f7fa;
  position: relative;
  transition: all 0.3s ease;
}

.icon-preview {
  width: 48px;
  height: 48px;
  transition: transform 0.3s ease;
  transform-origin: center center;
}

.icon-preview-container:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}
</style>

