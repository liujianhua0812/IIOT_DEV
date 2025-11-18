<template>
  <div class="page-shell">
    <div class="container">
      <aside class="sidebar">
        <div class="system-header">
          <div class="system-title">细粒度访问控制系统</div>
        </div>

        <div 
          v-for="item in accessControlItems" 
          :key="item.name"
          class="device-category"
          :class="{ active: currentAccessControlType === item.name }"
          @click="navigateToAccessControl(item.name)"
        >
          <span class="category-icon">{{ item.icon }}</span> {{ item.name }}
        </div>
      </aside>

      <div class="main-content">
        <div class="header">
          <h1>柔性制造产线设备模型授权推理平台</h1>
        </div>

        <div class="status-bar">
          <div class="status-card">
            <span class="status-label">🕒 当前时间：</span>
            <span class="status-value">{{ currentTime }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">📍 设备位置：</span>
            <span class="status-value">{{ deviceLocation }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">🔐 模型状态：</span>
            <span class="status-badge" :class="modelStatus">{{ modelStatus === 'decrypted' ? '已解密' : '已加密' }}</span>
          </div>
        </div>

        <!-- 设备和模型选择栏 -->
        <div class="device-model-selection">
          <div class="selection-panel">
            <div class="device-list">
              <h3>🖥️ 可用设备</h3>
              <div class="selection-content">
                <div v-if="loadingDevices" class="loading-message">加载中...</div>
                <div v-else-if="devices.length === 0" class="empty-message">
                  {{ errorMessage || '暂无设备数据' }}
                </div>
                <div
                  v-for="device in devices"
                  :key="device.id"
                  class="device-item"
                  :class="{ active: currentDeviceId === device.id }"
                  @click="selectDevice(device)"
                >
                  <h4>{{ device.name }} <span class="device-meta">ID: {{ device.id }} | 位置: {{ device.location.region }}</span></h4>
                </div>
              </div>
            </div>
            
            <div class="model-list">
              <h3>🔷 现有模型</h3>
              <div class="selection-content">
                <div v-if="loadingModels" class="loading-message">加载中...</div>
                <div v-else-if="models.length === 0 && currentDeviceId" class="empty-message">
                  该设备暂无模型
                </div>
                <div v-else-if="!currentDeviceId" class="empty-message">
                  请先选择设备
                </div>
                <div
                  v-for="model in models"
                  :key="model.id"
                  class="model-item"
                  :class="{ active: currentModelId === model.id }"
                  @click="selectModel(model)"
                >
                  <div class="model-content">
                    <h4>{{ model.name }} <span class="model-meta">ID: {{ model.id }}</span></h4>
                    <p>{{ model.description }}</p>
                  </div>
                  <div class="model-status">
                    <span class="status-badge" :class="model.status">{{ model.status === 'decrypted' ? '已解密' : '已加密' }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="authorized-models-list">
              <h3>📜 授权合约信息</h3>
              <div class="selection-content">
                <div v-if="!currentDeviceId" class="empty-message">
                  请先选择设备
                </div>
                <div v-else-if="models.length === 0" class="empty-message">
                  该设备暂无模型
                </div>
                <div v-else>
                  <div
                    v-for="model in models"
                    :key="model.id"
                    :id="`contract-item-${model.id}`"
                    class="contract-item"
                    :class="{ 
                      'contract-valid': getContractForModel(model.id)?.isAuthorized,
                      'contract-invalid': !getContractForModel(model.id)?.isAuthorized,
                      active: currentModelId === model.id 
                    }"
                    @click="selectModel(model)"
                  >
                    <h4>{{ model.name }} <span class="model-meta">ID: {{ model.id }}</span></h4>
                    <div v-if="getContractForModel(model.id)?.contract" class="contract-details">
                      <div class="contract-details-grid">
                        <div class="contract-field">
                          <span class="field-label">合约ID:</span>
                          <span class="field-value">{{ getContractForModel(model.id).contract.contract_id }}</span>
                        </div>
                        <div class="contract-field">
                          <span class="field-label">设备ID:</span>
                          <span class="field-value">{{ getContractForModel(model.id).contract.device_id }}</span>
                        </div>
                        <div class="contract-field">
                          <span class="field-label">模型ID:</span>
                          <span class="field-value">{{ getContractForModel(model.id).contract.model_id }}</span>
                        </div>
                        <div class="contract-field">
                          <span class="field-label">授权区域:</span>
                          <span class="field-value">{{ getContractForModel(model.id).contract.allowed_regions.join(', ') }}</span>
                        </div>
                        <div class="contract-field">
                          <span class="field-label">授权开始:</span>
                          <span class="field-value">{{ getContractForModel(model.id).contract.start_time }}</span>
                        </div>
                        <div class="contract-field">
                          <span class="field-label">授权结束:</span>
                          <span class="field-value">{{ getContractForModel(model.id).contract.end_time }}</span>
                        </div>
                        <div class="contract-field">
                          <span class="field-label">{{ getDaysLabel(getContractForModel(model.id).contract.end_time) }}:</span>
                          <span class="field-value" :class="getDaysClass(getContractForModel(model.id).contract.end_time)">{{ getDaysValue(getContractForModel(model.id).contract.end_time) }}</span>
                        </div>
                      </div>
                    </div>
                    <div v-else>
                      <p class="no-contract">该模型未授权</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="action-verification-panel selection-panel" :class="{ 'has-content': verificationResult || showProgress || progress > 0 }">
          <div class="top-row">
            <div class="action-section">
              <button class="btn btn-primary" @click="decryptModel" :disabled="!canDecrypt || decrypting">
                {{ decrypting ? '解密中...' : '解密模型' }}
              </button>
              <button class="btn btn-info" @click="inferenceDataset" :disabled="!canInference">
                执行推理
              </button>
            </div>

            <div class="verification-result" v-if="verificationResult" :class="verificationResult.type" id="verificationResult">
              <div class="verification-layout">
                <div class="verification-left">
                  <!-- 授权合约 -->
                  <div class="verification-item" :class="{ checked: verificationResult.authorizationChecked, failed: verificationResult.authorizationFailed }">
                    <span class="check-icon">{{ verificationResult.authorizationChecked ? '✓' : (verificationResult.authorizationFailed ? '✗' : '') }}</span>
                    <span class="verification-label">授权合约:</span>
                    <span class="verification-message">{{ verificationResult.authorization }}</span>
                  </div>
                  <!-- 代码完整性 -->
                  <div class="verification-item" :class="{ checked: verificationResult.codeIntegrityChecked, failed: verificationResult.codeIntegrityFailed }">
                    <span class="check-icon">{{ verificationResult.codeIntegrityChecked ? '✓' : (verificationResult.codeIntegrityFailed ? '✗' : '') }}</span>
                    <span class="verification-label">代码完整性:</span>
                    <span class="verification-message">{{ verificationResult.codeIntegrity }}</span>
                  </div>
                  <!-- 模型完整性：始终展示，根据状态显示 ✓ / ✗ / 未执行 -->
                  <div class="verification-item" :class="{ checked: verificationResult.modelIntegrityChecked, failed: verificationResult.modelIntegrityFailed }">
                    <span class="check-icon">{{ verificationResult.modelIntegrityChecked ? '✓' : (verificationResult.modelIntegrityFailed ? '✗' : '') }}</span>
                    <span class="verification-label">模型完整性:</span>
                    <span class="verification-message">{{ verificationResult.modelIntegrity }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="progress-column" v-if="progress > 0 || showProgress" id="progressSection">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: progress + '%' }">{{ progress }}%</div>
              </div>
              <p class="progress-text">{{ uiProgressText }}</p>
            </div>
          </div>
        </div>

        <div class="inference-section selection-panel" v-if="showInference" id="inferenceSection">
          <h2>🧠 模型推理</h2>
          <div class="inference-actions">
            <button class="btn btn-primary" @click="inferenceDataset">数据集推理</button>
            <button class="btn btn-primary" @click="showUploadArea">上传图片推理</button>
            <input type="file" id="imageInput" accept="image/*" style="display: none;" @change="handleImageUpload" ref="imageInput">
          </div>
          <div class="upload-area" v-if="showUpload" id="uploadArea" @click="$refs.imageInput.click()" @dragover.prevent="handleDragOver" @dragleave.prevent="handleDragLeave" @drop.prevent="handleDrop" :class="{ dragover: isDragover }">
            <p>点击或拖拽图片到此处上传</p>
          </div>
          <div class="result-display" v-if="inferenceResult" id="resultDisplay">
            <div id="resultContent" v-html="inferenceResult"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'EdgeModelAccessControlView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const accessControlItems = [
      { name: '端侧模型访问控制', route: 'edge-model-access-control', icon: '⚙️' },
      { name: '云侧模型访问控制', route: 'cloud-model-access-control', icon: '☁️' },
      { name: '云上数据访问控制', route: 'cloud-data-access-control', icon: '💾' },
      { name: '链上数据访问控制', route: 'chain-data-access-control', icon: '⛓️' },
      { name: '视频数据访问控制', route: 'video-data-access-control', icon: '🎥' }
    ]
    
    const currentAccessControlType = ref('端侧模型访问控制')
    
    const currentTime = ref('--')
    const deviceLocation = ref('--')
    const modelStatus = ref('encrypted')
    const currentDeviceId = ref(null)
    const currentModelId = ref(null)
    const currentLocation = ref(null)
    const currentDeviceLocation = ref(null)
    const devices = ref([])
    const models = ref([])
    const authorizedModels = ref([])
    const contract = ref(null)
    const modelContracts = ref([])
    const showProgress = ref(false)
    const progress = ref(0)
    const progressText = ref('')
    const verificationResult = ref(null)
    const showInference = ref(false)
    const showUpload = ref(false)
    const inferenceResult = ref(null)
    const canDecrypt = ref(false)
    const canInference = ref(false)
    const decrypting = ref(false)
    const isDragover = ref(false)
    const imageInput = ref(null)
    const loadingDevices = ref(false)
    const loadingModels = ref(false)
    const errorMessage = ref('')

    // 检查合约是否已到期
    const isContractExpired = computed(() => {
      if (!contract.value || !contract.value.contract_id || !contract.value.end_time) {
        return false
      }
      try {
        const endTime = new Date(contract.value.end_time)
        const now = new Date()
        return now > endTime
      } catch (error) {
        console.error('解析合约到期时间失败:', error)
        return false
      }
    })

    // API配置
    // 优先使用环境变量，否则使用当前主机名和5002端口（后端服务端口）
    const API_HOST = import.meta.env.VITE_API_HOST || window.location.hostname
    const API_PORT = import.meta.env.VITE_API_PORT || '5002'
    const API_BASE = `http://${API_HOST}:${API_PORT}/api`
    const currentUserId = 'user1'
    
    // 调试信息
    console.log('API_BASE:', API_BASE)

    let timeInterval = null
    let statusCheckInterval = null

    // 重置所有模型状态为已加密的函数
    const resetAllModelsToEncrypted = async () => {
      try {
        // 调用后端API重置所有模型状态
        const res = await fetch(`${API_BASE}/reset-states`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (!res.ok) {
          console.error('重置后端模型状态失败:', res.statusText)
        } else {
          const data = await res.json()
          console.log('后端模型状态已重置:', data.message)
        }
      } catch (error) {
        console.error('调用重置后端模型状态API失败:', error)
      }
      
      // 重置前端所有模型的status为'encrypted'
      models.value.forEach(model => {
        model.status = 'encrypted'
      })
      // 重置当前模型状态
      modelStatus.value = 'encrypted'
      // 重置解密和推理相关状态
      canDecrypt.value = false
      canInference.value = false
      decrypting.value = false
      // 清空推理结果
      inferenceResult.value = null
      verificationResult.value = null
      showInference.value = false
    }

    const navigateToAccessControl = async (name) => {
      currentAccessControlType.value = name
      const item = accessControlItems.find(item => item.name === name)
      
      // 如果点击的是"端侧模型访问控制"，将所有模型状态更新为已加密
      if (name === '端侧模型访问控制') {
        await resetAllModelsToEncrypted()
      }
      
      if (item && route.name !== item.route) {
        router.push({ name: item.route })
      }
    }

    const updateTime = () => {
      const now = new Date()
      const pad = num => num.toString().padStart(2, '0')
      currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
    }

    const loadUserDevices = async () => {
      loadingDevices.value = true
      errorMessage.value = ''
      try {
        console.log('正在加载设备，API:', `${API_BASE}/user/devices?user_id=${currentUserId}`)
        const res = await fetch(`${API_BASE}/user/devices?user_id=${currentUserId}`)
        
        if (!res.ok) {
          throw new Error(`HTTP错误: ${res.status} ${res.statusText}`)
        }
        
        const data = await res.json()
        console.log('设备数据:', data)
        currentLocation.value = data.location
        deviceLocation.value = '--'
        devices.value = data.devices || []
        
        if (!data.devices || data.devices.length === 0) {
          errorMessage.value = '暂无设备数据，请检查后端服务是否正常运行'
        }
      } catch (error) {
        console.error('加载设备失败:', error)
        errorMessage.value = `加载设备失败: ${error.message}。请检查后端服务是否运行在 ${API_BASE}`
        devices.value = []
      } finally {
        loadingDevices.value = false
      }
    }

    const selectDevice = async (device) => {
      currentDeviceId.value = device.id
      if (device.location) {
        currentDeviceLocation.value = device.location
        deviceLocation.value = device.location.region
      }
      
      // 清空验证内容和进度条
      verificationResult.value = null
      showProgress.value = false
      progress.value = 0
      progressText.value = ''
      
      await loadDeviceModels(device.id)
      await loadAuthorizedModels(device.id)
      
      // 自动选择第一个可用模型
      if (models.value && models.value.length > 0) {
        await selectModel(models.value[0])
      } else {
        // 如果没有可用模型，清空当前模型选择和相关状态
        currentModelId.value = null
        contract.value = null
        modelStatus.value = 'encrypted'
        verificationResult.value = null
        inferenceResult.value = null
        showInference.value = false
        showUpload.value = false
        canDecrypt.value = false
        canInference.value = false
      }
    }

    const loadDeviceModels = async (deviceId) => {
      loadingModels.value = true
      try {
        console.log('正在加载模型，API:', `${API_BASE}/device/models?device_id=${deviceId}`)
        const res = await fetch(`${API_BASE}/device/models?device_id=${deviceId}`)
        
        if (!res.ok) {
          throw new Error(`HTTP错误: ${res.status} ${res.statusText}`)
        }
        
        const data = await res.json()
        console.log('模型数据:', data)
        const modelList = data.models || []
        // 按照后端返回的顺序显示
        models.value = modelList
        
        // 为每个模型加载授权合约信息
        await loadAllModelContracts(deviceId)
      } catch (error) {
        console.error('加载模型失败:', error)
        models.value = []
        modelContracts.value = []
        alert(`加载模型失败: ${error.message}`)
      } finally {
        loadingModels.value = false
      }
    }
    
    const loadAllModelContracts = async (deviceId) => {
      const contracts = []
      for (const model of models.value) {
        try {
          const res = await fetch(`${API_BASE}/contract?device_id=${deviceId}&model_id=${model.id}`)
          if (res.status === 404) {
            contracts.push({ model_id: model.id, contract: null, isAuthorized: false })
          } else {
            const data = await res.json()
            const contractData = data.contract
            const isAuthorized = contractData && contractData.contract_id && !isContractExpiredForModel(contractData)
            contracts.push({ 
              model_id: model.id, 
              contract: contractData, 
              isAuthorized 
            })
          }
        } catch (error) {
          console.error(`加载模型 ${model.id} 的合约失败:`, error)
          contracts.push({ model_id: model.id, contract: null, isAuthorized: false })
        }
      }
      modelContracts.value = contracts
    }
    
    const isContractExpiredForModel = (contractData) => {
      if (!contractData || !contractData.contract_id || !contractData.end_time) {
        return true
      }
      try {
        const endTime = new Date(contractData.end_time)
        const now = new Date()
        return now > endTime
      } catch (error) {
        console.error('解析合约到期时间失败:', error)
        return true
      }
    }
    
    const getContractForModel = (modelId) => {
      return modelContracts.value.find(c => c.model_id === modelId)
    }
    
    const calculateRemainingDays = (endTime) => {
      if (!endTime) return { days: 0, expired: true }
      try {
        const end = new Date(endTime)
        const now = new Date()
        const diffTime = end - now
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return { days: diffDays, expired: diffDays <= 0 }
      } catch (error) {
        console.error('计算剩余天数失败:', error)
        return { days: 0, expired: true }
      }
    }
    
    const getDaysLabel = (endTime) => {
      const result = calculateRemainingDays(endTime)
      return result.expired ? '过期天数' : '剩余天数'
    }
    
    const getDaysValue = (endTime) => {
      const result = calculateRemainingDays(endTime)
      const days = result.expired ? Math.abs(result.days) : result.days
      return `${days} 天`
    }
    
    const getDaysClass = (endTime) => {
      const result = calculateRemainingDays(endTime)
      return result.expired ? 'expired-days' : 'remaining-days'
    }

    const loadAuthorizedModels = async (deviceId) => {
      try {
        const res = await fetch(`${API_BASE}/device/authorized-models?device_id=${deviceId}`)
        const data = await res.json()
        if (data.authorized_models && data.authorized_models.length > 0) {
          // 按照后端返回的顺序显示
          authorizedModels.value = data.authorized_models
        } else {
          authorizedModels.value = []
        }
      } catch (error) {
        console.error('加载授权模型失败:', error)
        authorizedModels.value = []
      }
    }

    const selectModel = async (model) => {
      currentModelId.value = model.id
      
      // 清空验证内容和进度条
      verificationResult.value = null
      showProgress.value = false
      progress.value = 0
      progressText.value = ''
      
      inferenceResult.value = null
      showInference.value = false
      showUpload.value = false
      await loadModelStatus()
      await loadContract()
      canDecrypt.value = true
      canInference.value = true
      
      // 滚动到对应的授权合约信息选项框中间
      nextTick(() => {
        const contractItem = document.getElementById(`contract-item-${model.id}`)
        if (contractItem) {
          contractItem.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
            inline: 'nearest'
          })
        }
      })
    }

    const loadModelStatus = async () => {
      if (!currentDeviceId.value || !currentModelId.value) return
      try {
        const res = await fetch(`${API_BASE}/model/status?device_id=${currentDeviceId.value}&model_id=${currentModelId.value}`)
        const data = await res.json()
        modelStatus.value = data.status
        canInference.value = true
      } catch (error) {
        console.error('加载模型状态失败:', error)
        if (currentDeviceId.value && currentModelId.value) {
          canInference.value = true
        }
      }
    }

    const loadContract = async () => {
      if (!currentDeviceId.value || !currentModelId.value) return
      try {
        const res = await fetch(`${API_BASE}/contract?device_id=${currentDeviceId.value}&model_id=${currentModelId.value}`)
        if (res.status === 404) {
          contract.value = { contract_id: null }
          return
        }
        const data = await res.json()
        contract.value = data.contract
      } catch (error) {
        console.error('加载合约失败:', error)
      }
    }

    const decryptModel = async () => {
      if (!currentDeviceId.value || !currentModelId.value) {
        alert('请先选择设备和模型')
        return
      }

      showProgress.value = true
      progress.value = 0
      progressText.value = '授权合约验证中···'
      canDecrypt.value = false
      decrypting.value = true
      verificationResult.value = null

      try {
        // 步骤1: 验证授权合约和代码完整性
        progress.value = 30
        progressText.value = '代码完整性验证中···'

        const locationForVerification = currentDeviceLocation.value || currentLocation.value

        const verifyRes = await fetch(`${API_BASE}/model/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: currentDeviceId.value,
            model_id: currentModelId.value,
            location: locationForVerification
          })
        })

        const verifyData = await verifyRes.json()

        // 先显示授权/代码完整性阶段的初始状态，模型完整性默认未执行
        verificationResult.value = {
          type: 'verifying',
          authorization: verifyData.authorization.message,
          codeIntegrity: verifyData.code_integrity.message,
          modelIntegrity: '未执行',
          authorizationChecked: false,
          codeIntegrityChecked: false,
          modelIntegrityChecked: false,
          authorizationFailed: false,
          codeIntegrityFailed: false,
          modelIntegrityFailed: false
        }
        await new Promise(resolve => setTimeout(resolve, 300))

        // 若授权未通过，立即失败并停止后续验证
        if (!verifyData.authorization.valid) {
          verificationResult.value = {
            type: 'error',
            authorization: verifyData.authorization.message,
            codeIntegrity: '未执行',
            modelIntegrity: '未执行',
            authorizationChecked: false,
            codeIntegrityChecked: false,
            modelIntegrityChecked: false,
            authorizationFailed: true,
            codeIntegrityFailed: false,
            modelIntegrityFailed: false
          }
          progress.value = 100
          progressText.value = '模型解密失败！'
          showProgress.value = false
          canDecrypt.value = true
          decrypting.value = false
          return
        }

        // 授权通过，进入代码完整性验证阶段
        verificationResult.value = {
          type: 'verifying',
          authorization: verifyData.authorization.message,
          codeIntegrity: verifyData.code_integrity.message,
          modelIntegrity: '未执行',
          authorizationChecked: true,
          codeIntegrityChecked: false,
          modelIntegrityChecked: false,
          authorizationFailed: false,
          codeIntegrityFailed: false,
          modelIntegrityFailed: false
        }
        progressText.value = '代码完整性验证中···'
        await new Promise(resolve => setTimeout(resolve, 300))

        // 若代码完整性未通过，立即失败并停止后续流程
        if (!verifyData.code_integrity.valid) {
          verificationResult.value = {
            type: 'error',
            authorization: verifyData.authorization.message,
            codeIntegrity: verifyData.code_integrity.message,
            modelIntegrity: '未执行',
            authorizationChecked: true,
            codeIntegrityChecked: false,
            modelIntegrityChecked: false,
            authorizationFailed: false,
            codeIntegrityFailed: true,
            modelIntegrityFailed: false
          }
          progress.value = 100
          progressText.value = '模型解密失败！'
          showProgress.value = false
          canDecrypt.value = true
          decrypting.value = false
          return
        }

        // 两项验证均通过，进入模型完整性阶段提示
        progress.value = 40
        progressText.value = '模型完整性验证中···'
        await new Promise(resolve => setTimeout(resolve, 400))

        // 最后显示整体验证结果
        if (!verifyData.can_decrypt) {
          verificationResult.value = {
            type: 'error',
            authorization: verifyData.authorization.message,
            codeIntegrity: verifyData.code_integrity.message,
            modelIntegrity: '验证失败',
            authorizationChecked: verifyData.authorization.valid || false,
            codeIntegrityChecked: verifyData.code_integrity.valid || false,
            modelIntegrityChecked: false,
            authorizationFailed: false,
            codeIntegrityFailed: false,
            modelIntegrityFailed: true
          }
          progress.value = 100
          progressText.value = '模型解密失败！'
          showProgress.value = false
          canDecrypt.value = true
          decrypting.value = false
          return
        }

        verificationResult.value = {
          type: 'success',
          authorization: verifyData.authorization.message,
          codeIntegrity: verifyData.code_integrity.message,
          modelIntegrity: '模型完整性验证通过',
          authorizationChecked: verifyData.authorization.valid || false,
          codeIntegrityChecked: verifyData.code_integrity.valid || false,
          modelIntegrityChecked: true,
          authorizationFailed: false,
          codeIntegrityFailed: false,
          modelIntegrityFailed: false
        }

        // 步骤2: 获取解密密钥
        progress.value = 60
        progressText.value = '模型解密中···'

        const keyRes = await fetch(`${API_BASE}/model/get_key`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: currentDeviceId.value,
            model_id: currentModelId.value
          })
        })

        const keyData = await keyRes.json()
        if (!keyData.success) {
          throw new Error(keyData.error || '获取密钥失败')
        }

        // 步骤3: 解密模型
        progress.value = 85
        progressText.value = '模型解密中···'

        const decryptRes = await fetch(`${API_BASE}/model/decrypt`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: currentDeviceId.value,
            model_id: currentModelId.value
          })
        })

        const decryptData = await decryptRes.json()
        if (!decryptData.success) {
          throw new Error(decryptData.error || '解密失败')
        }

        // 完成
        progress.value = 100
        progressText.value = '模型解密完成！'

        setTimeout(async () => {
          await loadModelStatus()
          if (currentDeviceId.value) {
            await loadDeviceModels(currentDeviceId.value)
            await loadAuthorizedModels(currentDeviceId.value)
          }
          showProgress.value = false
          canDecrypt.value = true
          decrypting.value = false
          canInference.value = true
          alert('模型解密成功！')
        }, 1000)

      } catch (error) {
        alert('解密失败: ' + error.message + '\n提示：您仍然可以使用加密模型进行推理，但推理精度会较低。')
        showProgress.value = false
        canDecrypt.value = true
        decrypting.value = false
        canInference.value = true
      }
    }

    const showInferenceSection = () => {
      showInference.value = true
    }

    const showUploadArea = () => {
      showUpload.value = true
      inferenceResult.value = null
    }

    const handleImageUpload = (event) => {
      const file = event.target.files[0]
      if (!file) return

      const reader = new FileReader()
      reader.onload = (e) => {
        inferenceSingleImage(e.target.result)
      }
      reader.readAsDataURL(file)
    }

    const handleDragOver = () => {
      isDragover.value = true
    }

    const handleDragLeave = () => {
      isDragover.value = false
    }

    const handleDrop = (event) => {
      isDragover.value = false
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          inferenceSingleImage(e.target.result)
        }
        reader.readAsDataURL(file)
      }
    }

    const inferenceSingleImage = async (imageData) => {
      if (!currentDeviceId.value || !currentModelId.value) {
        alert('请先选择设备和模型')
        return
      }

      showProgress.value = true
      progress.value = 0
      progressText.value = '正在推理...'

      let currentProgress = 0
      const progressInterval = setInterval(() => {
        if (currentProgress < 90) {
          currentProgress += Math.random() * 15
          if (currentProgress > 90) currentProgress = 90
          progress.value = Math.floor(currentProgress)
        }
      }, 150)

      try {
        const res = await fetch(`${API_BASE}/inference/single`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: currentDeviceId.value,
            model_id: currentModelId.value,
            image: imageData
          })
        })

        const data = await res.json()
        clearInterval(progressInterval)

        progress.value = 100
        progressText.value = '推理完成！'

        if (data.error) {
          throw new Error(data.error)
        }

        showUpload.value = false

        if (data.model_type === 'yolov5') {
          const countColor = data.model_status === 'decrypted' ? 'rgba(39, 174, 96, 1)' : 'rgba(231, 76, 60, 1)'
          inferenceResult.value = `
            <div class="result-item">
              <h3>YOLOv5推理结果</h3>
              ${data.annotated_image ? `
                <div style="text-align: center; margin-bottom: 20px;">
                  <img src="${data.annotated_image}" alt="检测结果" style="max-width: 50%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
                </div>
              ` : '<p style="text-align: center; color: #e74c3c;">⚠️ 处理后的图像未返回</p>'}
              <p style="color: rgba(214, 232, 255, 0.9);"><strong style="color: #e6f1ff;">检测数量:</strong> <span style="font-size: 20px; font-weight: 700; color: ${countColor};">${data.detection_count || 0}</span></p>
              <p style="color: rgba(214, 232, 255, 0.9);"><strong style="color: #e6f1ff;">推理时间:</strong> <span style="font-size: 20px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.inference_time ? (data.inference_time * 1000).toFixed(2) : 'N/A'}ms</span></p>
              <p style="color: rgba(214, 232, 255, 0.9);"><strong style="color: #e6f1ff;">模型状态:</strong> <span style="font-size: 20px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></p>
              ${data.detections && data.detections.length > 0 ? `
                <div style="margin-top: 20px;">
                  <h4>检测详情:</h4>
                  <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <thead>
                      <tr style="background: rgba(9, 32, 56, 0.8);">
                        <th style="padding: 8px; border: 1px solid rgba(88, 178, 255, 0.2); color: #e6f1ff;">类别</th>
                        <th style="padding: 8px; border: 1px solid rgba(88, 178, 255, 0.2); color: #e6f1ff;">置信度</th>
                        <th style="padding: 8px; border: 1px solid rgba(88, 178, 255, 0.2); color: #e6f1ff;">边界框</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${data.detections.map(det => `
                        <tr>
                          <td style="padding: 8px; border: 1px solid rgba(88, 178, 255, 0.2); color: rgba(214, 232, 255, 0.9);">${det.class_name || 'N/A'}</td>
                          <td style="padding: 8px; border: 1px solid rgba(88, 178, 255, 0.2); color: rgba(214, 232, 255, 0.9);">${(det.confidence * 100).toFixed(2)}%</td>
                          <td style="padding: 8px; border: 1px solid rgba(88, 178, 255, 0.2); color: rgba(214, 232, 255, 0.9);">[${det.bbox ? det.bbox.map(b => b.toFixed(0)).join(', ') : 'N/A'}]</td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              ` : '<p style="text-align: center; color: rgba(214, 232, 255, 0.7); margin-top: 20px;">未检测到目标</p>'}
            </div>
          `
        } else {
          inferenceResult.value = `
            <div class="result-item">
              <h3>推理结果</h3>
              ${data.annotated_image ? `
                <div style="text-align: center; margin-bottom: 20px;">
                  <img src="${data.annotated_image}" alt="输入图像" style="max-width: 50%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
                </div>
              ` : ''}
              <p style="color: rgba(214, 232, 255, 0.9);"><strong style="color: #e6f1ff;">预测类别:</strong> <span style="font-size: 20px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.predicted_class}</span></p>
              <p style="color: rgba(214, 232, 255, 0.9);"><strong style="color: #e6f1ff;">置信度:</strong> <span style="font-size: 20px; font-weight: 700; color: rgba(88, 178, 255, 1);">${(data.confidence * 100).toFixed(2)}%</span></p>
              <p style="color: rgba(214, 232, 255, 0.9);"><strong style="color: #e6f1ff;">模型状态:</strong> <span style="font-size: 20px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></p>
            </div>
            <div class="result-item">
              <h3>所有类别概率</h3>
              <div class="class-probabilities">
                ${Object.entries(data.all_probabilities).map(([cls, prob]) => `
                  <div class="probability-item">
                    <div class="class-name">${cls}</div>
                    <div class="probability">${(prob * 100).toFixed(2)}%</div>
                  </div>
                `).join('')}
              </div>
            </div>
          `
        }

        setTimeout(() => {
          showProgress.value = false
        }, 500)

      } catch (error) {
        clearInterval(progressInterval)
        alert('推理失败: ' + error.message)
        showProgress.value = false
      }
    }

    const inferenceDataset = async () => {
      if (!currentDeviceId.value || !currentModelId.value) {
        alert('请先选择设备和模型')
        return
      }

      showUpload.value = false
      showInference.value = true

      showProgress.value = true
      progress.value = 0
      progressText.value = '正在推理数据集...'

      let currentProgress = 0
      const progressInterval = setInterval(() => {
        if (currentProgress < 90) {
          currentProgress += Math.random() * 10
          if (currentProgress > 90) currentProgress = 90
          progress.value = Math.floor(currentProgress)
        }
      }, 200)

      try {
        const res = await fetch(`${API_BASE}/inference/dataset`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: currentDeviceId.value,
            model_id: currentModelId.value,
            dataset: 'cifar10',
            batch_size: 128,
            num_samples: 1000
          })
        })

        clearInterval(progressInterval)

        progress.value = 100
        progressText.value = '推理完成！'

        const data = await res.json()

        if (data.error) {
          throw new Error(data.error)
        }

        if (data.dataset === 'yolov5_image_folder') {
          // 根据模型状态确定准确率指标的颜色
          const accuracyColor = data.model_status === 'decrypted' ? 'rgba(39, 174, 96, 1)' : 'rgba(231, 76, 60, 1)'
          
          inferenceResult.value = `
            <div class="result-item">
              <h3>数据集推理结果</h3>
              <div class="stats-highlight-box">
                <div class="stats-list">
                  ${data.accuracy ? `
                    <div class="stat-row">
                      <span class="stat-label">精确率:</span>
                      <span class="stat-value" style="font-size: 28px !important; font-weight: 700 !important; color: ${accuracyColor} !important;">${(data.accuracy.precision * 100).toFixed(2)}%</span>
                    </div>
                    <div class="stat-row">
                      <span class="stat-label">召回率:</span>
                      <span class="stat-value" style="font-size: 28px !important; font-weight: 700 !important; color: ${accuracyColor} !important;">${(data.accuracy.recall * 100).toFixed(2)}%</span>
                    </div>
                    <div class="stat-row">
                      <span class="stat-label">F1 Score:</span>
                      <span class="stat-value" style="font-size: 28px !important; font-weight: 700 !important; color: ${accuracyColor} !important;">${(data.accuracy.f1_score * 100).toFixed(2)}%</span>
                    </div>
                  ` : ''}
                  <div class="stat-row">
                    <span class="stat-label">总检测数量:</span>
                    <span class="stat-value" style="font-size: 22px; font-weight: 700; color: ${accuracyColor};">${data.total_detections}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">处理图片数:</span>
                    <span class="stat-value" style="font-size: 22px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.processed_images}/${data.total_images}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">平均检测数/图片:</span>
                    <span class="stat-value" style="font-size: 22px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.average_detections_per_image ? data.average_detections_per_image.toFixed(2) : '0.00'}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">模型状态:</span>
                    <span class="stat-value"><span class="status-badge ${data.model_status}">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></span>
                  </div>
                </div>
              </div>
              ${data.message ? `<p class="result-message">${data.message}</p>` : ''}
              ${data.images && data.images.length > 0 ? `
                <div style="margin-top: 20px;">
                  <h4>处理后的图片（${data.images.length}张）:</h4>
                  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-top: 12px;">
                    ${data.images.map(img => {
                      const count = img.detection_count !== undefined ? img.detection_count : (img.detections ? img.detections.length : 0)
                      const hasDetections = count > 0
                      const bgColor = hasDetections ? 'rgba(39, 174, 96, 0.2)' : 'rgba(231, 76, 60, 0.2)'
                      const borderColor = hasDetections ? 'rgba(39, 174, 96, 0.5)' : 'rgba(231, 76, 60, 0.5)'
                      return `
                        <div style="border: 2px solid ${borderColor}; border-radius: 6px; padding: 8px; background: ${bgColor};">
                          <div style="text-align: center; margin-bottom: 8px;">
                            <img src="${img.annotated_image}" alt="${img.filename}" style="max-width: 100%; height: auto; border-radius: 4px; border: 1px solid rgba(88, 178, 255, 0.2);">
                          </div>
                          <p style="text-align: center; font-weight: 600; margin-bottom: 4px; color: #e6f1ff; font-size: 12px;">${img.filename}</p>
                          <p style="text-align: center; color: rgba(214, 232, 255, 0.8); font-size: 11px; margin-bottom: 6px;">检测到 ${count} 个目标</p>
                          ${img.detections && img.detections.length > 0 ? `
                            <div style="margin-top: 6px; font-size: 11px;">
                              ${img.detections.map(det => `
                                <div style="padding: 2px 0; border-bottom: 1px solid rgba(88, 178, 255, 0.15); color: rgba(214, 232, 255, 0.85);">
                                  <strong style="color: #e6f1ff;">${det.class || det.class_name || 'N/A'}</strong>: ${(det.confidence * 100).toFixed(1)}%
                                </div>
                              `).join('')}
                            </div>
                          ` : ''}
                        </div>
                      `
                    }).join('')}
                  </div>
                </div>
              ` : ''}
            </div>
          `
        } else {
          const samples = data.samples || []
          inferenceResult.value = `
            <div class="result-item">
              <h3>数据集推理结果</h3>
              <div class="stats-highlight-box">
                <div class="stats-list">
                  <div class="stat-row">
                    <span class="stat-label">数据集准确率:</span>
                    <span class="stat-value accuracy" style="font-size: 32px; font-weight: 700; color: rgba(39, 174, 96, 1);">${data.accuracy ? data.accuracy.toFixed(2) : '0.00'}%</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">总样本数:</span>
                    <span class="stat-value" style="font-size: 22px; font-weight: 700; color: rgba(88, 178, 255, 1);">${data.total_samples || 0}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label">模型状态:</span>
                    <span class="stat-value"><span class="status-badge ${data.model_status}">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></span>
                  </div>
                </div>
              </div>
              ${data.model_status === 'encrypted' ? '<p class="result-warning">⚠️ 模型未解密，推理精度较低</p>' : ''}
              ${samples.length > 0 ? `
                <div style="margin-top: 20px;">
                  <h4>样本推理结果（显示前${samples.length}个）:</h4>
                  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-top: 12px;">
                    ${samples.map((sample, index) => {
                      const bgColor = sample.is_correct ? 'rgba(39, 174, 96, 0.2)' : 'rgba(231, 76, 60, 0.2)'
                      const borderColor = sample.is_correct ? 'rgba(39, 174, 96, 0.5)' : 'rgba(231, 76, 60, 0.5)'
                      return `
                      <div style="border: 2px solid ${borderColor}; border-radius: 6px; padding: 8px; background: ${bgColor};">
                        <div style="text-align: center; margin-bottom: 8px;">
                          <img src="${sample.image}" alt="Sample ${index + 1}" style="max-width: 100%; height: auto; border-radius: 4px; border: 1px solid rgba(88, 178, 255, 0.2);">
                        </div>
                        <div style="font-size: 11px;">
                          <p style="margin: 3px 0; font-weight: 600; color: #e6f1ff;">真实: ${sample.true_class}</p>
                          <p style="margin: 3px 0; font-weight: 600; ${sample.is_correct ? 'color: #27ae60;' : 'color: #e74c3c;'}">
                            预测: ${sample.predicted_class} ${sample.is_correct ? '✓' : '✗'}
                          </p>
                          <p style="margin: 3px 0; color: rgba(214, 232, 255, 0.85);">
                            置信度: ${(sample.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    `
                    }).join('')}
                  </div>
                </div>
              ` : ''}
            </div>
          `
        }

        setTimeout(() => {
          showProgress.value = false
        }, 500)

      } catch (error) {
        clearInterval(progressInterval)
        alert('推理失败: ' + error.message)
        showProgress.value = false
      }
    }

    const startStatusCheck = () => {
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval)
      }
      statusCheckInterval = setInterval(async () => {
        if (currentDeviceId.value && currentModelId.value) {
          await loadModelStatus()
          const res = await fetch(`${API_BASE}/model/status?device_id=${currentDeviceId.value}&model_id=${currentModelId.value}`)
          const data = await res.json()
          if (data.status === 'encrypted') {
            await loadDeviceModels(currentDeviceId.value)
            await loadAuthorizedModels(currentDeviceId.value)
          }
        }
      }, 10000)
    }

    const encryptAllModelsOnClose = () => {
      const data = JSON.stringify({})
      if (navigator.sendBeacon) {
        const blob = new Blob([data], { type: 'application/json' })
        navigator.sendBeacon(`${API_BASE}/encrypt-all`, blob)
      } else {
        const xhr = new XMLHttpRequest()
        xhr.open('POST', `${API_BASE}/encrypt-all`, false)
        xhr.setRequestHeader('Content-Type', 'application/json')
        try {
          xhr.send(data)
        } catch (e) {
          // 忽略错误
        }
      }
    }

    onMounted(async () => {
      // 如果当前路由是端侧模型访问控制，重置所有模型状态
      if (route.name === 'edge-model-access-control') {
        await resetAllModelsToEncrypted()
      }
      
      await loadUserDevices()
      updateTime()
      timeInterval = setInterval(updateTime, 1000)
      startStatusCheck()

      // 页面关闭时加密所有模型
      window.addEventListener('beforeunload', encryptAllModelsOnClose)
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
          fetch(`${API_BASE}/encrypt-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}),
            keepalive: true
          }).catch(() => {})
        }
      })
    })

    onUnmounted(() => {
      if (timeInterval) clearInterval(timeInterval)
      if (statusCheckInterval) clearInterval(statusCheckInterval)
      window.removeEventListener('beforeunload', encryptAllModelsOnClose)
    })

    return {
      accessControlItems,
      currentAccessControlType,
      currentTime,
      deviceLocation,
      modelStatus,
      currentDeviceId,
      currentModelId,
      devices,
      models,
      authorizedModels,
      contract,
      showProgress,
      progress,
      progressText,
      uiProgressText: computed(() => {
        // 优先使用现有progressText，但做一层文案映射，确保符合需求
        const t = (progressText.value || '').trim()
        if (t.includes('失败')) return '模型解密失败！'
        if (t.includes('授权') && t.includes('验证')) return '授权合约验证中···'
        if (t.includes('代码') && t.includes('验证')) return '代码完整性验证中···'
        if (t.includes('模型') && t.includes('完整') && t.includes('验证')) return '模型完整性验证中···'
        if (t.includes('解密完成')) return '模型解密完成！'
        if (t.includes('解密')) return '模型解密中···'
        return t || '处理中···'
      }),
      verificationResult,
      showInference,
      showUpload,
      inferenceResult,
      canDecrypt,
      canInference,
      decrypting,
      isDragover,
      imageInput,
      loadingDevices,
      loadingModels,
      errorMessage,
      isContractExpired,
      modelContracts,
      getContractForModel,
      calculateRemainingDays,
      getDaysLabel,
      getDaysValue,
      getDaysClass,
      navigateToAccessControl,
      selectDevice,
      selectModel,
      decryptModel,
      showInferenceSection,
      showUploadArea,
      handleImageUpload,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      inferenceDataset
    }
  }
}
</script>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(4, 21, 38, 0.96), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.container {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 200px);
}

.sidebar {
  width: 360px;
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.system-header {
  text-align: center;
  margin-bottom: 12px;
}

.system-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin-bottom: 6px;
}

.device-category {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  border-bottom: 1px solid rgba(88, 178, 255, 0.12);
  font-size: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 18px;
  line-height: 1;
}

.device-category:hover {
  background: rgba(128, 214, 255, 0.1);
}

.device-category.active {
  background: rgba(88, 178, 255, 0.2);
  border-color: rgba(88, 178, 255, 0.35);
  font-weight: 700;
}

.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  color: #e6f1ff;
  font-size: 24px;
  margin-bottom: 10px;
  letter-spacing: 1.4px;
  font-weight: normal;
}

.device-model-selection {
  margin-bottom: 30px;
}

.action-verification-panel {
  margin-bottom: 24px;
  display: block !important;
  width: fit-content;
  max-width: 100%;
  transition: width 0.3s ease;
}

.action-verification-panel.has-content {
  width: 100%;
}

/* 避免推理结果在grid布局中自动落到右侧列 */
.inference-section.selection-panel {
  display: block;
}

.selection-panel {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 2px 24px 12px 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.device-list, .model-list, .authorized-models-list {
  display: flex;
  flex-direction: column;
}

.device-list h3, .model-list h3, .authorized-models-list h3 {
  margin-bottom: 20px;
  font-size: 20px;
  color: #e6f1ff;
  font-weight: 600;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 10px;
}

.selection-content {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.selection-content::-webkit-scrollbar {
  width: 6px;
}

.selection-content::-webkit-scrollbar-track {
  background: rgba(4, 19, 34, 0.6);
  border-radius: 3px;
}

.selection-content::-webkit-scrollbar-thumb {
  background: rgba(88, 178, 255, 0.3);
  border-radius: 3px;
}

.selection-content::-webkit-scrollbar-thumb:hover {
  background: rgba(88, 178, 255, 0.5);
}

.device-item, .model-item {
  background: rgba(88, 178, 255, 0.1);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.model-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.model-content {
  flex: 1;
  min-width: 0;
}

.model-status {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.device-item:hover, .model-item:hover {
  background: rgba(88, 178, 255, 0.2);
  transform: translateX(5px);
  border-color: rgba(88, 178, 255, 0.3);
}

.device-item.active, .model-item.active {
  background: rgba(88, 178, 255, 0.25);
  border-color: rgba(88, 178, 255, 0.5);
}

.device-item h4, .model-item h4 {
  font-size: 14px;
  margin-bottom: 5px;
  color: #e6f1ff;
  font-weight: 600;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.model-content h4 {
  margin-bottom: 5px;
}

.device-meta, .model-meta {
  font-size: 11px;
  font-weight: normal;
  color: rgba(214, 232, 255, 0.6);
  opacity: 0.8;
}

.device-item p, .model-content p {
  font-size: 12px;
  opacity: 0.8;
  color: rgba(214, 232, 255, 0.8);
  margin: 3px 0;
}

.model-item.authorized {
  background: rgba(39, 174, 96, 0.15);
  border-left: 3px solid rgba(39, 174, 96, 0.6);
}

.model-item.authorized h4 {
  color: rgba(39, 174, 96, 1);
}

.authorized-models-list {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.authorized-models-list .contract-item {
  background: rgba(88, 178, 255, 0.1);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.authorized-models-list .contract-item.contract-valid {
  background: rgba(39, 174, 96, 0.15);
  border-left: 3px solid rgba(39, 174, 96, 0.6);
}

.authorized-models-list .contract-item.contract-invalid {
  background: rgba(231, 76, 60, 0.15);
  border-left: 3px solid rgba(231, 76, 60, 0.6);
}

.authorized-models-list .contract-item:hover {
  background: rgba(88, 178, 255, 0.2);
  transform: translateX(5px);
  border-color: rgba(88, 178, 255, 0.3);
}

.authorized-models-list .contract-item.contract-valid:hover {
  background: rgba(39, 174, 96, 0.25);
}

.authorized-models-list .contract-item.contract-invalid:hover {
  background: rgba(231, 76, 60, 0.25);
}

.authorized-models-list .contract-item.active {
  background: rgba(88, 178, 255, 0.25);
  border-color: rgba(88, 178, 255, 0.5);
}

.authorized-models-list .contract-item h4 {
  font-size: 14px;
  margin-bottom: 5px;
  color: #e6f1ff;
  font-weight: 600;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.authorized-models-list .contract-item p {
  font-size: 12px;
  opacity: 0.8;
  color: rgba(214, 232, 255, 0.8);
  margin: 3px 0;
}

.authorized-models-list .contract-item .no-contract {
  color: rgba(231, 76, 60, 0.9);
  font-style: italic;
}

.contract-details {
  margin-top: 8px;
}

.contract-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px 12px;
}

.contract-field {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
}

.contract-field .field-label {
  font-size: 11px;
  color: rgba(214, 232, 255, 0.6);
  font-weight: 500;
  white-space: nowrap;
}

.contract-field .field-value {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.9);
  word-break: break-word;
}

.contract-field .field-value.remaining-days {
  color: rgba(39, 174, 96, 1);
  font-weight: 600;
}

.contract-field .field-value.expired-days {
  color: rgba(231, 76, 60, 1);
  font-weight: 600;
}

.authorized-count {
  margin-bottom: 10px;
  color: rgba(39, 174, 96, 1);
  font-weight: bold;
  font-size: 13px;
}

.remaining-days {
  color: rgba(39, 174, 96, 1);
  font-weight: bold;
}

.empty-message {
  color: rgba(214, 232, 255, 0.6);
  font-size: 16px;
  text-align: center;
  padding: 20px;
}

.loading-message {
  color: rgba(88, 178, 255, 0.8);
  font-size: 12px;
  text-align: center;
  padding: 20px;
}

.status-bar {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.status-card {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  color: #e6f1ff;
  padding: 12px 16px;
  border-radius: 10px;
  flex: 1;
  min-width: 220px;
  height: 50px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-size: 14px;
  opacity: 0.9;
  color: rgba(214, 232, 255, 0.8);
  white-space: nowrap;
}

.status-value {
  font-size: 16px;
  font-weight: bold;
  color: #e6f1ff;
  flex: 1;
}

.status-badge {
  display: inline-block;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
}

.status-badge.encrypted {
  background: rgba(231, 76, 60, 0.3);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.5);
}

.status-badge.decrypted {
  background: rgba(39, 174, 96, 0.3);
  color: #27ae60;
  border: 1px solid rgba(39, 174, 96, 0.5);
}

.contract-section {
  background: rgba(9, 32, 56, 0.6);
  border-radius: 10px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(88, 178, 255, 0.12);
}

.contract-section h2 {
  color: #e6f1ff;
  margin-bottom: 20px;
  font-size: 22px;
}

.contract-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.contract-item {
  background: rgba(4, 19, 34, 0.6);
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid rgba(88, 178, 255, 0.5);
}

.contract-item label {
  font-weight: bold;
  color: rgba(214, 232, 255, 0.7);
  font-size: 12px;
  display: block;
  margin-bottom: 5px;
}

.contract-item .value {
  color: #e6f1ff;
  font-size: 16px;
}

.contract-warning {
  padding: 20px;
  text-align: center;
  background: rgba(255, 193, 7, 0.15);
  border: 2px solid rgba(255, 193, 7, 0.4);
  border-radius: 8px;
  color: rgba(255, 193, 7, 0.9);
  grid-column: 1 / -1;
  margin-bottom: 20px;
}

.contract-warning h3 {
  margin-bottom: 10px;
  color: rgba(255, 193, 7, 1);
}

.contract-warning p {
  margin: 5px 0;
  color: rgba(255, 193, 7, 0.9);
}

.contract-warning.expired {
  background: rgba(231, 76, 60, 0.15);
  border: 2px solid rgba(231, 76, 60, 0.4);
  color: rgba(231, 76, 60, 0.9);
}

.contract-warning.expired h3 {
  color: rgba(231, 76, 60, 1);
}

.contract-warning.expired p {
  color: rgba(231, 76, 60, 0.9);
}

.top-row {
  display: flex;
  gap: 24px;
  margin: 21px 0 8px 0;
  padding: 0 20px;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
}

.action-section {
  flex: 0 0 auto;
  padding-top: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 150px;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  margin-right: 10px;
  margin-bottom: 10px;
  font-family: inherit;
}

/* 仅在左侧操作区维持紧凑垂直布局与统一高度 */
.action-section .btn {
  margin: 0;
  line-height: 1.5;
}

.btn-primary {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.3), rgba(73, 197, 255, 0.3));
  color: #e6f1ff;
  border: 1px solid rgba(88, 178, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(73, 197, 255, 0.4));
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(88, 178, 255, 0.3);
}

.btn-info {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.3), rgba(73, 197, 255, 0.3));
  color: #e6f1ff;
  border: 1px solid rgba(88, 178, 255, 0.3);
}

.btn-info:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(73, 197, 255, 0.4));
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(88, 178, 255, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.progress-section {
  margin: 0;
  width: 100%;
  clear: both;
}

.progress-column {
  flex: 1 1 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  margin-top: 8px;
}

.progress-bar {
  width: 100%;
  height: 30px;
  background: rgba(4, 19, 34, 0.6);
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: 10px;
  border: 1px solid rgba(88, 178, 255, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(88, 178, 255, 0.6), rgba(73, 197, 255, 0.6));
  width: 0%;
  transition: width 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e6f1ff;
  font-weight: bold;
}

.progress-text {
  text-align: center;
  color: rgba(214, 232, 255, 0.8);
}

.verification-result {
  flex: 0 0 auto;
  margin: 0;
  padding: 12px 15px;
  border-radius: 8px;
  background: rgba(9, 32, 56, 0.6);
  border: 1px solid rgba(88, 178, 255, 0.2);
  height: 116px;
  box-sizing: border-box;
  overflow-y: auto;
  width: fit-content;
}

.verification-layout {
  display: flex;
  align-items: stretch;
  gap: 16px;
}

.verification-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0;
  height: 100%;
}

.verification-middle {
  width: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.verification-middle .arrow {
  font-size: 40px;
  color: rgba(39, 174, 96, 0.95);
}

.verification-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.verification-right .pass-text {
  color: rgba(39, 174, 96, 0.95);
  font-weight: 600;
}

.verification-right .pending-text {
  color: rgba(214, 232, 255, 0.8);
}

.verification-right .fail-text {
  color: rgba(231, 76, 60, 0.95);
  font-weight: 600;
}

.verification-result.verifying {
  background: rgba(9, 32, 56, 0.6);
  border: 1px solid rgba(88, 178, 255, 0.3);
  color: #e6f1ff;
}

.verification-result.success {
  background: rgba(39, 174, 96, 0.15);
  border: 1px solid rgba(39, 174, 96, 0.4);
  color: rgba(39, 174, 96, 1);
}

.verification-result.error {
  background: rgba(231, 76, 60, 0.15);
  border: 1px solid rgba(231, 76, 60, 0.4);
  color: #e74c3c;
}

.verification-result h3 {
  margin-bottom: 12px;
  font-size: 18px;
}

.verification-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.verification-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.verification-item.checked {
  color: rgba(39, 174, 96, 1);
}

.verification-item .check-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  color: rgba(39, 174, 96, 1);
}

.verification-item.failed {
  color: rgba(231, 76, 60, 1);
}

.verification-item.failed .check-icon {
  color: rgba(231, 76, 60, 1);
}

.verification-item .verification-label {
  font-weight: 600;
  min-width: 100px;
  color: inherit;
}

.verification-item .verification-message {
  flex: 1;
  color: inherit;
  opacity: 0.9;
}

.inference-section {
  margin-top: 0;
  margin-bottom: 24px;
}

.inference-section h2 {
  color: #e6f1ff;
  margin-bottom: 20px;
  font-size: 20px;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 10px;
}

.inference-actions {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed rgba(88, 178, 255, 0.3);
  border-radius: 10px;
  padding: 40px;
  text-align: center;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(9, 32, 56, 0.3);
  color: rgba(214, 232, 255, 0.8);
}

.upload-area:hover {
  border-color: rgba(88, 178, 255, 0.5);
  background: rgba(9, 32, 56, 0.5);
}

.upload-area.dragover {
  border-color: rgba(88, 178, 255, 0.6);
  background: rgba(9, 32, 56, 0.6);
}

.result-display {
  background: rgba(9, 32, 56, 0.6);
  border-radius: 10px;
  padding: 12px 25px 25px 25px;
  margin-top: 20px;
  border: 1px solid rgba(88, 178, 255, 0.12);
}

.result-item {
  margin-bottom: 15px;
  padding: 8px 15px 15px 15px;
  background: rgba(4, 19, 34, 0.6);
  border-radius: 8px;
  color: #e6f1ff;
}

.result-item h3 {
  color: #e6f1ff;
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 18px;
}

.result-item h4 {
  color: rgba(214, 232, 255, 0.9);
  margin-top: 15px;
  margin-bottom: 10px;
  font-size: 14px;
}

.result-item p {
  color: rgba(214, 232, 255, 0.8);
  margin: 8px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.stats-highlight-box {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.15), rgba(73, 197, 255, 0.15));
  border: 2px solid rgba(88, 178, 255, 0.4);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.2);
}

/* 让“下面数据框”根据文字长度自适应宽度，而不是占满整行 */
.result-item .stats-highlight-box {
  display: inline-block;
  width: auto;
  max-width: 100%;
}
.result-item .stats-list { 
  width: max-content; 
}
.result-item .stat-row { 
  width: max-content; 
}

/* 作用于v-html渲染内容的深度选择器，确保自适应宽度生效 */
:deep(.result-item .stats-highlight-box) {
  display: inline-block;
  width: auto;
  max-width: 100%;
}
:deep(.result-item .stats-list) {
  width: max-content;
  align-items: flex-start;
}
:deep(.result-item .stat-row) {
  width: max-content;
  justify-content: flex-start;
  gap: 12px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 0;
}

.stat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(9, 32, 56, 0.3);
  border-radius: 6px;
  border: 1px solid rgba(88, 178, 255, 0.2);
}

.stat-item {
  background: rgba(9, 32, 56, 0.4);
  border-radius: 6px;
  padding: 10px 12px;
  text-align: center;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #e6f1ff;
  margin-bottom: 4px;
  line-height: 1.2;
}

.stat-row .stat-value {
  font-size: 22px;
  font-weight: 700;
  color: rgba(88, 178, 255, 1);
  margin-bottom: 0;
}

.stat-value.accuracy {
  font-size: 32px;
  font-weight: 700;
  color: rgba(39, 174, 96, 1);
}

:deep(.stat-row .stat-value) {
  font-size: 22px !important;
  font-weight: 700 !important;
  color: rgba(88, 178, 255, 1) !important;
  margin-bottom: 0;
}

:deep(.stat-value.accuracy) {
  font-size: 32px !important;
  font-weight: 700 !important;
  color: rgba(39, 174, 96, 1) !important;
}

:deep(.stats-highlight-box) {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.15), rgba(73, 197, 255, 0.15)) !important;
  border: 2px solid rgba(88, 178, 255, 0.4) !important;
  border-radius: 10px !important;
  padding: 16px !important;
  margin-bottom: 12px !important;
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.2) !important;
}

.stat-label {
  font-size: 11px;
  color: rgba(214, 232, 255, 0.7);
  font-weight: 500;
}

.stat-row .stat-label {
  font-size: 16px;
  color: rgba(214, 232, 255, 0.9);
  font-weight: 600;
  white-space: nowrap;
}

.result-message {
  text-align: center;
  color: rgba(39, 174, 96, 1);
  margin-top: 12px;
  padding: 8px;
  background: rgba(39, 174, 96, 0.1);
  border-radius: 4px;
  font-size: 13px;
}

.result-warning {
  text-align: center;
  color: rgba(231, 76, 60, 1);
  margin-top: 12px;
  padding: 8px;
  background: rgba(231, 76, 60, 0.1);
  border-radius: 4px;
  font-size: 13px;
}

.result-item table {
  color: #e6f1ff;
}

.result-item table th {
  background: rgba(9, 32, 56, 0.8);
  color: #e6f1ff;
  border: 1px solid rgba(88, 178, 255, 0.2);
}

.result-item table td {
  border: 1px solid rgba(88, 178, 255, 0.2);
  color: rgba(214, 232, 255, 0.9);
}

.accuracy-display {
  font-size: 48px;
  font-weight: bold;
  color: rgba(39, 174, 96, 1);
  text-align: center;
  margin: 20px 0;
}

.class-probabilities {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.probability-item {
  background: rgba(4, 19, 34, 0.6);
  padding: 10px;
  border-radius: 5px;
  text-align: center;
  border: 1px solid rgba(88, 178, 255, 0.2);
}

.probability-item .class-name {
  font-weight: bold;
  color: #e6f1ff;
  margin-bottom: 5px;
}

.probability-item .probability {
  color: rgba(214, 232, 255, 0.8);
  font-size: 14px;
}

@media (max-width: 1100px) {
  .main-content {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
  }
  .selection-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-shell {
    padding: 16px 24px 32px;
  }
  .main-content {
    padding: 20px 15px;
  }
  .header h1 {
    font-size: 24px;
  }
  .selection-panel {
    padding: 16px;
  }
  .selection-content {
    max-height: 300px;
  }
}
</style>

