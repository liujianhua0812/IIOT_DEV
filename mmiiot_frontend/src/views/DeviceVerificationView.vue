<template>
  <div class="page-shell">
    <div class="container">
      <aside class="sidebar">
        <div class="system-header">
          <div class="system-title">设备可信认证系统</div>
        </div>

        <div 
          v-for="deviceType in deviceTypes" 
          :key="deviceType.type"
          class="device-category"
          :class="{ active: currentDeviceType === deviceType.type }"
          @click="selectDeviceType(deviceType.type)"
        >
          {{ deviceType.icon }} {{ deviceType.name }}（{{ deviceType.protocol }}）
        </div>
      </aside>

      <main class="main-content">
        <div class="device-verification-panel">
          <div class="panel">
            <div class="device-header">
              <div class="device-name">{{ currentDeviceName }}</div>
            </div>
            
            <div class="device-image-container">
              <img 
                v-if="deviceImageUrl" 
                class="device-image" 
                :src="deviceImageUrl" 
                alt="设备图像" 
              />
            </div>

            <!-- 验证流程状态面板 -->
            <div class="dashboard-panel">
              <h3>验证状态</h3>
              <div class="verification-steps">
                <div class="step-indicator">
                  <div 
                    v-for="(step, index) in verificationSteps" 
                    :key="index"
                    class="step"
                    :class="step.status"
                    :id="`step-${index + 1}`"
                  >
                    <div class="step-number">{{ index + 1 }}</div>
                    <div class="step-title">{{ step.title }}</div>
                    <div class="step-status" :id="`step-${index + 1}-status`">{{ step.statusText }}</div>
                    <div class="step-description">{{ step.description }}</div>
                  </div>
                </div>
                
                <div class="progress-container">
                  <div 
                    class="progress-bar" 
                    :style="{ width: `${verificationProgress}%` }"
                  ></div>
                </div>
                
                <div 
                  class="result" 
                  :class="verificationResultClass"
                  id="verification-result"
                >
                  {{ verificationResultText }}
                </div>
              </div>
            </div>

            <div class="simulation-buttons">
              <button 
                v-for="(btn, index) in simulationButtons" 
                :key="index"
                @click="handleSimulation(btn.scenario)"
              >
                {{ btn.label }}
              </button>
            </div>

            <div class="device-output">
              <h4>设备验证数据</h4>
              <div class="output-item">
                <div class="output-label">时空频指纹:</div>
                <div class="output-value" id="output-spacetime-fingerprint">{{ deviceOutput.spacetimeFingerprint }}</div>
              </div>
              <div 
                class="output-item" 
                id="device-fingerprint-container"
                style="display: flex; align-items: center; flex-wrap: nowrap; width: 100%; white-space: nowrap; overflow: visible;"
              >
                <div class="output-label" style="margin-right: 10px; min-width: 60px; flex-shrink: 0; display: inline-block;">设备指纹:</div>
                <div 
                  class="output-value" 
                  id="output-device-fingerprint"
                  style="flex-shrink: 1; overflow: hidden; text-overflow: ellipsis; display: inline-block;"
                >
                  {{ deviceOutput.deviceFingerprint }}
                </div>
              </div>
              <div 
                class="output-item" 
                id="data-fingerprint-container"
                style="display: flex; align-items: center; flex-wrap: nowrap; width: 100%; white-space: nowrap; overflow: visible;"
              >
                <div class="output-label" style="margin-right: 10px; min-width: 60px; flex-shrink: 0; display: inline-block;">数据指纹:</div>
                <div 
                  class="output-value" 
                  id="output-hash"
                  style="flex-shrink: 1; overflow: hidden; text-overflow: ellipsis; min-width: 0; display: inline-block;"
                >
                  {{ deviceOutput.dataFingerprint }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="history-panel">
          <h3>历史验证记录</h3>
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>结果</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in historyRecords" :key="index">
                <td>{{ record.time }}</td>
                <td :class="record.is_trusted ? 'status-ok' : 'status-fail'"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import CryptoJS from 'crypto-js'

export default {
  name: 'DeviceVerificationView',
  setup() {
    const route = useRoute()
    
    const deviceTypes = [
      { type: '海康工业相机', name: '海康工业相机', modal: 'EtherNET', protocol: 'Ethernet Protocol', icon: '📷' },
      { type: '西门子电机驱动器', name: '西门子电机驱动器', modal: 'profiNet', protocol: 'ProfiNet Protocol', icon: '⚙️' },
      { type: 'TSN交换机', name: 'TSN交换机', modal: 'TSN', protocol: 'TSN Protocol', icon: '🌐' },
      { type: '温度传感器', name: '温度传感器', modal: 'modbus', protocol: 'Modbus Protocol', icon: '🌡️' },
      { type: 'EtherCat电机驱动器', name: 'EtherCat电机驱动器', modal: 'EtherCat', protocol: 'EtherCat Protocol', icon: '🔌' }
    ]

    const currentDeviceType = ref('')
    const currentDeviceId = ref(null)
    const currentDeviceName = ref('请选择设备')
    const deviceImageUrl = ref('')
    const currentDeviceData = ref(null)
    
    const deviceOutput = reactive({
      spacetimeFingerprint: '-',
      deviceFingerprint: '-',
      dataFingerprint: '-'
    })

    const verificationSteps = reactive([
      { title: '时空频验证', status: '', statusText: '等待验证', description: '验证时空频信息合法性' },
      { title: '设备指纹验证', status: '', statusText: '等待验证', description: '验证设备指纹合法性' },
      { title: '数据指纹验证', status: '', statusText: '等待验证', description: '验证数据指纹合法性' }
    ])

    const verificationProgress = ref(0)
    const verificationResultClass = ref('trusted')
    const verificationResultText = ref('请选择设备以开始验证')
    
    const historyRecords = ref([])
    
    const simulationButtons = [
      { label: '1. 空间信息伪造', scenario: 'ip_spoof' },
      { label: '2. 时间信息伪造', scenario: 'time_invalid' },
      { label: '3. 设备伪造', scenario: 'mac_spoof' },
      { label: '4. 数据完整性破坏', scenario: 'data_tamper' },
      { label: '5. 正常通信（完整性校验通过）', scenario: 'normal' }
    ]

    let verificationTimer = null
    let stepTimers = {}
    let backendVerificationResults = null
    let verificationOutput = null
    const stepTime = 2000

    // API配置
    // 固定后端地址
    const API_BASE = 'http://210.45.71.131:5001/api'
    
    console.log('API_BASE:', API_BASE)

    // API 工具函数
    const apiGet = async (url) => {
      let fullUrl
      if (url.startsWith('http')) {
        fullUrl = url
      } else if (url.startsWith('/api')) {
        // 如果 URL 已经包含 /api，直接拼接到基地址（不重复 /api）
        fullUrl = `http://210.45.71.131:5001${url}`
      } else {
        // 如果 URL 不包含 /api，使用 API_BASE
        fullUrl = `${API_BASE}${url.startsWith('/') ? url : '/' + url}`
      }
      console.log('API GET:', fullUrl)
      const res = await fetch(fullUrl)
      if (!res.ok) {
        const errorText = await res.text()
        console.error('API GET 错误:', res.status, errorText)
        throw new Error(`请求失败: ${res.status} ${errorText}`)
      }
      return await res.json()
    }

    const apiPost = async (url, data) => {
      let fullUrl
      if (url.startsWith('http')) {
        fullUrl = url
      } else if (url.startsWith('/api')) {
        // 如果 URL 已经包含 /api，直接拼接到基地址（不重复 /api）
        fullUrl = `http://210.45.71.131:5001${url}`
      } else {
        // 如果 URL 不包含 /api，使用 API_BASE
        fullUrl = `${API_BASE}${url.startsWith('/') ? url : '/' + url}`
      }
      console.log('API POST:', fullUrl, data)
      const res = await fetch(fullUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) {
        const errorText = await res.text()
        console.error('API POST 错误:', res.status, errorText)
        throw new Error(`请求失败: ${res.status} ${errorText}`)
      }
      return await res.json()
    }

    // 计算时空频指纹 (IP + 时间的哈希)
    const calculateSpacetimeFingerprint = (ip, timestamp) => {
      const combined = ip + '|' + timestamp
      return CryptoJS.MD5(combined).toString()
    }

    // 计算设备指纹
    const calculateDeviceFingerprint = (ip, mac) => {
      const combined = ip + '|' + mac
      return CryptoJS.MD5(combined).toString()
    }

    // 重置验证流程
    const resetVerification = () => {
      if (verificationTimer) {
        clearTimeout(verificationTimer)
        verificationTimer = null
      }

      Object.keys(stepTimers).forEach(key => {
        clearInterval(stepTimers[key])
        delete stepTimers[key]
      })

      verificationSteps.forEach((step, index) => {
        step.status = ''
        step.statusText = '等待验证'
      })

      verificationProgress.value = 0
      verificationResultClass.value = 'trusted'
      verificationResultText.value = '准备验证...'

      deviceOutput.deviceFingerprint = '-'
      deviceOutput.dataFingerprint = '-'
    }

    // 更新步骤UI
    const updateStepUI = (stepNumber, status) => {
      const step = verificationSteps[stepNumber - 1]
      if (step) {
        step.status = status
        switch (status) {
          case 'active':
            step.statusText = '验证中...'
            startStepTimer(stepNumber)
            break
          case 'completed':
            step.statusText = '验证通过'
            clearStepTimer(stepNumber)
            break
          case 'failed':
            step.statusText = '验证失败'
            clearStepTimer(stepNumber)
            break
        }
      }
    }

    // 开始步骤计时器
    const startStepTimer = (stepNumber) => {
      clearStepTimer(stepNumber)
      let remainingTime = stepTime / 1000
      const timerId = setInterval(() => {
        remainingTime -= 0.1
        if (remainingTime <= 0) {
          clearStepTimer(stepNumber)
        }
      }, 100)
      stepTimers[stepNumber] = timerId
    }

    // 清除步骤计时器
    const clearStepTimer = (stepNumber) => {
      if (stepTimers[stepNumber]) {
        clearInterval(stepTimers[stepNumber])
        delete stepTimers[stepNumber]
      }
    }

    // 时空频验证
    const validateSpatialTemporalFrequency = () => {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (backendVerificationResults && backendVerificationResults.spatial_temporal) {
            const isValid = backendVerificationResults.spatial_temporal.valid
            const ipValid = backendVerificationResults.spatial_temporal.ip_valid
            const timeValid = backendVerificationResults.spatial_temporal.time_valid
            const message = backendVerificationResults.spatial_temporal.message

            // 更新步骤状态文本
            if (verificationSteps[0]) {
              verificationSteps[0].statusText = message || (isValid ? '验证通过' : '验证失败')
            }

            if (verificationOutput) {
              // 计算并显示时空频指纹
              if (verificationOutput.ip && verificationOutput.timestamp) {
                const receivedFingerprint = calculateSpacetimeFingerprint(verificationOutput.ip, verificationOutput.timestamp);
                
                if (isValid && currentDeviceData.value) {
                  // 验证通过，显示正确的时空频指纹
                  deviceOutput.spacetimeFingerprint = receivedFingerprint;
                } else if (!isValid && currentDeviceData.value) {
                  // 验证失败，显示接收到的指纹和正确的指纹
                  const correctFingerprint = calculateSpacetimeFingerprint(currentDeviceData.value.ip, currentDeviceData.value.timestamp);
                  deviceOutput.spacetimeFingerprint = `接收值: ${receivedFingerprint} | 合法值: ${correctFingerprint}`;
                } else {
                  // 其他情况，只显示接收到的指纹
                  deviceOutput.spacetimeFingerprint = receivedFingerprint;
                }
              }

              // 保留原有的详细信息显示逻辑
              if (!ipValid && currentDeviceData.value) {
                const originalIp = currentDeviceData.value.ip || '未知'
                // 这里我们不再直接显示IP，而是保持时空频指纹的显示
              }

              if (!timeValid) {
                const now = new Date()
                const before10min = new Date(now.getTime() - 10 * 60 * 1000)
                const after5min = new Date(now.getTime() + 5 * 60 * 1000)
                const formatTime = (date) => {
                  return date.toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                  }).replace(/\//g, '-')
                }
                // 我们不再直接显示时间，时空频指纹已经包含了时间信息
              }
            }

            resolve(isValid)
          } else {
            if (verificationSteps[0]) {
              verificationSteps[0].statusText = '验证服务不可用'
            }
            resolve(false)
          }
        }, stepTime)
      })
    }

    // 设备指纹验证
    const validateDeviceFingerprint = () => {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (backendVerificationResults && backendVerificationResults.device_fingerprint) {
            const isValid = backendVerificationResults.device_fingerprint.valid
            const macValid = backendVerificationResults.device_fingerprint.mac_valid
            const fpValid = backendVerificationResults.device_fingerprint.fingerprint_valid
            const message = backendVerificationResults.device_fingerprint.message

            // 更新步骤状态文本
            if (verificationSteps[1]) {
              verificationSteps[1].statusText = message || (isValid ? '验证通过' : '验证失败')
            }

            if (verificationOutput) {
              if (!isValid && verificationOutput.device_fingerprint) {
                const validFingerprint = backendVerificationResults.device_fingerprint.valid_fingerprint || 
                  (currentDeviceData.value ? calculateDeviceFingerprint(currentDeviceData.value.ip, currentDeviceData.value.mac) : '未知')
                deviceOutput.deviceFingerprint = `接收值: ${verificationOutput.device_fingerprint} | 合法值: ${validFingerprint}`
              } else if (verificationOutput.device_fingerprint) {
                deviceOutput.deviceFingerprint = verificationOutput.device_fingerprint
              }
            }

            resolve(isValid)
          } else {
            if (verificationSteps[1]) {
              verificationSteps[1].statusText = '验证服务不可用'
            }
            resolve(false)
          }
        }, stepTime)
      })
    }

    // 数据指纹验证
    const validateDataFingerprint = () => {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (backendVerificationResults && backendVerificationResults.data_fingerprint) {
            const isValid = backendVerificationResults.data_fingerprint.valid
            const message = backendVerificationResults.data_fingerprint.message

            // 更新步骤状态文本
            if (verificationSteps[2]) {
              verificationSteps[2].statusText = message || (isValid ? '验证通过' : '验证失败')
            }

            if (verificationOutput) {
              if (!isValid) {
                const sentHash = verificationOutput.data_hash || '未知'
                const correctHash = backendVerificationResults.data_fingerprint.correct_hash || '未知'
                deviceOutput.dataFingerprint = `发送值: ${sentHash} | 验证值: ${correctHash}`
              } else {
                deviceOutput.dataFingerprint = verificationOutput.data_hash || '-'
              }
            }

            resolve(isValid)
          } else {
            if (verificationSteps[2]) {
              verificationSteps[2].statusText = '验证服务不可用'
            }
            resolve(false)
          }
        }, stepTime)
      })
    }

    // 执行验证步骤
    const executeStep = (stepNumber) => {
      if (stepNumber > 3) {
        verificationResultClass.value = 'trusted'
        verificationResultText.value = '所有验证通过！设备验证成功。'
        return
      }

      updateStepUI(stepNumber, 'active')

      let validationPromise
      switch (stepNumber) {
        case 1:
          validationPromise = validateSpatialTemporalFrequency()
          break
        case 2:
          validationPromise = validateDeviceFingerprint()
          break
        case 3:
          validationPromise = validateDataFingerprint()
          break
      }

      validationPromise.then(isValid => {
        if (isValid) {
          updateStepUI(stepNumber, 'completed')
          verificationProgress.value = (stepNumber / 3) * 100

          if (stepNumber < 3) {
            verificationTimer = setTimeout(() => {
              executeStep(stepNumber + 1)
            }, stepTime)
          } else {
            verificationResultClass.value = 'trusted'
            verificationResultText.value = '所有验证通过！设备验证成功。'
          }
        } else {
          updateStepUI(stepNumber, 'failed')
          verificationResultClass.value = 'untrusted'
          const stepNames = ['时空频', '设备指纹', '数据指纹']
          verificationResultText.value = `验证失败：${stepNames[stepNumber - 1]} 验证不通过`
        }
      })
    }

    // 开始验证流程
    const startVerification = () => {
      resetVerification()
      executeStep(1)
    }

    // 选择设备类型
    const selectDeviceType = async (deviceType) => {
      currentDeviceType.value = deviceType
      currentDeviceName.value = deviceType
      currentDeviceId.value = null // 先重置

      try {
        const res = await apiGet('/api/devices')
        console.log('获取设备列表成功:', res)
        const device = res.devices.find(dev => dev.type === deviceType)
        console.log('查找设备类型:', deviceType, '找到设备:', device)
        if (device) {
          currentDeviceId.value = device.id
          console.log('设置当前设备ID:', currentDeviceId.value)
          await loadDeviceDetails(device.id)
        } else {
          currentDeviceId.value = null
          deviceImageUrl.value = ''
          resetVerification()
          alert(`未找到类型为"${deviceType}"的设备`)
        }
      } catch (err) {
        console.error('获取设备失败:', err)
        alert('获取设备列表失败: ' + err.message)
      }
    }

    // 加载设备详情
    const loadDeviceDetails = async (deviceId) => {
      try {
        const dev = await apiGet(`/api/devices/${deviceId}`)
        currentDeviceData.value = dev

        // 根据设备类型设置默认图片
        if (dev.type) {
          const imageMap = {
            '海康工业相机': '/static/images/海康工业相机.png',
            '西门子电机驱动器': '/static/images/西门子电机驱动器.jpg',
            'TSN交换机': '/static/images/TSN交换机.avif',
            '温度传感器': '/static/images/温度传感器.jpg',
            'EtherCat电机驱动器': '/static/images/电机驱动器.jpg'
          }
          
          const imagePath = imageMap[dev.type] || '/static/images/default.png'
          deviceImageUrl.value = imagePath + '?t=' + Date.now()
        } else if (dev.image_url) {
          deviceImageUrl.value = dev.image_url + '?t=' + Date.now()
        } else {
          deviceImageUrl.value = '/static/images/default.png'
        }

        deviceOutput.spacetimeFingerprint = '-'
        deviceOutput.deviceFingerprint = '-'
        deviceOutput.dataFingerprint = '-'

        const history = await apiGet(`/api/devices/${deviceId}/history`)
        historyRecords.value = history.slice(0, 20)

        resetVerification()
        verificationResultText.value = '就绪：点击上方按钮进行验证'
      } catch (err) {
        console.error('加载设备详情失败:', err)
      }
    }

    // 处理模拟按钮点击
    const handleSimulation = async (scenario) => {
      console.log('点击模拟按钮，当前设备ID:', currentDeviceId.value)
      if (!currentDeviceId.value) {
        alert('请先选择一个设备！当前设备ID为空')
        return
      }

      try {
        const result = await apiPost(`/api/devices/${currentDeviceId.value}/verify`, {
          scenario: scenario
        })

        backendVerificationResults = result.verification_results
        verificationOutput = result.output

        deviceOutput.spacetimeFingerprint = '-'
        deviceOutput.deviceFingerprint = '-'
        deviceOutput.dataFingerprint = '-'

        startVerification()

        const history = await apiGet(`/api/devices/${currentDeviceId.value}/history`)
        historyRecords.value = history.slice(0, 20)
      } catch (err) {
        console.error('模拟验证失败:', err)
        alert('模拟验证失败: ' + err.message)
      }
    }

    // 从路由参数初始化设备类型
    onMounted(() => {
      const deviceType = route.params.deviceType
      if (deviceType) {
        selectDeviceType(deviceType)
      }
    })

    return {
      deviceTypes,
      currentDeviceType,
      currentDeviceName,
      deviceImageUrl,
      deviceOutput,
      verificationSteps,
      verificationProgress,
      verificationResultClass,
      verificationResultText,
      historyRecords,
      simulationButtons,
      selectDeviceType,
      handleSimulation
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
  display: flex;
  gap: 24px;
}

.device-verification-panel {
  flex: 3;
  display: flex;
  flex-direction: column;
}

.panel {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  flex: 1;
}

.device-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.device-name {
  font-size: 20px;
  font-weight: 600;
  color: #e6f1ff;
}

.device-image-container {
  width: 220px;
  height: 180px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(128, 214, 255, 0.05);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.device-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.dashboard-panel {
  background: rgba(4, 19, 34, 0.6);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.dashboard-panel h3 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #e6f1ff;
}

.verification-steps {
  margin-top: 20px;
}

.step-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  margin-bottom: 30px;
  padding: 0 10px;
}

.step {
  text-align: center;
  position: relative;
  z-index: 2;
  flex: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(128, 214, 255, 0.2);
  color: rgba(230, 241, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin: 0 auto 10px;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background: #58b2ff;
  color: white;
  transform: scale(1.1);
  animation: pulse 1.5s infinite;
}

.step.completed .step-number {
  background: #4caf50;
  color: white;
}

.step.completed .step-number::after {
  content: '✓';
  font-size: 18px;
}

.step.failed .step-number {
  background: #f44336;
  color: white;
}

.step-title {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 14px;
  color: #e6f1ff;
}

.step-status {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
  margin-bottom: 5px;
}

.step-status.active {
  color: #58b2ff;
}

.step-status.completed {
  color: #4caf50;
}

.step-status.failed {
  color: #f44336;
}

.step-description {
  font-size: 11px;
  color: rgba(214, 232, 255, 0.5);
}

.progress-container {
  height: 8px;
  background: rgba(128, 214, 255, 0.1);
  border-radius: 4px;
  margin-bottom: 15px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #4caf50;
  width: 0%;
  transition: width 0.5s ease-in-out;
}

.result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  font-size: 16px;
}

.result.trusted {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.result.untrusted {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.simulation-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin: 16px 0;
}

.simulation-buttons button {
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(128, 214, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  background: rgba(128, 214, 255, 0.12);
  color: #e6f1ff;
  transition: all 0.3s ease;
}

.simulation-buttons button:hover {
  background: rgba(128, 214, 255, 0.2);
  border-color: rgba(128, 214, 255, 0.35);
}

.simulation-buttons button:nth-child(1) { 
  background: rgba(255, 234, 167, 0.2);
  border-color: rgba(255, 234, 167, 0.3);
}
.simulation-buttons button:nth-child(2) { 
  background: rgba(253, 203, 110, 0.2);
  border-color: rgba(253, 203, 110, 0.3);
}
.simulation-buttons button:nth-child(3) { 
  background: rgba(225, 112, 85, 0.2);
  border-color: rgba(225, 112, 85, 0.3);
}
.simulation-buttons button:nth-child(4) { 
  background: rgba(214, 48, 49, 0.2);
  border-color: rgba(214, 48, 49, 0.3);
}
.simulation-buttons button:nth-child(5) { 
  background: rgba(0, 184, 148, 0.2);
  border-color: rgba(0, 184, 148, 0.3);
}

.device-output {
  margin-top: 16px;
  padding: 12px;
  background: rgba(4, 19, 34, 0.6);
  border-radius: 8px;
  font-size: 14px;
  border: 1px solid rgba(88, 178, 255, 0.1);
}

.device-output h4 {
  margin-bottom: 8px;
  color: #e6f1ff;
  font-weight: 600;
}

.output-item {
  display: flex;
  margin: 6px 0;
}

.output-label {
  width: 80px;
  color: rgba(214, 232, 255, 0.7);
  flex-shrink: 0;
}

.output-value {
  flex: 1;
  font-family: monospace;
  color: #e6f1ff;
  word-break: break-all;
}

.history-panel {
  width: 320px;
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  flex-shrink: 0;
  position: sticky;
  top: 20px;
  height: fit-content;
}

.history-panel h3 {
  margin-bottom: 16px;
  color: #e6f1ff;
  font-weight: 600;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th, td {
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
  color: rgba(214, 232, 255, 0.8);
}

th {
  color: rgba(214, 232, 255, 0.9);
  font-weight: 600;
}

.status-ok::before { 
  content: "✅"; 
}

.status-fail::before { 
  content: "❌"; 
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@media (max-width: 1100px) {
  .main-content {
    flex-direction: column;
  }
  .history-panel {
    width: 100%;
    position: relative;
  }
}
</style>

