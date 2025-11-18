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

      <main class="main-content">
        <div class="header">
          <h1>企业级大模型交互平台</h1>
        </div>

        <!-- 顶部状态栏 -->
        <div class="status-bar">
          <div class="status-card">
            <span class="status-label">🕒 当前时间：</span>
            <span class="status-value">{{ currentTime }}</span>
          </div>
          <div class="status-card">
            <span class="status-label">👤 用户身份:</span>
            <select v-model="selectedDepartment" @change="onDepartmentChange" class="department-select">
              <option value="Technical_L3">技术部 (L3)</option>
              <option value="Finance_L4">财务部 (L4)</option>
              <option value="Personnel_L1">人力资源部 (L1)</option>
              <option value="Operations_L2">销售部 (L2)</option>
            </select>
          </div>
          <div class="status-card">
            <span class="status-label">✅ 授权状态:</span>
            <span class="status-value authorized">正常</span>
          </div>
        </div>

        <!-- 用户信息卡片 -->
        <div class="user-info-section">
          <h2>🔰 用户信息</h2>
          <div class="user-attributes">
            <div class="attribute-item">
              <span class="icon">🏢</span>
              <span class="label">用户部门:</span>
              <span class="value">{{ departmentMap[currentUser.department] }}</span>
            </div>
            <div class="attribute-item">
              <span class="icon">📈</span>
              <span class="label">用户职级:</span>
              <span class="value">{{ currentUser.rank }} - {{ currentUser.rankName }}</span>
            </div>
            <div class="attribute-item">
              <span class="icon">🔒</span>
              <span class="label">权限等级:</span>
              <span class="value">{{ currentUser.permission }}</span>
            </div>
            <div class="attribute-item">
              <span class="icon">🔐</span>
              <span class="label">安全级别:</span>
              <span class="value" :class="'clearance-' + currentUser.clearance">{{ currentUser.clearance }}</span>
            </div>
          </div>
        </div>

        <!-- 对话区域 -->
        <div class="chat-section">
          <div class="chat-header">
            <div class="access-control-info">
              <span>🔒 访问控制状态: </span>
              <span :class="['access-status', accessStatus.allowed ? 'normal' : 'restricted']">
                {{ accessStatus.allowed ? '正常' : '受限' }}
              </span>
            </div>
          </div>

          <div class="chat-history" ref="chatHistoryRef">
            <div 
              v-for="(message, index) in messages" 
              :key="index" 
              :class="['message-container', message.sender]"
            >
              <div :class="['chat-bubble', message.sender]">
                {{ message.text }}
              </div>
              <div class="timestamp">{{ message.timestamp }}</div>
            </div>
          </div>

          <div class="chat-input-area">
            <textarea 
              v-model="userInput"
              @keydown.enter.exact="handleSendMessage"
              placeholder="请输入您的问题..."
              rows="1"
              ref="inputRef"
            ></textarea>
            <button @click="handleSendMessage" :disabled="!userInput.trim() || isSending" class="btn btn-primary">
              发送
            </button>
            <button @click="startNewChat" class="btn btn-info">
              新对话
            </button>
          </div>
        </div>

        <!-- 可视化区域 -->
        <div class="visualization-container">
          <div class="visualization-panel">
            <h4>激活锚点降维可视化</h4>
            <div class="chart-container" ref="anchorChartRef"></div>
          </div>
          <div class="visualization-panel">
            <h4>锚点偏移分析</h4>
            <div class="chart-container" ref="steeringChartRef"></div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'

export default {
  name: 'CloudModelAccessControlView',
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
    
    const currentAccessControlType = ref('云侧模型访问控制')
    const currentTime = ref('--')
    const selectedDepartment = ref('Technical_L3')
    const messages = ref([])
    const userInput = ref('')
    const isSending = ref(false)
    const chatTitle = ref('企业级大模型交互平台')
    const accessStatus = ref({ allowed: true })
    
    const chatHistoryRef = ref(null)
    const inputRef = ref(null)
    const anchorChartRef = ref(null)
    const steeringChartRef = ref(null)
    
    let anchorChartInstance = null
    let steeringChartInstance = null
    let timeInterval = null

    // API配置
    const API_BASE = 'http://210.45.71.131:10088'
    
    // 部门名称映射
    const departmentMap = {
      'Technical': '技术部',
      'Finance': '财务部',
      'Personnel': '人力资源部',
      'Operations': '销售部'
    }
    
    // 部门权限配置
    const departmentPermissions = {
      'Technical_L3': {
        department: 'Technical',
        rank: 'L3',
        rankName: '高级工程师',
        permission: '中级',
        clearance: 'CONFIDENTIAL',
        maxResultLength: 1000
      },
      'Finance_L4': {
        department: 'Finance',
        rank: 'L4',
        rankName: '财务总监',
        permission: '高级',
        clearance: 'RESTRICTED',
        maxResultLength: 2000
      },
      'Personnel_L1': {
        department: 'Personnel',
        rank: 'L1',
        rankName: '招聘经理',
        permission: '初级',
        clearance: 'PUBLIC',
        maxResultLength: 500
      },
      'Operations_L2': {
        department: 'Operations',
        rank: 'L2',
        rankName: '运营专员',
        permission: '初级',
        clearance: 'PUBLIC',
        maxResultLength: 500
      }
    }
    
    // 访问控制规则
    const accessControlRules = {
      keywords: {
        '财报': {
          minClearance: 'CONFIDENTIAL',
          message: '⚠️ 您无权访问财报相关信息'
        },
        '财务': {
          minClearance: 'CONFIDENTIAL',
          message: '⚠️ 您无权访问财务相关信息'
        },
        '薪资': {
          minClearance: 'RESTRICTED',
          message: '⚠️ 您无权访问薪资相关信息'
        }
      },
      departmentContent: {
        '财报分析': {
          'Technical': '作为技术部门，您可以查看系统架构相关的财报数据。第三季度系统维护成本降低了12%，主要得益于新的自动化部署流程。',
          'Finance': '作为财务部门，您可以查看完整财务数据。第三季度总收入1.2亿元，同比增长15%，毛利率提升至62%。运营成本降低了8%。',
          'Personnel': '作为人力资源部门，您可以查看人力资源相关的财报数据。第三季度人力成本占总成本的45%，比上季度下降2%。',
          'Operations': '作为销售部门，您可以查看销售业绩相关的财报数据。第三季度销售额达到8000万元，完成季度目标的110%。'
        }
      }
    }
    
    // 当前用户信息
    const currentUser = computed(() => {
      return {
        id: 'U001',
        name: '当前用户',
        ...departmentPermissions[selectedDepartment.value]
      }
    })
    
    // 更新时间
    const updateTime = () => {
      const now = new Date()
      const pad = num => num.toString().padStart(2, '0')
      currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
    }
    
    // 导航到访问控制
    const navigateToAccessControl = (name) => {
      currentAccessControlType.value = name
      const item = accessControlItems.find(item => item.name === name)
      if (item && route.name !== item.route) {
        router.push({ name: item.route })
      }
    }
    
    // 检查访问控制
    const checkAccessControl = (query) => {
      const lowerQuery = query.toLowerCase()
      const clearanceLevels = { 'PUBLIC': 1, 'CONFIDENTIAL': 2, 'RESTRICTED': 3 }
      
      for (const [keyword, rule] of Object.entries(accessControlRules.keywords)) {
        if (lowerQuery.includes(keyword)) {
          if (rule.minClearance) {
            if (clearanceLevels[currentUser.value.clearance] < clearanceLevels[rule.minClearance]) {
              return {
                allowed: false,
                message: rule.message,
                reason: `权限级别不足，需要${rule.minClearance}级别，当前为${currentUser.value.clearance}级别`
              }
            }
          }
        }
      }
      
      return { allowed: true }
    }
    
    // 添加消息
    const addMessage = (sender, text) => {
      const timestamp = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      messages.value.push({ sender, text, timestamp })
      
      nextTick(() => {
        if (chatHistoryRef.value) {
          chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
        }
      })
    }
    
    // 加载欢迎消息
    const loadWelcomeMessage = () => {
      messages.value = []
      const user = currentUser.value
      const welcomeText = `你好，欢迎使用企业级大模型交互平台。\n\n` +
                          `您正在使用的权限配置：\n` +
                          `- 部门: ${departmentMap[user.department]}\n` +
                          `- 职级: ${user.rank} - ${user.rankName}\n` +
                          `- 权限等级: ${user.clearance}\n\n` +
                          `💡 提示：您可以通过上方的下拉菜单切换不同部门的权限配置，体验差异化的访问控制效果。`
      addMessage('ai', welcomeText)
    }
    
    // 发送消息
    const handleSendMessage = async (e) => {
      if (e && e.shiftKey) return
      if (e) e.preventDefault()
      
      const text = userInput.value.trim()
      if (!text || isSending.value) return
      
      addMessage('user', text)
      userInput.value = ''
      isSending.value = true
      
      // 检查访问控制
      const accessCheck = checkAccessControl(text)
      accessStatus.value = accessCheck
      
      // 添加思考中消息
      addMessage('ai', '思考中...')
      const loadingIndex = messages.value.length - 1
      
      try {
        const response = await fetch(`${API_BASE}/api/v1/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: currentUser.value.id,
            department: currentUser.value.department,
            position_level: currentUser.value.rank,
            query: text,
            enable_steering: true
          })
        })
        
        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status} ${response.statusText}`)
        }
        
        const data = await response.json()
        
        // 移除思考中消息
        messages.value.splice(loadingIndex, 1)
        
        let aiResponse
        
        if (!accessCheck.allowed) {
          aiResponse = accessCheck.message + '\n\n' + 
                      `🔒 访问控制原因: ${accessCheck.reason}\n` +
                      `👤 当前用户: ${departmentMap[currentUser.value.department]}, ${currentUser.value.rank}\n` +
                      `📊 权限等级: ${currentUser.value.clearance}`
        } else {
          aiResponse = data.output || '无法生成响应'
          
          const extraInfo = `\n\n---\n用户身份: ${departmentMap[currentUser.value.department]} - ${currentUser.value.rankName}\n激活偏移: ${data.steering_applied ? '已应用' : '未应用'}\nASI分数: ${data.total_asi ? data.total_asi.toFixed(2) : 'N/A'}`
          aiResponse += extraInfo
        }
        
        addMessage('ai', aiResponse)
        
        // 生成可视化
        if (data.activations && data.layer_asi_scores) {
          visualizeAnchors(data.activations, data.layer_asi_scores)
          visualizeSteering(data.layer_asi_scores, data.steering_applied)
        }
        
      } catch (error) {
        // 移除思考中消息
        messages.value.splice(loadingIndex, 1)
        console.error('API调用失败:', error)
        addMessage('ai', `发生错误: ${error.message}\n请检查网络连接和后端服务状态。`)
      } finally {
        isSending.value = false
      }
    }
    
    // 开始新对话
    const startNewChat = () => {
      chatTitle.value = '新对话'
      loadWelcomeMessage()
      accessStatus.value = { allowed: true }
    }
    
    // 部门切换
    const onDepartmentChange = () => {
      loadWelcomeMessage()
      accessStatus.value = { allowed: true }
    }
    
    // 可视化锚点
    const visualizeAnchors = (activations, asiScores) => {
      if (!anchorChartRef.value) return
      
      // 初始化或获取 ECharts 实例
      if (!anchorChartInstance) {
        anchorChartInstance = echarts.init(anchorChartRef.value)
      }
      
      const departments = ['Technical', 'Finance', 'Marketing', 'Personnel']
      const levels = ['L3', 'L4', 'L5']
      const seriesData = []
      
      // 添加查询激活点
      if (activations && Object.keys(activations).length > 0) {
        const firstLayer = Object.keys(activations)[0]
        const queryData = {
          value: [
            activations[firstLayer].slice(0, 200).reduce((a, b) => a + b, 0) / 200,
            activations[firstLayer].slice(200, 400).reduce((a, b) => a + b, 0) / 200
          ],
          name: '查询激活',
          itemStyle: {
            color: 'rgba(255, 99, 132, 1)'
          },
          symbolSize: 15
        }
        
        seriesData.push({
          name: '查询激活',
          type: 'scatter',
          data: [queryData],
          symbolSize: 15,
          itemStyle: {
            color: 'rgba(255, 99, 132, 1)'
          }
        })
      }
      
      // 添加锚点数据
      departments.forEach(dept => {
        const deptData = []
        levels.forEach(level => {
          deptData.push({
            value: [Math.random() * 10 - 5, Math.random() * 10 - 5],
            name: `${dept} ${level}`
          })
        })
        
        seriesData.push({
          name: dept,
          type: 'scatter',
          data: deptData,
          symbolSize: 10,
          itemStyle: {
            color: dept === currentUser.value.department ? 
              'rgba(88, 178, 255, 0.8)' : 'rgba(75, 192, 192, 0.5)'
          }
        })
      })
      
      const option = {
        backgroundColor: 'transparent',
        title: {
          text: '激活锚点降维可视化',
          left: 'center',
          textStyle: {
            color: '#e6f1ff',
            fontSize: 14
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '10%',
          top: '15%'
        },
        xAxis: {
          name: '维度1',
          nameTextStyle: {
            color: '#e6f1ff'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.3)'
            }
          },
          axisLabel: {
            color: '#e6f1ff'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.1)'
            }
          }
        },
        yAxis: {
          name: '维度2',
          nameTextStyle: {
            color: '#e6f1ff'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.3)'
            }
          },
          axisLabel: {
            color: '#e6f1ff'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.1)'
            }
          }
        },
        series: seriesData,
        tooltip: {
          trigger: 'item',
          formatter: '{b}'
        }
      }
      
      anchorChartInstance.setOption(option)
    }
    
    // 可视化锚点偏移
    const visualizeSteering = (asiScores, steeringApplied) => {
      if (!steeringChartRef.value) return
      
      // 初始化或获取 ECharts 实例
      if (!steeringChartInstance) {
        steeringChartInstance = echarts.init(steeringChartRef.value)
      }
      
      const labels = asiScores ? Object.keys(asiScores) : []
      const data = asiScores ? Object.values(asiScores) : []
      
      const option = {
        backgroundColor: 'transparent',
        title: {
          text: `锚点偏移分析 (转向${steeringApplied ? '已' : '未'}应用)`,
          left: 'center',
          textStyle: {
            color: '#e6f1ff',
            fontSize: 14
          }
        },
        grid: {
          left: '15%',
          right: '10%',
          bottom: '15%',
          top: '15%'
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.3)'
            }
          },
          axisLabel: {
            color: '#e6f1ff',
            rotate: 45,
            interval: 0
          },
          splitLine: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          name: 'ASI分数',
          nameTextStyle: {
            color: '#e6f1ff'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.3)'
            }
          },
          axisLabel: {
            color: '#e6f1ff'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(88, 178, 255, 0.1)'
            }
          }
        },
        series: [{
          name: 'ASI分数',
          type: 'bar',
          data: data.map((value, index) => ({
            value,
            itemStyle: {
              color: value > 0.5 ? 'rgba(255, 99, 132, 0.8)' : 
                     value > 0.2 ? 'rgba(255, 205, 86, 0.8)' : 
                     'rgba(75, 192, 192, 0.8)'
            }
          })),
          barWidth: '60%'
        }],
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        }
      }
      
      steeringChartInstance.setOption(option)
    }
    
    // 自动调整输入框高度
    watch(userInput, () => {
      nextTick(() => {
        if (inputRef.value) {
          inputRef.value.style.height = 'auto'
          inputRef.value.style.height = inputRef.value.scrollHeight + 'px'
        }
      })
    })
    
    onMounted(() => {
      updateTime()
      timeInterval = setInterval(updateTime, 1000)
      loadWelcomeMessage()
    })
    
    onUnmounted(() => {
      if (timeInterval) clearInterval(timeInterval)
      if (anchorChartInstance) {
        anchorChartInstance.dispose()
        anchorChartInstance = null
      }
      if (steeringChartInstance) {
        steeringChartInstance.dispose()
        steeringChartInstance = null
      }
    })

    return {
      accessControlItems,
      currentAccessControlType,
      navigateToAccessControl,
      currentTime,
      selectedDepartment,
      currentUser,
      departmentMap,
      messages,
      userInput,
      isSending,
      chatTitle,
      accessStatus,
      chatHistoryRef,
      inputRef,
      anchorChartRef,
      steeringChartRef,
      handleSendMessage,
      startNewChat,
      onDepartmentChange
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
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.header {
  margin-bottom: 0;
}

.header h1 {
  color: #e6f1ff;
  font-size: 24px;
  margin-bottom: 10px;
  letter-spacing: 1.4px;
  font-weight: normal;
}

.status-bar {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
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

.status-value.authorized {
  color: rgba(39, 174, 96, 1);
}

.department-select {
  flex: 1;
  padding: 8px 12px;
  background: rgba(88, 178, 255, 0.2);
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-radius: 6px;
  color: #e6f1ff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.department-select:hover {
  background: rgba(88, 178, 255, 0.3);
}

.department-select option {
  background: rgba(4, 19, 34, 1);
  color: #e6f1ff;
}

.user-info-section {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 2px 24px 12px 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
}

.user-info-section h2 {
  color: #e6f1ff;
  margin-bottom: 20px;
  font-size: 20px;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 10px;
}

.user-attributes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.attribute-item {
  display: flex;
  align-items: center;
  background: rgba(4, 19, 34, 0.6);
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid rgba(88, 178, 255, 0.5);
}

.attribute-item .icon {
  margin-right: 12px;
  font-size: 1.4em;
}

.attribute-item .label {
  font-weight: 600;
  color: rgba(214, 232, 255, 0.7);
  margin-right: 8px;
  font-size: 14px;
}

.attribute-item .value {
  color: #e6f1ff;
  font-weight: 600;
  font-size: 14px;
}

.clearance-PUBLIC {
  color: rgba(39, 174, 96, 1) !important;
}

.clearance-CONFIDENTIAL {
  color: rgba(255, 193, 7, 1) !important;
}

.clearance-RESTRICTED {
  color: rgba(231, 76, 60, 1) !important;
}

.chat-section {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  display: flex;
  flex-direction: column;
  min-height: 400px;
  max-height: 600px;
}

.chat-header {
  padding: 20px 25px;
  border-bottom: 2px solid rgba(88, 178, 255, 0.2);
}

.access-control-info {
  font-size: 14px;
  color: rgba(214, 232, 255, 0.7);
}

.access-status {
  font-weight: 600;
}

.access-status.normal {
  color: rgba(39, 174, 96, 1);
}

.access-status.restricted {
  color: rgba(231, 76, 60, 1);
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: rgba(4, 19, 34, 0.6);
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb {
  background: rgba(88, 178, 255, 0.3);
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background: rgba(88, 178, 255, 0.5);
}

.message-container {
  display: flex;
  flex-direction: column;
}

.message-container.user {
  align-items: flex-end;
}

.message-container.ai {
  align-items: flex-start;
}

.chat-bubble {
  max-width: 80%;
  padding: 12px 18px;
  border-radius: 18px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.chat-bubble.user {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.3), rgba(73, 197, 255, 0.3));
  color: #e6f1ff;
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-bottom-right-radius: 4px;
}

.chat-bubble.ai {
  background: rgba(4, 19, 34, 0.8);
  color: rgba(214, 232, 255, 0.9);
  border: 1px solid rgba(88, 178, 255, 0.15);
  border-bottom-left-radius: 4px;
}

.timestamp {
  font-size: 11px;
  color: rgba(214, 232, 255, 0.5);
  margin-top: 5px;
}

.message-container.user .timestamp {
  text-align: right;
  margin-right: 5px;
}

.message-container.ai .timestamp {
  text-align: left;
  margin-left: 5px;
}

.chat-input-area {
  display: flex;
  padding: 20px;
  border-top: 1px solid rgba(88, 178, 255, 0.2);
  gap: 10px;
}

.chat-input-area textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid rgba(88, 178, 255, 0.2);
  background: rgba(4, 19, 34, 0.6);
  color: #e6f1ff;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  font-family: inherit;
  max-height: 120px;
}

.chat-input-area textarea::placeholder {
  color: rgba(214, 232, 255, 0.5);
}

.chat-input-area textarea:focus {
  outline: none;
  border-color: rgba(88, 178, 255, 0.5);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
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
  background: linear-gradient(135deg, rgba(39, 174, 96, 0.3), rgba(46, 213, 115, 0.3));
  color: #e6f1ff;
  border: 1px solid rgba(39, 174, 96, 0.3);
}

.btn-info:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(39, 174, 96, 0.4), rgba(46, 213, 115, 0.4));
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(39, 174, 96, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.visualization-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.visualization-panel {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
}

.visualization-panel h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #e6f1ff;
  font-size: 16px;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
  padding-bottom: 10px;
}

.chart-container {
  height: 300px;
  width: 100%;
  position: relative;
}

@media (max-width: 1400px) {
  .visualization-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1100px) {
  .container {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
  }
  .user-attributes {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-shell {
    padding: 16px 24px 32px;
  }
  .status-bar {
    flex-direction: column;
  }
  .status-card {
    min-width: 100%;
  }
  .user-attributes {
    grid-template-columns: 1fr;
  }
}
</style>

