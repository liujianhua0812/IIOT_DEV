<template>
  <div class="page-shell">
    <div class="container">
      <div class="sidebar" :class="{ collapsed: sidebarCollapsed }" id="sidebar">
        <button class="sidebar-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'">
          <span>{{ sidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
        <h2>设备与模型</h2>
        <div class="device-list">
          <h3>可用设备</h3>
          <div id="deviceList">
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
              <h3>{{ device.name }}</h3>
              <p>ID: {{ device.id }}</p>
              <p>位置: {{ device.location.region }}</p>
            </div>
          </div>
        </div>
        <div class="model-list">
          <h3>可用模型</h3>
          <div id="modelList">
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
              <h3>{{ model.name }}</h3>
              <p>ID: {{ model.id }}</p>
              <p>{{ model.description }}</p>
              <p>状态: <span class="status-badge" :class="model.status">{{ model.status === 'decrypted' ? '已解密' : '已加密' }}</span></p>
            </div>
          </div>
        </div>
        <div class="authorized-models-list">
          <h3>授权周期内可用模型</h3>
          <div id="authorizedModelsList">
            <div v-if="authorizedModels.length === 0" class="empty-message">
              请先选择设备
            </div>
            <div v-else>
              <p class="authorized-count">✓ 当前有 {{ authorizedModels.length }} 个模型在授权周期内</p>
              <div
                v-for="model in authorizedModels"
                :key="model.id"
                class="model-item authorized"
                :class="{ active: currentModelId === model.id }"
                @click="selectModel(model)"
              >
                <h3>{{ model.name }}</h3>
                <p>ID: {{ model.id }}</p>
                <p>
                  <strong>授权到期:</strong> {{ model.contract.end_time }}<br>
                  <strong>剩余天数:</strong> <span class="remaining-days">{{ model.contract.remaining_days }} 天</span><br>
                  <strong>授权区域:</strong> {{ model.contract.allowed_regions.join(', ') }}
                </p>
                <p>状态: <span class="status-badge" :class="model.status">{{ model.status === 'decrypted' ? '已解密' : '已加密' }}</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="main-content">
        <div class="header">
          <h1>端侧模型访问控制系统</h1>
          <p>柔性制造产线设备模型推理平台模型</p>
        </div>

        <div class="status-bar">
          <div class="status-card">
            <h3>当前时间</h3>
            <div class="value">{{ currentTime }}</div>
          </div>
          <div class="status-card">
            <h3>设备位置</h3>
            <div class="value">{{ deviceLocation }}</div>
          </div>
          <div class="status-card">
            <h3>模型状态</h3>
            <div class="value">
              <span class="status-badge" :class="modelStatus">{{ modelStatus === 'decrypted' ? '已解密' : '已加密' }}</span>
            </div>
          </div>
        </div>

        <div class="contract-section" v-if="contract" id="contractSection">
          <h2>授权合约信息</h2>
          <div class="contract-info" id="contractInfo">
            <div v-if="!contract.contract_id" class="contract-warning">
              <h3>⚠️ 该模型未授权</h3>
              <p>设备 <strong>{{ currentDeviceId }}</strong> 未授权使用模型 <strong>{{ currentModelId }}</strong></p>
              <p>您仍然可以使用加密模型进行推理，但推理精度会很低，且无法解密模型。</p>
            </div>
            <template v-else>
              <div class="contract-item">
                <label>合约ID</label>
                <div class="value">{{ contract.contract_id }}</div>
              </div>
              <div class="contract-item">
                <label>设备ID</label>
                <div class="value">{{ contract.device_id }}</div>
              </div>
              <div class="contract-item">
                <label>模型ID</label>
                <div class="value">{{ contract.model_id }}</div>
              </div>
              <div class="contract-item">
                <label>授权区域</label>
                <div class="value">{{ contract.allowed_regions.join(', ') }}</div>
              </div>
              <div class="contract-item">
                <label>授权开始时间</label>
                <div class="value">{{ contract.start_time }}</div>
              </div>
              <div class="contract-item">
                <label>授权结束时间</label>
                <div class="value">{{ contract.end_time }}</div>
              </div>
            </template>
          </div>
        </div>

        <div class="action-section">
          <button class="btn btn-primary" @click="decryptModel" :disabled="!canDecrypt || decrypting">
            {{ decrypting ? '解密中...' : '解密模型' }}
          </button>
          <button class="btn btn-info" @click="showInferenceSection" :disabled="!canInference">
            执行推理
          </button>
        </div>

        <div class="progress-section" v-if="showProgress" id="progressSection">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }">{{ progress }}%</div>
          </div>
          <p class="progress-text">{{ progressText }}</p>
        </div>

        <div class="verification-result" v-if="verificationResult" :class="verificationResult.type" id="verificationResult">
          <h3>{{ verificationResult.type === 'success' ? '✓' : '✗' }} {{ verificationResult.type === 'success' ? '验证通过' : '验证失败' }}</h3>
          <p>授权合约: {{ verificationResult.authorization }}</p>
          <p>代码完整性: {{ verificationResult.codeIntegrity }}</p>
        </div>

        <div class="inference-section" v-if="showInference" id="inferenceSection">
          <h2>模型推理</h2>
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
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'EdgeModelAccessControlView',
  setup() {
    const sidebarCollapsed = ref(false)
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

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      if (window.innerWidth > 768) {
        localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
      }
    }

    const updateTime = async () => {
      try {
        const res = await fetch(`${API_BASE}/time`)
        const data = await res.json()
        currentTime.value = data.current_time
      } catch (error) {
        console.error('获取时间失败:', error)
      }
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
      await loadDeviceModels(device.id)
      await loadAuthorizedModels(device.id)
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
        models.value = data.models || []
      } catch (error) {
        console.error('加载模型失败:', error)
        models.value = []
        alert(`加载模型失败: ${error.message}`)
      } finally {
        loadingModels.value = false
      }
    }

    const loadAuthorizedModels = async (deviceId) => {
      try {
        const res = await fetch(`${API_BASE}/device/authorized-models?device_id=${deviceId}`)
        const data = await res.json()
        if (data.authorized_models && data.authorized_models.length > 0) {
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
      verificationResult.value = null
      inferenceResult.value = null
      showInference.value = false
      showUpload.value = false
      await loadModelStatus()
      await loadContract()
      canDecrypt.value = true
      canInference.value = true
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
      progressText.value = '开始验证授权合约...'
      canDecrypt.value = false
      decrypting.value = true

      try {
        // 步骤1: 验证授权合约和代码完整性
        progress.value = 30
        progressText.value = '验证授权合约和代码完整性...'

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

        verificationResult.value = {
          type: verifyData.can_decrypt ? 'success' : 'error',
          authorization: verifyData.authorization.message,
          codeIntegrity: verifyData.code_integrity.message
        }

        if (!verifyData.can_decrypt) {
          showProgress.value = false
          canDecrypt.value = true
          decrypting.value = false
          return
        }

        // 步骤2: 获取解密密钥
        progress.value = 50
        progressText.value = '获取解密密钥...'

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
        progress.value = 80
        progressText.value = '解密模型...'

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
        progressText.value = '解密完成！'

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
          inferenceResult.value = `
            <div class="result-item">
              <h3>YOLOv5推理结果</h3>
              ${data.annotated_image ? `
                <div style="text-align: center; margin-bottom: 20px;">
                  <img src="${data.annotated_image}" alt="检测结果" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
                </div>
              ` : '<p style="text-align: center; color: #e74c3c;">⚠️ 处理后的图像未返回</p>'}
              <p><strong>检测数量:</strong> ${data.detection_count || 0}</p>
              <p><strong>推理时间:</strong> ${data.inference_time ? (data.inference_time * 1000).toFixed(2) : 'N/A'}ms</p>
              <p><strong>模型状态:</strong> <span class="status-badge ${data.model_status}">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></p>
              ${data.detections && data.detections.length > 0 ? `
                <div style="margin-top: 20px;">
                  <h4>检测详情:</h4>
                  <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <thead>
                      <tr style="background: #f8f9fa;">
                        <th style="padding: 8px; border: 1px solid #ddd;">类别</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">置信度</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">边界框</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${data.detections.map(det => `
                        <tr>
                          <td style="padding: 8px; border: 1px solid #ddd;">${det.class_name || 'N/A'}</td>
                          <td style="padding: 8px; border: 1px solid #ddd;">${(det.confidence * 100).toFixed(2)}%</td>
                          <td style="padding: 8px; border: 1px solid #ddd;">[${det.bbox ? det.bbox.map(b => b.toFixed(0)).join(', ') : 'N/A'}]</td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              ` : '<p style="text-align: center; color: #7f8c8d; margin-top: 20px;">未检测到目标</p>'}
            </div>
          `
        } else {
          inferenceResult.value = `
            <div class="result-item">
              <h3>推理结果</h3>
              ${data.annotated_image ? `
                <div style="text-align: center; margin-bottom: 20px;">
                  <img src="${data.annotated_image}" alt="输入图像" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;">
                </div>
              ` : ''}
              <p><strong>预测类别:</strong> ${data.predicted_class}</p>
              <p><strong>置信度:</strong> ${(data.confidence * 100).toFixed(2)}%</p>
              <p><strong>模型状态:</strong> <span class="status-badge ${data.model_status}">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></p>
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
          inferenceResult.value = `
            <div class="result-item">
              <h3>YOLOv5数据集推理结果</h3>
              <div class="accuracy-display">${data.total_detections}</div>
              <p style="text-align: center; color: #7f8c8d;">总检测数量</p>
              <p style="text-align: center; margin-top: 10px;"><strong>处理图片数:</strong> ${data.processed_images}/${data.total_images}</p>
              <p style="text-align: center;"><strong>平均检测数/图片:</strong> ${data.average_detections_per_image ? data.average_detections_per_image.toFixed(2) : '0.00'}</p>
              <p style="text-align: center; margin-top: 10px;"><strong>模型状态:</strong> <span class="status-badge ${data.model_status}">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></p>
              ${data.message ? `<p style="text-align: center; color: #27ae60; margin-top: 10px;">${data.message}</p>` : ''}
              ${data.images && data.images.length > 0 ? `
                <div style="margin-top: 30px;">
                  <h4>处理后的图片（${data.images.length}张）:</h4>
                  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;">
                    ${data.images.map(img => {
                      const count = img.detection_count !== undefined ? img.detection_count : (img.detections ? img.detections.length : 0)
                      return `
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: #f9f9f9;">
                          <div style="text-align: center; margin-bottom: 10px;">
                            <img src="${img.annotated_image}" alt="${img.filename}" style="max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #ccc;">
                          </div>
                          <p style="text-align: center; font-weight: bold; margin-bottom: 5px;">${img.filename}</p>
                          <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">检测到 ${count} 个目标</p>
                          ${img.detections && img.detections.length > 0 ? `
                            <div style="margin-top: 10px; font-size: 0.85em;">
                              ${img.detections.map(det => `
                                <div style="padding: 3px 0; border-bottom: 1px solid #eee;">
                                  <strong>${det.class || det.class_name || 'N/A'}</strong>: ${(det.confidence * 100).toFixed(1)}%
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
              <div class="accuracy-display">${data.accuracy ? data.accuracy.toFixed(2) : '0.00'}%</div>
              <p style="text-align: center; color: #7f8c8d;">数据集准确率</p>
              <p style="text-align: center; margin-top: 10px;"><strong>总样本数:</strong> ${data.total_samples || 0}</p>
              <p style="text-align: center;"><strong>模型状态:</strong> <span class="status-badge ${data.model_status}">${data.model_status === 'decrypted' ? '已解密' : '已加密'}</span></p>
              ${data.model_status === 'encrypted' ? '<p style="text-align: center; color: #e74c3c; margin-top: 10px;">⚠️ 模型未解密，推理精度较低</p>' : ''}
              ${samples.length > 0 ? `
                <div style="margin-top: 30px;">
                  <h4>样本推理结果（显示前${samples.length}个）:</h4>
                  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; margin-top: 15px;">
                    ${samples.map((sample, index) => `
                      <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: #f9f9f9; ${sample.is_correct ? '' : 'border-color: #e74c3c; background: #ffeaea;'}">
                        <div style="text-align: center; margin-bottom: 10px;">
                          <img src="${sample.image}" alt="Sample ${index + 1}" style="max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #ccc;">
                        </div>
                        <div style="font-size: 0.85em;">
                          <p style="margin: 5px 0; font-weight: bold;">真实类别: ${sample.true_class}</p>
                          <p style="margin: 5px 0; ${sample.is_correct ? 'color: #27ae60;' : 'color: #e74c3c;'}">
                            预测类别: ${sample.predicted_class}
                            ${sample.is_correct ? ' ✓' : ' ✗'}
                          </p>
                          <p style="margin: 5px 0; color: #7f8c8d; font-size: 0.9em;">
                            置信度: ${(sample.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    `).join('')}
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
      // 恢复侧边栏状态
      if (window.innerWidth > 768) {
        const saved = localStorage.getItem('sidebarCollapsed')
        sidebarCollapsed.value = saved === 'true'
      } else {
        sidebarCollapsed.value = true
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
      sidebarCollapsed,
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
      toggleSidebar,
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
  padding: 0;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(4, 21, 38, 0.96), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.container {
  max-width: 100%;
  margin: 0;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  overflow: visible;
  display: flex;
  min-height: calc(100vh - 80px);
  position: relative;
}

.sidebar {
  width: 350px;
  min-width: 280px;
  max-width: 400px;
  background: linear-gradient(180deg, rgba(9, 32, 56, 0.95), rgba(4, 19, 34, 0.95));
  color: #e6f1ff;
  padding: 30px 20px;
  overflow-y: auto;
  transition: all 0.3s ease;
  position: relative;
  border-right: 1px solid rgba(88, 178, 255, 0.12);
}

.sidebar.collapsed {
  width: 0;
  min-width: 0;
  padding: 0;
  overflow: visible;
  border-right: none;
}

.sidebar-toggle {
  position: absolute;
  top: 20px;
  right: -40px;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.3), rgba(73, 197, 255, 0.3));
  color: #e6f1ff;
  border: 1px solid rgba(88, 178, 255, 0.2);
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  z-index: 1001;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.sidebar-toggle:hover {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(73, 197, 255, 0.4));
  transform: scale(1.1);
}

.sidebar h2 {
  margin-bottom: 25px;
  font-size: 24px;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 15px;
  color: #e6f1ff;
}

.device-list, .model-list {
  margin-bottom: 30px;
}

.device-list h3, .model-list h3 {
  margin-bottom: 15px;
  font-size: 14px;
  opacity: 0.8;
  color: rgba(214, 232, 255, 0.8);
}

.device-item, .model-item {
  background: rgba(88, 178, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
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

.device-item h3, .model-item h3 {
  font-size: 16px;
  margin-bottom: 5px;
  color: #e6f1ff;
}

.device-item p, .model-item p {
  font-size: 12px;
  opacity: 0.8;
  color: rgba(214, 232, 255, 0.8);
  margin: 3px 0;
}

.model-item.authorized {
  background: rgba(39, 174, 96, 0.15);
  border-left: 3px solid rgba(39, 174, 96, 0.6);
}

.model-item.authorized h3 {
  color: rgba(39, 174, 96, 1);
}

.authorized-models-list {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(88, 178, 255, 0.2);
}

.authorized-models-list h3 {
  margin-bottom: 15px;
  font-size: 14px;
  opacity: 0.8;
  color: rgba(214, 232, 255, 0.8);
}

.empty-message {
  color: rgba(214, 232, 255, 0.6);
  font-size: 12px;
  text-align: center;
  padding: 20px;
}

.loading-message {
  color: rgba(88, 178, 255, 0.8);
  font-size: 12px;
  text-align: center;
  padding: 20px;
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
  font-size: 32px;
  margin-bottom: 10px;
  letter-spacing: 1.4px;
}

.header p {
  color: rgba(214, 232, 255, 0.74);
  margin-top: 5px;
}

.status-bar {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.status-card {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  color: #e6f1ff;
  padding: 20px;
  border-radius: 10px;
  flex: 1;
  min-width: 200px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.status-card h3 {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 10px;
  color: rgba(214, 232, 255, 0.8);
}

.status-card .value {
  font-size: 24px;
  font-weight: bold;
  color: #e6f1ff;
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
}

.contract-warning h3 {
  margin-bottom: 10px;
  color: rgba(255, 193, 7, 1);
}

.contract-warning p {
  margin: 5px 0;
  color: rgba(255, 193, 7, 0.9);
}

.action-section {
  margin-bottom: 30px;
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
  margin: 20px 0;
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
  margin: 20px 0;
  padding: 15px;
  border-radius: 8px;
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
  margin-bottom: 10px;
}

.verification-result p {
  margin: 5px 0;
}

.inference-section {
  margin-top: 30px;
}

.inference-section h2 {
  color: #e6f1ff;
  margin-bottom: 20px;
  font-size: 22px;
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
  padding: 25px;
  margin-top: 20px;
  border: 1px solid rgba(88, 178, 255, 0.12);
}

.result-item {
  margin-bottom: 15px;
  padding: 15px;
  background: rgba(4, 19, 34, 0.6);
  border-radius: 8px;
  color: #e6f1ff;
}

.result-item h3 {
  color: #e6f1ff;
  margin-bottom: 10px;
}

.result-item h4 {
  color: rgba(214, 232, 255, 0.9);
  margin-top: 15px;
  margin-bottom: 10px;
}

.result-item p {
  color: rgba(214, 232, 255, 0.8);
  margin: 8px 0;
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

@media (max-width: 768px) {
  .container {
    flex-direction: row;
    position: relative;
  }

  .sidebar {
    width: 280px;
    max-width: 80%;
    min-width: 0;
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 999;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }

  .sidebar-toggle {
    position: fixed;
    top: 20px;
    left: 20px;
    right: auto;
    border-radius: 8px;
    z-index: 1001;
  }

  .main-content {
    width: 100%;
    padding: 20px 15px;
  }

  .header h1 {
    font-size: 24px;
  }

  .status-bar {
    flex-direction: column;
  }

  .status-card {
    min-width: 100%;
  }
}
</style>

