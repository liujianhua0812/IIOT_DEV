<script setup>
import { onMounted, ref, nextTick } from 'vue'
import MetricsGrid from '../components/home/MetricsGrid.vue'
import { fetchHomeOverview, saveTopologyLayout, loadTopologyLayout } from '../services/api'

const metrics = ref({})
const loading = ref(true)
const errorMessage = ref('')
const deleteMessage = ref('')

// 设备类型计数器，用于生成唯一名称
const deviceCounters = ref({
  'TSN交换机': 1,
  '工控机': 1,
  '工业相机': 1,
  'PLC': 1,
  '机械臂控制器': 1,
  '可信网关': 1,
  '区块链节点': 1,
})

// 节点ID计数器
let nodeIdCounter = 0

// 初始化节点，添加唯一ID、固定状态和原始标签
const initialNodes = [
  { baseLabel: 'TSN交换机', x: 18, y: 46, color: '#4cc9f0', type: 'switch' },
  { baseLabel: '工控机', x: 36, y: 38, color: '#4361ee', type: 'monitor' },
  { baseLabel: '工业相机', x: 28, y: 68, color: '#3a0ca3', type: 'camera' },
  { baseLabel: 'PLC', x: 52, y: 60, color: '#f72585', type: 'plc' },
  { baseLabel: '机械臂控制器', x: 61, y: 33, color: '#ffba08', type: 'robot' },
  { baseLabel: '可信网关', x: 77, y: 48, color: '#06d6a0', type: 'shield' },
  { baseLabel: '区块链节点', x: 90, y: 44, color: '#ff6b6b', type: 'chain' },
]

// 创建节点，包含唯一ID和标签
const createNode = (nodeData) => {
  const counter = deviceCounters.value[nodeData.baseLabel] || 1
  const label = counter === 1 ? nodeData.baseLabel : `${nodeData.baseLabel}${counter}`
  deviceCounters.value[nodeData.baseLabel] = counter + 1
  
  return {
    id: `node_${nodeIdCounter++}`,
    baseLabel: nodeData.baseLabel,
    label: label,
    x: nodeData.x,
    y: nodeData.y,
    color: nodeData.color,
    type: nodeData.type,
    fixed: false, // 是否固定位置
  }
}

const topologyNodes = ref(initialNodes.map(createNode))

// 全局固定状态
const allNodesFixed = ref(false)

// 控制按钮显示/隐藏状态（默认隐藏）
const showActionButtons = ref(false)

// 切换按钮显示/隐藏，隐藏时如果位置未固定则先固定
const toggleActionButtonsVisibility = () => {
  // 如果要隐藏按钮，且当前位置未固定，先固定位置
  if (showActionButtons.value && !allNodesFixed.value) {
    toggleFixAllNodes()
  }
  // 切换显示/隐藏状态
  showActionButtons.value = !showActionButtons.value
}

// 拖拽相关状态
const draggingNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const lineVisualRef = ref(null)

// 编辑名称相关状态
const editingNodeId = ref(null) // 正在编辑的图块ID
const editingLabel = ref('') // 正在编辑的标签文本

// 连接线相关状态
let connectionLineIdCounter = 0
const connectionLines = ref([])
const draggingLineEnd = ref(null) // 正在拖拽的连接线端点：'start' | 'end' | null
const draggingLine = ref(null) // 正在拖拽的连接线
const lineDragOffset = ref({ x: 0, y: 0 })
const hoveredLineId = ref(null) // 当前鼠标悬浮的连接线ID

const topologyLinks = [
  ['camera', 'switch'],
  ['plc', 'switch'],
  ['robot', 'edge'],
  ['switch', 'edge'],
  ['edge', 'gateway'],
  ['gateway', 'blockchain'],
]

const deviceIcons = {
  plc: '/plc.svg',
  switch: '/switch.svg',
  camera: '/camera.svg',
  monitor: '/monitor.svg',
  robot: '/robot-arm.png',
  shield: '/indicator.svg',
  chain: '⛓',
}

const isSvgPath = (icon) => typeof icon === 'string' && icon.endsWith('.svg')
const isImagePath = (icon) => typeof icon === 'string' && (icon.endsWith('.svg') || icon.endsWith('.png') || icon.endsWith('.jpg') || icon.endsWith('.jpeg'))

const getNodeStyle = (node) => ({
  left: `${node.x}%`,
  top: `${node.y}%`,
  '--node-color': node.color,
  cursor: node.fixed ? 'default' : 'move',
  opacity: node.fixed ? 0.8 : 1,
})

// 开始拖拽
const startDrag = (event, node) => {
  if (node.fixed) return
  
  event.preventDefault()
  draggingNode.value = node
  
  const rect = lineVisualRef.value.getBoundingClientRect()
  const nodeX = (rect.width * node.x) / 100
  const nodeY = (rect.height * node.y) / 100
  
  dragOffset.value = {
    x: event.clientX - rect.left - nodeX,
    y: event.clientY - rect.top - nodeY,
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

// 拖拽中
const onDrag = (event) => {
  if (!draggingNode.value || !lineVisualRef.value) return
  
  const rect = lineVisualRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left - dragOffset.value.x
  const y = event.clientY - rect.top - dragOffset.value.y
  
  // 限制在可视区域内 (0% - 100%)
  const newX = Math.max(0, Math.min(100, (x / rect.width) * 100))
  const newY = Math.max(0, Math.min(100, (y / rect.height) * 100))
  
  draggingNode.value.x = newX
  draggingNode.value.y = newY
}

// 停止拖拽
const stopDrag = () => {
  draggingNode.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  
  // 如果当前是固定状态，保存布局（虽然固定状态下不应该能拖拽，但为了保险起见）
  if (allNodesFixed.value) {
    saveLayout()
  }
}

// 复制节点
const duplicateNode = (node) => {
  const counter = deviceCounters.value[node.baseLabel] || 1
  const label = `${node.baseLabel}${counter}`
  deviceCounters.value[node.baseLabel] = counter + 1
  
  const newNode = {
    id: `node_${nodeIdCounter++}`,
    baseLabel: node.baseLabel,
    label: label,
    x: node.x + 2, // 稍微偏移位置
    y: node.y + 2,
    color: node.color,
    type: node.type,
    fixed: allNodesFixed.value, // 继承当前的全局固定状态
  }
  
  topologyNodes.value.push(newNode)
  
  // 如果当前是固定状态，保存布局
  if (allNodesFixed.value) {
    saveLayout()
  }
}

// 保存图块和连接线布局到后端数据库
const saveLayout = async () => {
  try {
    const layoutData = {
      nodes: topologyNodes.value.map(node => ({
        id: node.id,
        baseLabel: node.baseLabel,
        label: node.label,
        x: node.x,
        y: node.y,
        color: node.color,
        type: node.type,
        fixed: node.fixed,
      })),
      lines: connectionLines.value.map(line => ({
        id: line.id,
        startX: line.startX,
        startY: line.startY,
        endX: line.endX,
        endY: line.endY,
      })),
      deviceCounters: deviceCounters.value,
      nodeIdCounter: nodeIdCounter,
      connectionLineIdCounter: connectionLineIdCounter,
    }
    
    const response = await saveTopologyLayout(layoutData)
    console.log('布局已保存到数据库:', response.data)
    deleteMessage.value = '布局已保存到数据库'
    setTimeout(() => {
      deleteMessage.value = ''
    }, 2000)
  } catch (error) {
    console.error('保存布局失败:', error)
    deleteMessage.value = `保存失败: ${error.response?.data?.error || error.message}`
    setTimeout(() => {
      deleteMessage.value = ''
    }, 3000)
  }
}

// 从后端数据库加载图块和连接线布局
const loadLayout = async () => {
  try {
    const response = await loadTopologyLayout()
    const layoutData = response.data
    
    // 如果没有数据，返回false使用默认布局
    if (!layoutData || (!layoutData.nodes || layoutData.nodes.length === 0)) {
      console.log('数据库中没有保存的布局，使用默认布局')
      return false
    }
    
    // 恢复设备计数器
    if (layoutData.deviceCounters && Object.keys(layoutData.deviceCounters).length > 0) {
      deviceCounters.value = layoutData.deviceCounters
    }
    
    // 恢复节点ID计数器
    if (layoutData.nodeIdCounter !== undefined && layoutData.nodeIdCounter > 0) {
      nodeIdCounter = layoutData.nodeIdCounter
    }
    
    // 恢复连接线ID计数器
    if (layoutData.connectionLineIdCounter !== undefined && layoutData.connectionLineIdCounter > 0) {
      connectionLineIdCounter = layoutData.connectionLineIdCounter
    }
    
    // 恢复图块位置
    if (layoutData.nodes && layoutData.nodes.length > 0) {
      topologyNodes.value = layoutData.nodes.map(node => ({
        ...node,
        // 确保所有必要的属性都存在
        fixed: node.fixed || false,
      }))
      console.log(`已加载 ${layoutData.nodes.length} 个图块`)
    }
    
    // 恢复连接线
    if (layoutData.lines && layoutData.lines.length > 0) {
      connectionLines.value = layoutData.lines.map(line => ({
        ...line,
      }))
      console.log(`已加载 ${layoutData.lines.length} 条连接线`)
    }
    
    // 恢复全局固定状态（如果所有节点都是固定的，则设置为固定状态）
    if (topologyNodes.value.length > 0) {
      const allFixed = topologyNodes.value.every(node => node.fixed)
      allNodesFixed.value = allFixed
    }
    
    console.log('布局已从数据库加载成功')
    return true
  } catch (error) {
    console.error('加载布局失败:', error)
    // 加载失败时使用默认布局
    return false
  }
}

// 一键固定/取消固定所有节点位置
const toggleFixAllNodes = () => {
  allNodesFixed.value = !allNodesFixed.value
  topologyNodes.value.forEach(node => {
    node.fixed = allNodesFixed.value
  })
  
  // 当固定位置时，保存布局
  if (allNodesFixed.value) {
    saveLayout()
  }
}

// 双击复制节点（只在图标区域双击时触发）
const handleDoubleClick = (node, event) => {
  // 如果双击的是标签区域，不触发复制
  if (event.target.classList.contains('device-node-label')) {
    return
  }
  duplicateNode(node)
}

// 开始编辑图块名称
const startEditLabel = (node, event) => {
  // 如果位置已固定，不允许编辑
  if (allNodesFixed.value) {
    return
  }
  event.stopPropagation()
  editingNodeId.value = node.id
  editingLabel.value = node.label
}

// 保存编辑的图块名称
const saveEditLabel = (node) => {
  if (editingLabel.value.trim()) {
    node.label = editingLabel.value.trim()
    editingNodeId.value = null
    editingLabel.value = ''
    
    // 如果当前是固定状态，保存布局
    if (allNodesFixed.value) {
      saveLayout()
    }
  } else {
    // 如果名称为空，恢复原名称
    editingLabel.value = node.label
    editingNodeId.value = null
  }
}

// 取消编辑图块名称
const cancelEditLabel = (node) => {
  editingNodeId.value = null
  editingLabel.value = ''
}

// 处理标签区域的键盘事件
const handleLabelKeydown = (event, node) => {
  if (event.key === 'Enter') {
    event.preventDefault()
    saveEditLabel(node)
  } else if (event.key === 'Escape') {
    event.preventDefault()
    cancelEditLabel(node)
  }
}

// 右键双击删除节点
let rightClickTime = 0
let rightClickNode = null
const RIGHT_CLICK_DOUBLE_TIME = 500 // 右键双击时间间隔（毫秒）

const handleRightClick = (event, node) => {
  event.preventDefault()
  const now = Date.now()
  
  // 检查是否是右键双击（两次右键点击间隔小于500ms且是同一个节点）
  if (rightClickNode?.id === node.id && now - rightClickTime < RIGHT_CLICK_DOUBLE_TIME) {
    // 右键双击，执行删除
    deleteNode(node)
    rightClickTime = 0
    rightClickNode = null
  } else {
    // 记录第一次右键点击
    rightClickTime = now
    rightClickNode = node
  }
}

// 删除节点
const deleteNode = (node) => {
  // 检查同类型图块数量
  const sameTypeNodes = topologyNodes.value.filter(n => n.baseLabel === node.baseLabel)
  
  // 如果该类型仅剩一个，不允许删除
  if (sameTypeNodes.length <= 1) {
    deleteMessage.value = `无法删除：${node.baseLabel}类型仅剩一个图块，必须保留至少一个`
    setTimeout(() => {
      deleteMessage.value = ''
    }, 2000)
    return
  }
  
  // 删除节点时，同时删除相关的连接线
  connectionLines.value = connectionLines.value.filter(line => 
    !(line.startX === node.x && line.startY === node.y) &&
    !(line.endX === node.x && line.endY === node.y)
  )
  
  // 删除节点
  const index = topologyNodes.value.findIndex(n => n.id === node.id)
  if (index !== -1) {
    topologyNodes.value.splice(index, 1)
    deleteMessage.value = `已删除：${node.label}`
    setTimeout(() => {
      deleteMessage.value = ''
    }, 1500)
    
    // 如果当前是固定状态，保存布局
    if (allNodesFixed.value) {
      saveLayout()
    }
  }
}

// 创建新连接线
const createConnectionLine = () => {
  const newLine = {
    id: `line_${connectionLineIdCounter++}`,
    startX: 20,
    startY: 30,
    endX: 80,
    endY: 50,
  }
  connectionLines.value.push(newLine)
  
  // 如果当前是固定状态，保存布局
  if (allNodesFixed.value) {
    saveLayout()
  }
}

// 开始拖拽连接线端点
const startLineDrag = (event, line, endType) => {
  // 如果位置已固定，不允许移动线体
  if (allNodesFixed.value) {
    return
  }
  event.preventDefault()
  event.stopPropagation()
  
  draggingLineEnd.value = endType
  draggingLine.value = line
  
  const rect = lineVisualRef.value.getBoundingClientRect()
  const currentX = endType === 'start' ? line.startX : line.endX
  const currentY = endType === 'start' ? line.startY : line.endY
  
  const nodeX = (rect.width * currentX) / 100
  const nodeY = (rect.height * currentY) / 100
  
  lineDragOffset.value = {
    x: event.clientX - rect.left - nodeX,
    y: event.clientY - rect.top - nodeY,
  }
  
  document.addEventListener('mousemove', onLineDrag)
  document.addEventListener('mouseup', stopLineDrag)
}

// 拖拽连接线端点中
const onLineDrag = (event) => {
  if (!draggingLine.value || !lineVisualRef.value || !draggingLineEnd.value) return
  
  const rect = lineVisualRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left - lineDragOffset.value.x
  const y = event.clientY - rect.top - lineDragOffset.value.y
  
  // 限制在可视区域内 (0% - 100%)
  const newX = Math.max(0, Math.min(100, (x / rect.width) * 100))
  const newY = Math.max(0, Math.min(100, (y / rect.height) * 100))
  
  if (draggingLineEnd.value === 'start') {
    draggingLine.value.startX = newX
    draggingLine.value.startY = newY
  } else {
    draggingLine.value.endX = newX
    draggingLine.value.endY = newY
  }
}

// 停止拖拽连接线端点
const stopLineDrag = () => {
  draggingLineEnd.value = null
  draggingLine.value = null
  document.removeEventListener('mousemove', onLineDrag)
  document.removeEventListener('mouseup', stopLineDrag)
  
  // 如果当前是固定状态，保存布局
  if (allNodesFixed.value) {
    saveLayout()
  }
}

// 删除连接线
const deleteConnectionLine = (line) => {
  const index = connectionLines.value.findIndex(l => l.id === line.id)
  if (index !== -1) {
    connectionLines.value.splice(index, 1)
    deleteMessage.value = '已删除连接线'
    setTimeout(() => {
      deleteMessage.value = ''
    }, 1500)
    
    // 如果当前是固定状态，保存布局
    if (allNodesFixed.value) {
      saveLayout()
    }
  }
}

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const overviewResponse = await fetchHomeOverview()
    metrics.value = overviewResponse.data
  } catch (error) {
    errorMessage.value = '数据加载出现波动，请稍后重试。'
    console.error(error)
  } finally {
    loading.value = false
  }
}



onMounted(async () => {
  // 先尝试从数据库加载保存的布局
  const layoutLoaded = await loadLayout()
  
  // 如果没有保存的布局，使用默认布局
  if (!layoutLoaded) {
    // 使用默认的initialNodes创建节点
    topologyNodes.value = initialNodes.map(createNode)
  }
  
  // 加载数据
  loadData()
})
</script>

<template>
  <div class="home-view">
    <MetricsGrid :metrics="metrics" />

    <section class="blockchain-section">
      <div class="section-header">
        <div>
          <h2>生产数据上链可视化</h2>
          <p>生产线设备通过可信网关实时上传数据，形成区块链可信账本</p>
        </div>
        <div class="header-actions">
          <button 
            class="toggle-visibility-button"
            @click="toggleActionButtonsVisibility"
            :title="showActionButtons ? '隐藏操作按钮' : '显示操作按钮'"
          >
            {{ showActionButtons ? '👁️' : '👁️‍🗨️' }}
          </button>
          <div class="header-actions-row">
            <div v-show="showActionButtons" class="action-buttons-group">
              <button 
                class="fix-all-button" 
                :class="{ 'fixed': allNodesFixed }"
                @click="toggleFixAllNodes"
              >
                {{ allNodesFixed ? '🔒 位置固定' : '🔓 位置固定' }}
              </button>
              <button 
                class="add-line-button"
                @click="createConnectionLine"
                title="添加连接线"
              >
                ➕ 添加连接线
              </button>
            </div>
            <div class="section-tag">实时上链</div>
          </div>
        </div>
      </div>
      <div class="line-visual" ref="lineVisualRef">
        <div class="line-background"></div>
        <!-- 连接线层：在背景图之上，图块之下 -->
        <svg class="connection-lines-layer" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <marker id="arrow-green" markerWidth="3" markerHeight="3" refX="2.5" refY="1.5" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L3,1.5 L0,3 z" fill="#90EE90" />
            </marker>
          </defs>
          <g
            v-for="line in connectionLines"
            :key="line.id"
            class="connection-line-group"
            @contextmenu.prevent="() => deleteConnectionLine(line)"
            @mouseenter="hoveredLineId = line.id"
            @mouseleave="hoveredLineId = null"
          >
            <line
              :x1="line.startX"
              :y1="line.startY"
              :x2="line.endX"
              :y2="line.endY"
              stroke="#90EE90"
              stroke-width="0.3"
              stroke-dasharray="2 1"
              marker-end="url(#arrow-green)"
              opacity="0.7"
              class="connection-line"
            />
            <!-- 起点拖拽点 -->
            <circle
              v-if="!allNodesFixed"
              :cx="line.startX"
              :cy="line.startY"
              r="2.5"
              fill="#90EE90"
              stroke="#ffffff"
              stroke-width="0.8"
              class="line-endpoint line-start"
              :class="{ 'endpoint-visible': hoveredLineId === line.id }"
              @mousedown="(e) => startLineDrag(e, line, 'start')"
              cursor="move"
            />
            <!-- 终点拖拽点 -->
            <circle
              v-if="!allNodesFixed"
              :cx="line.endX"
              :cy="line.endY"
              r="2.5"
              fill="#90EE90"
              stroke="#ffffff"
              stroke-width="0.8"
              class="line-endpoint line-end"
              :class="{ 'endpoint-visible': hoveredLineId === line.id }"
              @mousedown="(e) => startLineDrag(e, line, 'end')"
              cursor="move"
            />
          </g>
        </svg>
        <div
          v-for="node in topologyNodes"
          :key="node.id"
          class="device-node"
          :class="{ 'node-fixed': node.fixed, 'node-dragging': draggingNode?.id === node.id }"
          :style="getNodeStyle(node)"
          @mousedown="(e) => startDrag(e, node)"
          @contextmenu="(e) => handleRightClick(e, node)"
        >
          <div 
            class="device-node-icon"
            @dblclick.stop="(e) => handleDoubleClick(node, e)"
          >
            <img
              v-if="isImagePath(deviceIcons[node.type])"
              :src="deviceIcons[node.type]"
              alt=""
            />
            <span v-else>{{ deviceIcons[node.type] || '●' }}</span>
          </div>
          <div class="device-node-label-wrapper">
            <input
              v-if="editingNodeId === node.id"
              v-model="editingLabel"
              class="device-node-label-input"
              @blur="saveEditLabel(node)"
              @keydown="(e) => handleLabelKeydown(e, node)"
              @click.stop
              @mousedown.stop
              autofocus
            />
            <span
              v-else
              class="device-node-label"
              :class="{ 'label-disabled': allNodesFixed }"
              @dblclick.stop="(e) => startEditLabel(node, e)"
              :title="allNodesFixed ? '位置已固定，无法编辑' : '双击编辑名称'"
            >
              {{ node.label }}
            </span>
          </div>
        </div>
        <div class="blockchain-stack">
          <div class="chain-layer" v-for="i in 4" :key="i" :style="{ transform: `translateZ(${i * 6}px)` }"></div>
          <div class="chain-label">
            <span>区块链账本</span>
            <p>跨企业可信共享</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="loading" class="loading">数据加载中...</section>
    <section v-else-if="errorMessage" class="error">{{ errorMessage }}</section>
    
    <!-- 删除提示消息 -->
    <div v-if="deleteMessage" class="delete-message" :class="{ 'delete-error': deleteMessage.includes('无法删除') }">
      {{ deleteMessage }}
    </div>
  </div>
</template>

<style scoped>
.home-view {
  padding: 32px 64px 64px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(5, 26, 43, 0.95), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.header-actions-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-visibility-button {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  background: rgba(10, 20, 35, 0.8);
  color: #80d6ff;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 32px;
}

.toggle-visibility-button:hover {
  background: rgba(20, 40, 60, 0.9);
  border-color: rgba(88, 178, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.2);
}

.action-buttons-group {
  display: flex;
  align-items: center;
  gap: 12px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header h2 {
  margin: 0;
  font-size: 26px;
  color: #ffffff;
}

.section-header p {
  margin: 6px 0 0;
  color: rgba(214, 232, 255, 0.7);
  letter-spacing: 0.4px;
}

.section-tag {
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  color: #80d6ff;
  font-size: 13px;
  letter-spacing: 1px;
}

.blockchain-section {
  padding: 32px;
  background: linear-gradient(135deg, rgba(10, 32, 51, 0.9), rgba(5, 18, 30, 0.92));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.28);
}

.line-visual {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  min-height: 360px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.line-background {
  position: absolute;
  inset: 0;
  background-image: url('/product_line.png');
  background-size: cover;
  background-position: center;
  filter: saturate(1.1) brightness(0.9);
  opacity: 0.85;
  z-index: 1;
}

.connection-lines-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 5;
  pointer-events: none;
  overflow: visible;
}

.connection-line-group {
  pointer-events: all;
}

.connection-line {
  pointer-events: stroke;
  cursor: pointer;
  stroke-width: 0.8;
}

/* 增加连接线的可点击区域 */
.connection-line-group {
  transition: opacity 0.2s;
}

.connection-line-group:hover .connection-line {
  opacity: 0.9;
  stroke-width: 1;
}

.line-endpoint {
  cursor: move;
  pointer-events: all;
  transition: opacity 0.2s, r 0.2s;
  opacity: 0;
}

.line-endpoint.endpoint-visible {
  opacity: 1;
}

.line-endpoint:hover {
  r: 3.5;
  opacity: 1;
  filter: brightness(1.3);
}

.line-endpoint:active {
  r: 4;
  opacity: 1;
}

.device-node {
  position: absolute;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #e2e8f0;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
  user-select: none;
  z-index: 10;
  transition: opacity 0.2s, transform 0.1s;
  pointer-events: all;
}

.device-node.node-dragging {
  z-index: 100;
  opacity: 0.9;
  transform: translate(-50%, -50%) scale(1.1);
}

.device-node.node-fixed {
  opacity: 0.8;
}

.device-node-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: 1px solid var(--node-color, rgba(255, 255, 255, 0.3));
  background: rgba(10, 20, 35, 0.8);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  pointer-events: all;
  cursor: pointer;
}

.device-node-icon img,
.device-node-icon span {
  pointer-events: none;
}

.device-node-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
}


.device-node-icon span {
  font-size: 20px;
}

.device-node-label-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
}

.device-node-label {
  font-size: 13px;
  letter-spacing: 0.5px;
  white-space: nowrap;
  cursor: text;
  user-select: none;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.device-node-label:hover:not(.label-disabled) {
  background-color: rgba(255, 255, 255, 0.1);
}

.device-node-label.label-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.device-node-label.label-disabled:hover {
  background-color: transparent;
}

.device-node-label-input {
  font-size: 13px;
  letter-spacing: 0.5px;
  background: rgba(10, 20, 35, 0.95);
  border: 1px solid rgba(88, 178, 255, 0.5);
  color: #e2e8f0;
  padding: 2px 6px;
  border-radius: 4px;
  outline: none;
  min-width: 60px;
  max-width: 150px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.device-node-label-input:focus {
  border-color: #58b2ff;
  box-shadow: 0 0 0 2px rgba(88, 178, 255, 0.2);
}

.fix-all-button {
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  background: rgba(10, 20, 35, 0.8);
  color: #80d6ff;
  font-size: 13px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.fix-all-button:hover {
  background: rgba(20, 40, 60, 0.9);
  border-color: rgba(88, 178, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.2);
}

.fix-all-button.fixed {
  background: rgba(76, 175, 80, 0.9);
  border-color: rgba(76, 175, 80, 0.5);
  color: #ffffff;
}

.add-line-button {
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  background: rgba(10, 20, 35, 0.8);
  color: #80d6ff;
  font-size: 13px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.add-line-button:hover {
  background: rgba(20, 40, 60, 0.9);
  border-color: rgba(88, 178, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.2);
}

.blockchain-stack {
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  perspective: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.chain-layer {
  width: 110px;
  height: 44px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.9), rgba(255, 175, 113, 0.9));
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(255, 135, 135, 0.35);
  opacity: 0.9;
}

.chain-label {
  text-align: center;
  color: #ffe5e0;
  letter-spacing: 1px;
}

.chain-label span {
  font-size: 16px;
  font-weight: 600;
}

.chain-label p {
  margin: 4px 0 0;
  font-size: 13px;
  color: rgba(255, 229, 224, 0.8);
}

.loading,
.error {
  padding: 18px 24px;
  border-radius: 12px;
  background: rgba(7, 27, 44, 0.8);
  border: 1px solid rgba(88, 178, 255, 0.12);
  font-size: 15px;
  letter-spacing: 0.8px;
}

.error {
  color: #ff9a9e;
}

.delete-message {
  position: fixed;
  top: 100px;
  right: 32px;
  padding: 12px 20px;
  border-radius: 8px;
  background: rgba(76, 175, 80, 0.9);
  color: #ffffff;
  font-size: 14px;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.delete-message.delete-error {
  background: rgba(255, 107, 107, 0.9);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>

