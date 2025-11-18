<template>
  <div class="tsn-configurator">
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
      <div class="navbar-left">
        <div class="logo">NEST-FIELD</div>
      </div>
      <div class="navbar-right">
        <div class="navbar-menu">
          <button class="nav-btn" :class="{ active: activeTab === 'topology' }" @click="activeTab = 'topology'">
            拓扑
          </button>
          <button class="nav-btn" :class="{ active: activeTab === 'scheduling' }" @click="activeTab = 'scheduling'">
            调度
          </button>
          <button class="nav-btn" :class="{ active: activeTab === 'simulation' }" @click="activeTab = 'simulation'">
            仿真
          </button>
        </div>
        <!-- 项目菜单 -->
        <div class="project-menu" @click.stop>
          <button class="project-menu-btn" @click="showProjectMenu = !showProjectMenu">
            <span>项目</span>
            <span class="menu-arrow" :class="{ 'open': showProjectMenu }">▼</span>
          </button>
          <div v-if="showProjectMenu" class="project-dropdown">
            <button class="dropdown-item" @click="exportTopology">
              <span>📤 导出保存拓扑</span>
            </button>
            <button class="dropdown-item" @click="importTopology">
              <span>📥 导入拓扑</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 左侧设备面板 -->
      <div class="device-panel">
        <div class="panel-header">
          <span>设备</span>
          <button class="close-btn" @click="showDevicePanel = false">×</button>
        </div>
        <div class="device-list">
          <div class="device-item" draggable="true" @dragstart="onDeviceDragStart($event, 'end-station')">
            <div class="device-icon device-end-station">
              <img src="/device.png" alt="设备" class="device-image" />
            </div>
            <span>设备</span>
          </div>
          <div class="device-item" draggable="true" @dragstart="onDeviceDragStart($event, 'switch')">
            <div class="device-icon device-switch">
              <img src="/switch.png" alt="交换机" class="device-image" />
            </div>
            <span>交换机</span>
          </div>
        </div>
      </div>

      <!-- 中间画布区域 -->
      <div class="canvas-container">
        <!-- Topology 视图 -->
        <div v-if="activeTab === 'topology'" class="topology-view">
          <div 
            class="canvas" 
            ref="canvasRef"
            @drop="onCanvasDrop"
            @dragover.prevent
            @click="onCanvasClick"
          >
            <!-- 网格背景 -->
            <div class="grid-background" v-if="showGrid"></div>
            
            <!-- 连线 -->
            <svg class="connections-layer" v-if="showFlows" @dblclick="handleLineDoubleClick">
              <line
                v-for="(link, index) in links"
                :key="`link-${link.id || index}`"
                :x1="link.source.x"
                :y1="link.source.y"
                :x2="link.target.x"
                :y2="link.target.y"
                :stroke="link.color || '#4ade80'"
                :stroke-width="3.5"
                :marker-end="`url(#arrowhead-${index})`"
                :marker-start="undefined"
                class="connection-line"
                :data-link-index="index"
                @dblclick.stop="editConnection(link)"
                @mousedown.stop
                @mouseenter="hoveredLink = link"
                @mouseleave="hoveredLink = null"
                style="cursor: pointer; pointer-events: all;"
              />
              <defs>
                <marker 
                  v-for="(link, index) in links" 
                  :key="`marker-${index}`"
                  :id="`arrowhead-${index}`"
                  markerWidth="20" 
                  markerHeight="14" 
                  refX="18" 
                  refY="7" 
                  orient="auto" 
                  markerUnits="userSpaceOnUse"
                  viewBox="0 0 20 14"
                >
                  <polygon 
                    points="0 0, 20 7, 0 14" 
                    :fill="link.color || '#4ade80'" 
                    :stroke="link.color || '#4ade80'"
                    stroke-width="0.6"
                  />
                </marker>
              </defs>
            </svg>

            <!-- 设备节点 -->
            <div
              v-for="node in nodes"
              :key="node.id"
              :data-node-id="node.id"
              class="node"
              :class="{ 
                'node-selected': selectedNode?.id === node.id,
                'node-connecting': connectingFromNode?.id === node.id,
                'node-connect-target': anchorDragging && anchorDragging.sourceNode?.id !== node.id
              }"
              :style="{ left: node.x + 'px', top: node.y + 'px' }"
              @click.stop="handleNodeClick(node)"
              @dblclick.stop="handleNodeDoubleClick(node)"
              @mousedown="startDrag($event, node)"
              @contextmenu.prevent="showNodeMenu($event, node)"
            >
              <div :class="['node-icon', node.type === 'switch' ? 'node-switch' : 'node-device']">
                <img 
                  :src="node.type === 'switch' ? '/switch.png' : '/device.png'" 
                  :alt="node.name" 
                  class="node-image" 
                />
              </div>
              <div class="node-label">{{ node.name }}</div>
              
              <!-- 四个锚点（上下左右中心） -->
              <div class="node-anchors">
                <div 
                  class="node-anchor anchor-top" 
                  @mousedown.stop="startAnchorDrag($event, node, 'top')"
                  title="从上方连接"
                ></div>
                <div 
                  class="node-anchor anchor-right" 
                  @mousedown.stop="startAnchorDrag($event, node, 'right')"
                  title="从右方连接"
                ></div>
                <div 
                  class="node-anchor anchor-bottom" 
                  @mousedown.stop="startAnchorDrag($event, node, 'bottom')"
                  title="从下方连接"
                ></div>
                <div 
                  class="node-anchor anchor-left" 
                  @mousedown.stop="startAnchorDrag($event, node, 'left')"
                  title="从左方连接"
                ></div>
              </div>
            </div>

            <!-- 临时拖拽连线 -->
            <svg v-if="anchorDragging" class="temp-connection-layer">
              <line
                :x1="anchorDragging.startX"
                :y1="anchorDragging.startY"
                :x2="anchorDragging.currentX"
                :y2="anchorDragging.currentY"
                stroke="#4ade80"
                stroke-width="3"
                stroke-dasharray="5,5"
                marker-end="url(#temp-arrowhead)"
              />
              <defs>
                <marker id="temp-arrowhead" markerWidth="16" markerHeight="16" refX="15" refY="4" orient="auto" markerUnits="userSpaceOnUse">
                  <polygon points="0 0, 16 4, 0 8" fill="#4ade80" stroke="#4ade80" stroke-width="0.5" />
                </marker>
              </defs>
            </svg>

            <!-- 右键菜单 -->
            <div 
              v-if="showContextMenu" 
              class="context-menu"
              :style="{ left: contextMenuPos.x + 'px', top: contextMenuPos.y + 'px' }"
              @click.stop
            >
              <button class="context-menu-item" @click="startConnecting">
                <span>🔗 连接</span>
              </button>
              <button class="context-menu-item" @click="editNodeProperties">
                <span>⚙️ 编辑属性</span>
              </button>
              <button class="context-menu-item" @click="deleteNode">
                <span>🗑️ 删除</span>
              </button>
            </div>

            <!-- 连接模式提示 -->
            <div v-if="connectingMode" class="connecting-hint">
              <div class="hint-content">
                <span>连接模式：请点击目标节点</span>
                <button class="btn btn-small" @click="cancelConnecting">取消</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Scheduling 视图 -->
        <div v-if="activeTab === 'scheduling'" class="scheduling-view">
          <div class="flows-table-container">
            <div class="table-header">
              <h3>流量配置</h3>
              <div class="table-actions">
                <button class="btn btn-add" @click="showAddFlowDialog = true">添加</button>
                <button class="btn btn-edit" @click="editSelectedFlow" :disabled="!selectedFlow">编辑</button>
                <button class="btn btn-delete" @click="deleteFlow" :disabled="!selectedFlow">删除</button>
                <button class="btn btn-close" @click="activeTab = 'topology'">关闭</button>
              </div>
            </div>
            <div class="table-wrapper">
              <table class="flows-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>名称</th>
                  <th>源节点</th>
                  <th>目标节点</th>
                  <th>长度 (字节)</th>
                  <th>周期 (纳秒)</th>
                  <th>允许延迟 (纳秒)</th>
                  <th>颜色</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="flow in flows" 
                  :key="flow.id"
                  :class="{ 'row-selected': selectedFlow?.id === flow.id }"
                  @click="selectedFlow = flow"
                >
                  <td>{{ flow.id }}</td>
                  <td>{{ flow.name }}</td>
                  <td>{{ flow.src }}</td>
                  <td>{{ flow.dst }}</td>
                  <td>{{ flow.length }}</td>
                  <td>{{ flow.period }}</td>
                  <td>{{ flow.delay }}</td>
                  <td>
                    <div class="color-indicator" :style="{ backgroundColor: flow.color }"></div>
                  </td>
                </tr>
                <tr v-if="flows.length === 0">
                  <td colspan="8" class="empty-row">暂无记录。</td>
                </tr>
              </tbody>
            </table>
            </div>
          </div>
          
          <!-- 拓扑图显示 -->
          <div class="topology-preview">
            <div class="canvas-preview-container">
              <div class="canvas-preview" ref="canvasPreviewRef" :style="previewCanvasStyle">
                <div class="grid-background" v-if="showGrid"></div>
                <svg class="connections-layer" v-if="showFlows">
                  <line
                    v-for="(link, index) in links"
                    :key="`preview-link-${link.id || index}`"
                    :x1="link.source.x"
                    :y1="link.source.y"
                    :x2="link.target.x"
                    :y2="link.target.y"
                    :stroke="link.color || '#4ade80'"
                    :stroke-width="2"
                  />
                </svg>
                <div
                  v-for="node in nodes"
                  :key="node.id"
                  class="node-preview"
                  :style="{ left: node.x + 'px', top: node.y + 'px' }"
                >
                  <div :class="['node-icon', node.type === 'switch' ? 'node-switch' : 'node-device']">
                    <img 
                      :src="node.type === 'switch' ? '/switch.png' : '/device.png'" 
                      :alt="node.name" 
                      class="node-image" 
                    />
                  </div>
                  <div class="node-label">{{ node.name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Simulation 视图 -->
        <div v-if="activeTab === 'simulation'" class="simulation-view">
          <div class="simulation-controls">
            <button class="btn btn-primary" @click="runSimulation" :disabled="flows.length === 0 || computing">
              {{ computing ? '计算中...' : '运行仿真' }}
            </button>
            <button class="btn btn-secondary" @click="showResults = false" v-if="simulationResult">
              关闭结果
            </button>
          </div>

          <!-- 结果显示 -->
          <div v-if="simulationResult && showResults" class="simulation-result">
            <div class="result-popup">
              <div class="result-title">完成</div>
              <div class="result-circle">
                <div class="result-value">{{ simulationResult.delay }}us!!</div>
              </div>
              <button class="btn btn-primary" @click="handleSeeResults">查看结果</button>
            </div>
          </div>

          <!-- 仿真结果表格 -->
          <div v-if="simulationResults.length" class="simulation-results-table">
            <div class="results-header">
              <div>
                <h3>TSN 仿真结果</h3>
                <p class="results-caption">基于当前拓扑与 Flow 的端到端时延评估</p>
              </div>
              <span class="results-summary">
                {{ simulationResults.filter(item => item.status === 'PASS').length }}/{{ simulationResults.length }} 个流量通过
              </span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>流量</th>
                  <th>发送节点</th>
                  <th>接收节点</th>
                  <th>允许延迟 (纳秒)</th>
                  <th>平均延迟 (微秒)</th>
                  <th>最大延迟 (微秒)</th>
                  <th>状态</th>
                  <th>路径</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="flow in simulationResults" :key="flow.id">
                  <td>{{ flow.name }}</td>
                  <td>{{ flow.src }}</td>
                  <td>{{ flow.dst }}</td>
                  <td>{{ formatNumber(flow.allowable) }}</td>
                  <td>{{ formatNumber(flow.avgDelay, 2) }}</td>
                  <td>{{ formatNumber(flow.maxDelay, 2) }}</td>
                  <td>
                    <span :class="['status-pill', flow.status === 'PASS' ? 'status-pass' : 'status-fail']">
                      {{ flow.status }}
                    </span>
                  </td>
                  <td class="path-cell">{{ flow.path || '未找到路径' }}</td>
                  <td>
                    <button class="btn btn-ghost" @click="viewFlowChart(flow)">
                      查看曲线
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Gate Control List -->
          <div v-if="showGateControlList" class="gate-control-list">
            <div class="gcl-header">
              <h3>门控列表</h3>
              <button class="close-btn" @click="showGateControlList = false">×</button>
            </div>
            <table class="gcl-table">
              <thead>
                <tr>
                  <th>交换机名称</th>
                  <th>接口名称</th>
                  <th>超周期 (纳秒)</th>
                  <th>门控状态</th>
                  <th>周期 (纳秒)</th>
                  <th>分配流量</th>
                  <th>周期用途</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(gcl, index) in gateControlList" :key="index">
                  <td>{{ gcl.switchName }}</td>
                  <td>{{ gcl.interfaceName }}</td>
                  <td>{{ gcl.hyperPeriod }}</td>
                  <td>{{ gcl.gateStatus }}</td>
                  <td>{{ gcl.period }}</td>
                  <td>{{ gcl.allocatedFlow }}</td>
                  <td>{{ gcl.periodFor }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 底部控制栏（浮动在画布上） -->
      <div class="bottom-controls-floating">
        <div class="controls-group">
          <label>
            <input type="checkbox" v-model="showGrid" />
            <span>显示网格</span>
          </label>
          <label>
            <input type="checkbox" v-model="showFlows" />
            <span>显示流量</span>
          </label>
          <div class="zoom-controls">
            <span>缩放</span>
            <button class="zoom-btn" @click="zoomOut">-</button>
            <span class="zoom-value">{{ zoom }}%</span>
            <button class="zoom-btn" @click="zoomIn">+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加设备对话框 -->
    <div v-if="showAddDeviceDialog" class="modal-overlay">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ editingNodeId ? '编辑设备' : '添加设备' }}</h3>
          <button class="close-btn" @click="closeDeviceDialog">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>节点名称 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="newDevice.name" 
              :class="{ 'error': errors.name }"
              placeholder="请输入节点名称"
            />
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>
          <div class="form-group">
            <label>类型</label>
            <input type="text" :value="newDevice.type" readonly />
          </div>
          <div class="form-group">
            <label>型号</label>
            <input type="text" v-model="newDevice.model" placeholder="请输入型号" />
          </div>
          <div class="form-group">
            <label>IP 地址 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="newDevice.ipAddress" 
              :class="{ 'error': errors.ipAddress }"
              placeholder="0.0.0.0"
            />
            <span v-if="errors.ipAddress" class="error-message">{{ errors.ipAddress }}</span>
          </div>
          <div class="form-group">
            <label>端口名称 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="newDevice.portName" 
              :class="{ 'error': errors.portName }"
              placeholder="请输入端口名称"
            />
            <span v-if="errors.portName" class="error-message">{{ errors.portName }}</span>
          </div>
          <div class="form-group">
            <label>MAC 地址 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="newDevice.macAddress" 
              :class="{ 'error': errors.macAddress }"
              placeholder="00:00:00:00:00:00"
            />
            <span v-if="errors.macAddress" class="error-message">{{ errors.macAddress }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeDeviceDialog">取消</button>
          <button class="btn btn-primary" @click="addDevice">确定</button>
        </div>
      </div>
    </div>

    <!-- 编辑连接对话框 -->
    <div v-if="showEditConnectionDialog" class="modal-overlay">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>编辑连接</h3>
          <p class="modal-subtitle">{{ editingConnection?.source?.name }} 到 {{ editingConnection?.target?.name }}</p>
          <button class="close-btn" @click="closeConnectionDialog">×</button>
        </div>
        <div class="modal-body">
          <div class="connection-form">
            <div class="form-section">
              <h4>本地设备</h4>
              <div class="form-group">
                <label>本地设备:</label>
                <input type="text" :value="editingConnection?.source?.name" readonly />
              </div>
              <div class="form-group">
                <label>端口:</label>
                <select v-model="editingConnection.port">
                  <option value="">无</option>
                  <option v-for="port in availablePorts" :key="port" :value="port">{{ port }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>链路权重:</label>
                <input type="number" v-model.number="editingConnection.weight" />
              </div>
            </div>
            <div class="form-section">
              <h4>远程设备</h4>
              <div class="form-group">
                <label>连接到:</label>
                <input type="text" :value="editingConnection?.target?.name" readonly />
              </div>
              <div class="form-group">
                <label>远程端口:</label>
                <select v-model="editingConnection.remotePort">
                  <option value="">无</option>
                </select>
              </div>
              <div class="form-group">
                <label>链路权重:</label>
                <input type="number" v-model.number="editingConnection.remoteWeight" />
              </div>
            </div>
            <div class="form-section">
              <div class="form-group">
                <label>长度:</label>
                <input type="number" v-model.number="editingConnection.length" />
              </div>
              <div class="form-group">
                <label>速度:</label>
                <input type="number" v-model.number="editingConnection.speed" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeConnectionDialog">取消</button>
          <button class="btn btn-primary" @click="saveConnection">确定</button>
        </div>
      </div>
    </div>

    <!-- 添加 Flow 对话框 -->
    <div v-if="showAddFlowDialog" class="modal-overlay">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>流量名称</h3>
          <button class="close-btn" @click="closeFlowDialog">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>名称</label>
            <input type="text" v-model="newFlow.name" placeholder="请输入流量名称" />
          </div>
          <div class="form-group">
            <label>源节点 (SRC) <span class="required">*</span></label>
            <select v-model="newFlow.src" @focus="handleSelectFocus">
              <option value="">请选择源节点</option>
              <option v-for="node in nodes" :key="node.id" :value="node.name">
                {{ node.name }} ({{ node.type === 'switch' ? '交换机' : '设备' }})
              </option>
            </select>
            <span v-if="!newFlow.src && showFlowErrors.src" class="error-message">请选择源节点</span>
          </div>
          <div class="form-group">
            <label>目标节点 (DST) <span class="required">*</span></label>
            <select v-model="newFlow.dst" @focus="handleSelectFocus">
              <option value="">请选择目标节点</option>
              <option v-for="node in nodes" :key="node.id" :value="node.name">
                {{ node.name }} ({{ node.type === 'switch' ? '交换机' : '设备' }})
              </option>
            </select>
            <span v-if="!newFlow.dst && showFlowErrors.dst" class="error-message">请选择目标节点</span>
          </div>
          <div class="form-group">
            <label>长度 (字节)</label>
            <input type="number" v-model.number="newFlow.length" placeholder="1500" />
          </div>
          <div class="form-group">
            <label>周期 (纳秒)</label>
            <input type="number" v-model.number="newFlow.period" placeholder="100000" />
          </div>
          <div class="form-group">
            <label>允许延迟 (纳秒)</label>
            <input type="number" v-model.number="newFlow.delay" placeholder="100000" />
          </div>
          <div class="form-group">
            <label>颜色</label>
            <div class="color-picker-wrapper">
              <input type="color" v-model="newFlow.color" id="flow-color-picker" />
              <div class="color-display">
                <div class="color-preview" :style="{ backgroundColor: newFlow.color }"></div>
                <span class="color-value">{{ newFlow.color }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeFlowDialog">关闭</button>
          <button class="btn btn-primary" @click="saveFlow">保存</button>
        </div>
      </div>
    </div>

    <!-- Flow 曲线对话框 -->
    <div v-if="showFlowChartDialog && selectedResultFlow" class="modal-overlay">
      <div class="modal-dialog chart-dialog">
        <div class="modal-header">
          <h3>{{ selectedResultFlow.name }} 的仿真结果</h3>
          <button class="close-btn" @click="closeFlowChart">×</button>
        </div>
        <div class="modal-body chart-body">
          <svg
            :width="chartConfig.width"
            :height="chartConfig.height"
            class="chart-canvas"
          >
            <rect
              :x="chartConfig.padding / 2"
              :y="chartConfig.padding / 2"
              :width="chartConfig.width - chartConfig.padding"
              :height="chartConfig.height - chartConfig.padding"
              class="chart-bg"
            />
            <line
              class="allowable-line"
              x1="chartConfig.padding / 2"
              :x2="chartConfig.width - chartConfig.padding / 2"
              :y1="flowChartAllowableY"
              :y2="flowChartAllowableY"
            />
            <polyline
              v-if="flowChartPolyline"
              class="latency-polyline"
              fill="none"
              :points="flowChartPolyline"
            />
          </svg>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-dot legend-delay"></span>
              端到端延迟 (微秒)
            </div>
            <div class="legend-item">
              <span class="legend-dot legend-limit"></span>
              延迟约束 ({{ formatNumber(selectedResultFlow.allowableUs, 2) }} 微秒)
            </div>
            <div class="legend-range">
              <span>最小值: {{ formatNumber(flowChartLatencyRange.min, 2) }} 微秒</span>
              <span>最大值: {{ formatNumber(flowChartLatencyRange.max, 2) }} 微秒</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

// 状态管理
const activeTab = ref('topology')
const showDevicePanel = ref(true)
const showGrid = ref(true)
const showFlows = ref(true)
const zoom = ref(100)
const nodes = ref([])
const links = ref([])
const flows = ref([])
const selectedNode = ref(null)
const selectedFlow = ref(null)
const showAddDeviceDialog = ref(false)
const showEditConnectionDialog = ref(false)
const showAddFlowDialog = ref(false)
const showResults = ref(false)
const showGateControlList = ref(false)
const computing = ref(false)
const showProjectMenu = ref(false)

// 画布引用
const canvasRef = ref(null)
const canvasPreviewRef = ref(null)

// 拖拽相关
const draggingNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const draggedDeviceType = ref(null)

// 连接相关
const connectingMode = ref(false)
const connectingFromNode = ref(null)
const showContextMenu = ref(false)
const contextMenuPos = ref({ x: 0, y: 0 })
const editingNodeId = ref(null) // 编辑节点时的ID
const hoveredLink = ref(null) // 鼠标悬停的连线

// 锚点拖拽相关
const anchorDragging = ref(null) // { sourceNode, side, startX, startY, currentX, currentY }

// 表单数据
const newDevice = reactive({
  name: '',
  type: 'End-station',
  model: '',
  ipAddress: '',
  portName: '',
  macAddress: '',
  portNumber: 1
})

const editingConnection = reactive({
  source: null,
  target: null,
  port: '',
  remotePort: '',
  weight: 10,
  remoteWeight: 10,
  length: 100,
  speed: 1000
})

const newFlow = reactive({
  name: '',
  src: '',
  dst: '',
  length: 1500,
  period: 100000,
  delay: 100000,
  color: '#000000'
})

const errors = reactive({})
const showFlowErrors = reactive({
  src: false,
  dst: false
})

const simulationResult = ref(null)
const simulationResults = ref([])
const selectedResultFlow = ref(null)
const showFlowChartDialog = ref(false)
const flowChartPolyline = ref('')
const flowChartAllowableY = ref(0)
const flowChartLatencyRange = ref({ min: 0, max: 0 })

// 预览画布样式（用于自适应节点，避免偏移出画布）
const previewCanvasStyle = computed(() => {
  if (nodes.value.length === 0) {
    return {}
  }
  
  // 计算所有节点的边界
  let minX = Infinity, minY = Infinity
  let maxX = -Infinity, maxY = -Infinity
  
  nodes.value.forEach(node => {
    minX = Math.min(minX, node.x)
    minY = Math.min(minY, node.y)
    maxX = Math.max(maxX, node.x + 100) // 100 是节点宽度
    maxY = Math.max(maxY, node.y + 100) // 100 是节点高度
  })
  
  // 添加边距
  const padding = 50
  const width = Math.max(maxX - minX + padding * 2, 400)
  const height = Math.max(maxY - minY + padding * 2, 300)
  
  return {
    width: width + 'px',
    height: height + 'px',
    transform: `translate(${-minX + padding}px, ${-minY + padding}px)`
  }
})

const availablePorts = ref(['swp1', 'swp2', 'swp3', 'swp4'])

const gateControlList = ref([])
const chartConfig = {
  width: 640,
  height: 260,
  padding: 40
}

// 基于实际拓扑和流量配置生成 Gate Control List
const generateGateControlList = (flowEdgeMap = new Map()) => {
  const gcl = []
  
  console.log('开始生成 GCL...')
  console.log('所有节点:', nodes.value.map(n => ({ id: n.id, name: n.name, type: n.type })))
  
  // 获取所有交换机节点（支持多种类型标识）
  const switches = nodes.value.filter(n => {
    const nodeType = n.type || n.typeRaw || ''
    return nodeType === 'switch' || n.type === 'Switch' || nodeType.toLowerCase().includes('switch')
  })
  
  console.log('找到的交换机:', switches.map(s => ({ name: s.name, type: s.type, typeRaw: s.typeRaw })))
  
  if (switches.length === 0) {
    console.warn('未找到交换机节点，无法生成 GCL')
    return []
  }
  
  // 遍历每个交换机
  switches.forEach((switchNode, switchIndex) => {
    console.log(`处理交换机 ${switchNode.name} (索引 ${switchIndex})`)
    
    // 找到连接到该交换机的所有连接
    const switchLinks = links.value.filter(link => {
      const sourceNode = nodes.value.find(n => n.id === link.sourceId)
      const targetNode = nodes.value.find(n => n.id === link.targetId)
      const isConnected = (sourceNode?.id === switchNode.id || targetNode?.id === switchNode.id)
      return isConnected
    })
    
    console.log(`交换机 ${switchNode.name} 的连接数:`, switchLinks.length)
    
    // 如果没有连接，为交换机生成一个默认接口的GCL
    if (switchLinks.length === 0) {
      console.log(`交换机 ${switchNode.name} 没有连接，生成默认接口`)
      const defaultInterface = 'swp1'
      const hyperPeriod = 100000
      
      // 即使没有连接，也生成基础的GCL条目
      gcl.push({
        switchName: switchNode.name,
        interfaceName: defaultInterface,
        hyperPeriod: hyperPeriod.toString(),
        gateStatus: '01111111',
        period: '8500',
        allocatedFlow: 'BE period',
        periodFor: 'Transmit Best effort flows'
      })
      
      gcl.push({
        switchName: switchNode.name,
        interfaceName: defaultInterface,
        hyperPeriod: hyperPeriod.toString(),
        gateStatus: '00000000',
        period: '12240',
        allocatedFlow: 'GB period',
        periodFor: 'Guard band'
      })
      
      // 查找所有流量（因为不知道路径，假设都经过默认接口）
      flows.value.forEach((flow, flowIndex) => {
        gcl.push({
          switchName: switchNode.name,
          interfaceName: defaultInterface,
          hyperPeriod: (flow.period || 100000).toString(),
          gateStatus: `${(1 << (7 - flowIndex % 8)).toString(2).padStart(8, '0')}`,
          period: Math.floor((flow.period || 100000) * 0.2).toString(),
          allocatedFlow: flow.name || `flow${flowIndex + 1}`,
          periodFor: 'Transmit TSN flows'
        })
      })
      
      return
    }
    
    // 为每个连接生成 GCL 条目
    switchLinks.forEach((link, linkIndex) => {
      const sourceNode = nodes.value.find(n => n.id === link.sourceId)
      const targetNode = nodes.value.find(n => n.id === link.targetId)
      
      console.log(`处理连接 ${linkIndex}: ${sourceNode?.name} -> ${targetNode?.name}`)
      
      // 确定接口名称（使用连接中的端口或生成）
      const interfaceName = link.port || `swp${linkIndex + 1}`
      
      // 找到通过该连接的流量（匹配路径包含的 link id）
      const relatedFlows = flows.value.filter(flow => {
        const flowEdges = flowEdgeMap.get(flow.id)
        if (!flowEdges || flowEdges.length === 0) return false
        return flowEdges.includes(link.id)
      })
      
      console.log(`连接 ${linkIndex} 相关的流量数:`, relatedFlows.length)
      relatedFlows.forEach(flow => {
        console.log(`  - 流量: ${flow.name} (${flow.src} -> ${flow.dst})`)
      })
      
      // 计算超周期（所有流量周期的最大值，或使用默认值）
      let hyperPeriod = 100000 // 默认值
      if (relatedFlows.length > 0) {
        const periods = relatedFlows.map(f => f.period || 100000).filter(p => p > 0)
        if (periods.length > 0) {
          hyperPeriod = Math.max(...periods)
        }
      } else {
        // 如果没有流量通过这个连接，使用所有流量的最大周期
        const allPeriods = flows.value.map(f => f.period || 100000).filter(p => p > 0)
        if (allPeriods.length > 0) {
          hyperPeriod = Math.max(...allPeriods)
        }
      }
      
      console.log(`超周期: ${hyperPeriod}ns`)
      
      // 生成 BE 周期条目
      const bePeriod = Math.floor(hyperPeriod * 0.08) // 8% 给 BE
      gcl.push({
        switchName: switchNode.name,
        interfaceName: interfaceName,
        hyperPeriod: hyperPeriod.toString(),
        gateStatus: '01111111', // BE 开放所有队列
        period: bePeriod.toString(),
        allocatedFlow: 'BE period',
        periodFor: 'Transmit Best effort flows'
      })
      
      // 生成保护带（Guard Band）条目
      const guardBand = Math.floor(hyperPeriod * 0.01) // 1% 保护带
      gcl.push({
        switchName: switchNode.name,
        interfaceName: interfaceName,
        hyperPeriod: hyperPeriod.toString(),
        gateStatus: '00000000', // 保护带关闭所有队列
        period: guardBand.toString(),
        allocatedFlow: 'GB period',
        periodFor: 'Guard band'
      })
      
      // 为每个 TSN 流量生成条目
      relatedFlows.forEach((flow, flowIndex) => {
        const tsnPeriod = Math.floor(hyperPeriod * 0.2) // 20% 给每个 TSN 流（简化）
        gcl.push({
          switchName: switchNode.name,
          interfaceName: interfaceName,
          hyperPeriod: hyperPeriod.toString(),
          gateStatus: `${(1 << (7 - (flowIndex % 8))).toString(2).padStart(8, '0')}`, // 为每个流分配不同的队列
          period: tsnPeriod.toString(),
          allocatedFlow: flow.name || `flow${flowIndex + 1}`,
          periodFor: 'Transmit TSN flows'
        })
      })
      
      // 再次添加 BE 周期（剩余时间）
      const tsnTotalPeriod = relatedFlows.length * Math.floor(hyperPeriod * 0.2)
      const remainingPeriod = Math.max(0, hyperPeriod - bePeriod - guardBand - tsnTotalPeriod)
      if (remainingPeriod > 0) {
        gcl.push({
          switchName: switchNode.name,
          interfaceName: interfaceName,
          hyperPeriod: hyperPeriod.toString(),
          gateStatus: '01111111',
          period: remainingPeriod.toString(),
          allocatedFlow: 'BE period',
          periodFor: 'Transmit Best effort flows'
        })
      }
      
      console.log(`为连接 ${linkIndex} 生成了 ${gcl.length} 个GCL条目`)
    })
  })
  
  console.log('最终生成的 GCL 条目总数:', gcl.length)
  return gcl
}

const buildTopologyGraph = () => {
  const graph = new Map()
  links.value.forEach(link => {
    if (!graph.has(link.sourceId)) {
      graph.set(link.sourceId, [])
    }
    if (!graph.has(link.targetId)) {
      graph.set(link.targetId, [])
    }
    graph.get(link.sourceId).push({ nodeId: link.targetId, link })
    graph.get(link.targetId).push({ nodeId: link.sourceId, link })
  })
  return graph
}

const findLinkBetweenNodes = (aId, bId) => {
  return links.value.find(
    link =>
      (link.sourceId === aId && link.targetId === bId) ||
      (link.sourceId === bId && link.targetId === aId)
  )
}

const findFlowPath = (sourceId, targetId, graph) => {
  if (!graph.has(sourceId) || !graph.has(targetId)) {
    return { nodes: [], links: [] }
  }
  const queue = [[sourceId]]
  const visited = new Set([sourceId])
  while (queue.length > 0) {
    const path = queue.shift()
    const node = path[path.length - 1]
    if (node === targetId) {
      const linkSequence = []
      for (let i = 0; i < path.length - 1; i += 1) {
        const link = findLinkBetweenNodes(path[i], path[i + 1])
        if (link) {
          linkSequence.push(link)
        }
      }
      return { nodes: path, links: linkSequence }
    }
    const neighbors = graph.get(node) || []
    neighbors.forEach(({ nodeId }) => {
      if (!visited.has(nodeId)) {
        visited.add(nodeId)
        queue.push([...path, nodeId])
      }
    })
  }
  return { nodes: [], links: [] }
}

const createLatencySeries = (avgDelay, maxDelay, samples = 20) => {
  const series = []
  for (let i = 0; i < samples; i += 1) {
    const jitter = (Math.random() - 0.5) * 6
    const trend = (i / samples) * (maxDelay - avgDelay)
    series.push({
      index: i + 1,
      value: Number((avgDelay + trend + jitter).toFixed(2))
    })
  }
  return series
}

const calculateFlowMetrics = (flow, pathInfo) => {
  const allowableUs = flow.delay ? flow.delay / 1000 : 100
  if (!pathInfo.nodes.length) {
    return {
      allowableUs,
      avgDelay: allowableUs * 1.2,
      maxDelay: allowableUs * 1.5,
      pathNames: '路径不可用',
      latencySeries: createLatencySeries(allowableUs * 1.2, allowableUs * 1.5)
    }
  }

  const hopCount = Math.max(1, pathInfo.nodes.length - 1)
  const totalLength = pathInfo.links.reduce((acc, link) => acc + (link.length || 100), 0)
  const averageSpeed = pathInfo.links.reduce((acc, link) => acc + (link.speed || 1000), 0) / hopCount || 1000
  const serializationDelay = (flow.length * 8) / averageSpeed // μs
  const propagationDelay = (totalLength * 5) / 1000 // 5ns/m -> μs
  const queuingDelay = Math.min((flow.period || 100000) / 1000 * 0.05 * hopCount, allowableUs * 0.5)
  const base = 20 + hopCount * 5
  const avgDelay = Number((base + serializationDelay + propagationDelay + queuingDelay).toFixed(2))
  const maxDelay = Number((avgDelay + hopCount * 2 + Math.random() * 5).toFixed(2))

  return {
    allowableUs,
    avgDelay,
    maxDelay,
    pathNames: pathInfo.nodes
      .map(id => nodes.value.find(n => n.id === id)?.name || 'unknown')
      .join(' → '),
    latencySeries: createLatencySeries(avgDelay, maxDelay)
  }
}

const formatNumber = (value, digits = 0) => {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return '-'
  }
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  })
}

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

const updateChartState = (flowResult) => {
  if (!flowResult) return
  const series = flowResult.latencySeries || []
  if (!series.length) {
    flowChartPolyline.value = ''
    flowChartAllowableY.value = chartConfig.height - chartConfig.padding
    flowChartLatencyRange.value = { min: 0, max: flowResult.allowableUs || 0 }
    return
  }

  const maxLatency = Math.max(...series.map(point => point.value), flowResult.allowableUs || 0)
  const minLatency = Math.min(...series.map(point => point.value))
  flowChartLatencyRange.value = {
    min: Number(minLatency.toFixed(2)),
    max: Number(maxLatency.toFixed(2))
  }
  const range = maxLatency - minLatency || 1
  const width = chartConfig.width
  const height = chartConfig.height
  const padding = chartConfig.padding

  flowChartPolyline.value = series
    .map((point, index) => {
      const x =
        padding +
        (index / Math.max(series.length - 1, 1)) * (width - padding * 2)
      const y =
        height -
        padding -
        ((point.value - minLatency) / range) * (height - padding * 2)
      return `${x},${y}`
    })
    .join(' ')

  const allowablePosition =
    height -
    padding -
    ((flowResult.allowableUs - minLatency) / range) * (height - padding * 2)
  flowChartAllowableY.value = clamp(
    allowablePosition,
    padding,
    height - padding
  )
}

const viewFlowChart = (flowResult) => {
  if (!flowResult) return
  selectedResultFlow.value = flowResult
  updateChartState(flowResult)
  showFlowChartDialog.value = true
}

const closeFlowChart = () => {
  showFlowChartDialog.value = false
}

// 设备拖拽开始
const onDeviceDragStart = (event, type) => {
  draggedDeviceType.value = type
  event.dataTransfer.effectAllowed = 'copy'
}

// 生成设备默认值
const generateDeviceDefaults = (type) => {
  const isSwitch = type === 'switch'
  
  // 统计已存在的同类型设备数量
  const existingCount = nodes.value.filter(n => n.type === type).length
  const deviceIndex = existingCount + 1
  
  // 生成 MAC 地址（格式：00:00:00:00:00:XX）
  const macSuffix = String(deviceIndex).padStart(2, '0')
  
  if (isSwitch) {
    return {
      name: `switch${deviceIndex}`,
      type: 'Switch',
      typeRaw: 'switch',
      model: 'TSN-Switch-1000',
      ipAddress: `192.168.1.${100 + deviceIndex}`,
      portName: `swp${deviceIndex}`,
      macAddress: `00:00:00:00:00:${macSuffix}`,
      portNumber: deviceIndex
    }
  } else {
    // End-station 使用不同的 MAC 前缀以便区分
    const macPrefix = String(deviceIndex).padStart(2, '0')
    return {
      name: `end-station${deviceIndex}`,
      type: 'End-station',
      typeRaw: 'end-station',
      model: 'TSN-EndStation-100',
      ipAddress: `192.168.1.${10 + deviceIndex}`,
      portName: `port${deviceIndex}`,
      macAddress: `00:00:00:00:${macPrefix}:${macSuffix}`,
      portNumber: deviceIndex
    }
  }
}

// 画布拖放
const onCanvasDrop = (event) => {
  event.preventDefault()
  if (!draggedDeviceType.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  // 生成设备默认值
  const defaults = generateDeviceDefaults(draggedDeviceType.value)
  
  // 准备添加设备（填充默认值）
  newDevice.name = defaults.name
  newDevice.type = defaults.type
  newDevice.typeRaw = defaults.typeRaw
  newDevice.model = defaults.model
  newDevice.ipAddress = defaults.ipAddress
  newDevice.portName = defaults.portName
  newDevice.macAddress = defaults.macAddress
  newDevice.portNumber = defaults.portNumber
  newDevice.x = x
  newDevice.y = y

  showAddDeviceDialog.value = true
  draggedDeviceType.value = null
}

// 节点选择
const selectNode = (node) => {
  selectedNode.value = node
  selectedFlow.value = null
}

// 节点点击处理
const handleNodeClick = (node) => {
  // 如果处于连接模式
  if (connectingMode.value && connectingFromNode.value) {
    if (connectingFromNode.value.id !== node.id) {
      // 创建连接
      createConnection(connectingFromNode.value, node)
    }
    cancelConnecting()
    return
  }
  
  // 如果正在锚点拖拽，完成连接
  if (anchorDragging.value && anchorDragging.value.sourceNode && anchorDragging.value.sourceNode.id !== node.id) {
    finishAnchorConnection(node)
    return
  }
  
  // 普通点击选择节点
  selectNode(node)
  showContextMenu.value = false
}

// 节点双击处理 - 编辑节点属性
const handleNodeDoubleClick = (node) => {
  selectNode(node)
  editNodeProperties()
}

// 画布点击
const onCanvasClick = (event) => {
  if (event.target === canvasRef.value || event.target.classList.contains('grid-background')) {
    selectedNode.value = null
    showContextMenu.value = false
    if (connectingMode.value) {
      cancelConnecting()
    }
    // 如果正在锚点拖拽，取消拖拽
    if (anchorDragging.value) {
      anchorDragging.value = null
      document.removeEventListener('mousemove', handleAnchorDrag)
      document.removeEventListener('mouseup', handleAnchorDragEnd)
    }
  }
}

// 开始拖拽节点（避免与锚点拖拽冲突）
const startDrag = (event, node) => {
  // 如果点击的是锚点，不处理节点拖拽
  if (event.target.classList.contains('node-anchor')) {
    return
  }
  
  if (event.button !== 0) return // 只处理左键
  if (event.detail === 2) return // 忽略双击事件
  
  draggingNode.value = node
  const rect = canvasRef.value.getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left - node.x,
    y: event.clientY - rect.top - node.y
  }
  event.preventDefault()
}

// 获取锚点的屏幕坐标（节点大小为100x100）
const getAnchorPosition = (node, side) => {
  const nodeWidth = 100 // 节点宽度
  const nodeHeight = 100 // 节点高度
  const nodeCenterX = node.x + nodeWidth / 2 // 节点中心X
  const nodeCenterY = node.y + nodeHeight / 2 // 节点中心Y
  
  switch (side) {
    case 'top':
      return { x: nodeCenterX, y: node.y } // 上边中心
    case 'right':
      return { x: node.x + nodeWidth, y: nodeCenterY } // 右边中心
    case 'bottom':
      return { x: nodeCenterX, y: node.y + nodeHeight } // 下边中心
    case 'left':
      return { x: node.x, y: nodeCenterY } // 左边中心
    default:
      return { x: nodeCenterX, y: nodeCenterY }
  }
}

// 开始锚点拖拽
const startAnchorDrag = (event, node, side) => {
  event.stopPropagation()
  event.preventDefault()
  
  const rect = canvasRef.value.getBoundingClientRect()
  const anchorPos = getAnchorPosition(node, side)
  
  anchorDragging.value = {
    sourceNode: node,
    side: side,
    startX: anchorPos.x,
    startY: anchorPos.y,
    currentX: event.clientX - rect.left,
    currentY: event.clientY - rect.top
  }
  
  // 添加全局事件监听
  document.addEventListener('mousemove', handleAnchorDrag)
  document.addEventListener('mouseup', handleAnchorDragEnd)
}

// 处理锚点拖拽
const handleAnchorDrag = (event) => {
  if (!anchorDragging.value || !canvasRef.value) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  anchorDragging.value.currentX = event.clientX - rect.left
  anchorDragging.value.currentY = event.clientY - rect.top
}

// 完成锚点连接
const finishAnchorConnection = (targetNode, targetSide = null) => {
  if (!anchorDragging.value) return
  
  const sourceNode = anchorDragging.value.sourceNode
  
  // 检查连接是否已存在
  const existingLink = links.value.find(
    link => link.sourceId === sourceNode.id && link.targetId === targetNode.id
  )
  
  if (existingLink) {
    alert('连接已存在')
    anchorDragging.value = null
    document.removeEventListener('mousemove', handleAnchorDrag)
    document.removeEventListener('mouseup', handleAnchorDragEnd)
    return
  }
  
  // 获取源节点锚点位置
  const sourcePos = getAnchorPosition(sourceNode, anchorDragging.value.side)
  
  // 如果用户指定了目标锚点，使用它；否则自动选择最近的边
  let finalTargetSide = targetSide
  if (!finalTargetSide) {
    // 计算目标节点的最佳锚点（选择与源节点最近的一边）
    const distances = {
      top: Math.abs(sourcePos.y - (targetNode.y)),
      right: Math.abs(sourcePos.x - (targetNode.x + 100)),
      bottom: Math.abs(sourcePos.y - (targetNode.y + 100)),
      left: Math.abs(sourcePos.x - (targetNode.x))
    }
    
    finalTargetSide = Object.keys(distances).reduce((a, b) => 
      distances[a] < distances[b] ? a : b
    )
  }
  
  // 获取目标节点锚点位置
  const targetPos = getAnchorPosition(targetNode, finalTargetSide)
  
  // 创建连接
  const link = {
    id: `link-${sourceNode.id}-${targetNode.id}-${Date.now()}`,
    sourceId: sourceNode.id,
    targetId: targetNode.id,
    source: sourcePos,
    target: targetPos,
    color: '#4ade80',
    weight: 10,
    length: 100,
    speed: 1000,
    sourceSide: anchorDragging.value.side,
    targetSide: finalTargetSide
  }

  links.value.push(link)
  
  // 打开编辑连接对话框
  editingConnection.source = sourceNode
  editingConnection.target = targetNode
  editingConnection.weight = link.weight
  editingConnection.remoteWeight = link.weight
  editingConnection.length = link.length
  editingConnection.speed = link.speed
  showEditConnectionDialog.value = true
  
  // 清理
  anchorDragging.value = null
  document.removeEventListener('mousemove', handleAnchorDrag)
  document.removeEventListener('mouseup', handleAnchorDragEnd)
}

// 检查鼠标位置是否在某个节点的锚点上
const checkMouseOverAnchor = (mouseX, mouseY, node) => {
  const anchorSize = 16 // 锚点大小（像素）
  const anchorRadius = anchorSize / 2
  
  // 检查四个锚点
  const sides = ['top', 'right', 'bottom', 'left']
  for (const side of sides) {
    const anchorPos = getAnchorPosition(node, side)
    const distance = Math.sqrt(
      Math.pow(mouseX - anchorPos.x, 2) + Math.pow(mouseY - anchorPos.y, 2)
    )
    if (distance <= anchorRadius + 5) { // 增加5px的容差
      return side
    }
  }
  return null
}

// 锚点拖拽结束
const handleAnchorDragEnd = (event) => {
  if (!anchorDragging.value || !canvasRef.value) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  // 检查是否拖拽到了某个锚点上（首先尝试通过event.target）
  let targetAnchorSide = null
  const targetAnchor = event.target.closest('.node-anchor')
  if (targetAnchor) {
    // 检测是哪个锚点
    if (targetAnchor.classList.contains('anchor-top')) {
      targetAnchorSide = 'top'
    } else if (targetAnchor.classList.contains('anchor-right')) {
      targetAnchorSide = 'right'
    } else if (targetAnchor.classList.contains('anchor-bottom')) {
      targetAnchorSide = 'bottom'
    } else if (targetAnchor.classList.contains('anchor-left')) {
      targetAnchorSide = 'left'
    }
    
    // 找到锚点所在的节点
    const targetNodeElement = targetAnchor.closest('.node')
    if (targetNodeElement && targetAnchorSide) {
      const nodeId = targetNodeElement.getAttribute('data-node-id')
      if (nodeId) {
        const targetNode = nodes.value.find(n => n.id === nodeId)
        if (targetNode && anchorDragging.value.sourceNode.id !== targetNode.id) {
          finishAnchorConnection(targetNode, targetAnchorSide)
          return
        }
      }
    }
  }
  
  // 如果event.target没有识别到锚点，使用鼠标位置检查所有节点
  for (const node of nodes.value) {
    if (node.id === anchorDragging.value.sourceNode.id) continue
    
    // 检查鼠标是否在节点范围内
    const nodeLeft = node.x
    const nodeRight = node.x + 100
    const nodeTop = node.y
    const nodeBottom = node.y + 100
    
    if (mouseX >= nodeLeft - 20 && mouseX <= nodeRight + 20 &&
        mouseY >= nodeTop - 20 && mouseY <= nodeBottom + 20) {
      // 检查是否在锚点上
      const anchorSide = checkMouseOverAnchor(mouseX, mouseY, node)
      if (anchorSide) {
        finishAnchorConnection(node, anchorSide)
        return
      } else {
        // 不在锚点上，但在节点范围内，使用自动选择
        finishAnchorConnection(node, null)
        return
      }
    }
  }
  
  // 如果没有连接到节点，取消拖拽
  anchorDragging.value = null
  document.removeEventListener('mousemove', handleAnchorDrag)
  document.removeEventListener('mouseup', handleAnchorDragEnd)
}

// 鼠标移动处理
const handleMouseMove = (event) => {
  if (!draggingNode.value || !canvasRef.value) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  draggingNode.value.x = event.clientX - rect.left - dragOffset.value.x
  draggingNode.value.y = event.clientY - rect.top - dragOffset.value.y
  
  // 更新连线
  updateLinks()
}

// 鼠标释放
const handleMouseUp = () => {
  draggingNode.value = null
}

// 计算连线在节点边缘的连接点（避免箭头被节点遮挡）
const calculateConnectionPoint = (node, targetNode, preferredSide = null) => {
  const nodeCenterX = node.x + 50
  const nodeCenterY = node.y + 50
  
  // 如果节点有指定的连接边，直接使用
  if (preferredSide) {
    return getAnchorPosition(node, preferredSide)
  }
  
  if (!targetNode) {
    return { x: nodeCenterX, y: nodeCenterY }
  }
  
  const targetCenterX = targetNode.x + 50
  const targetCenterY = targetNode.y + 50
  
  // 计算方向向量
  const dx = targetCenterX - nodeCenterX
  const dy = targetCenterY - nodeCenterY
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) {
    return { x: nodeCenterX, y: nodeCenterY }
  }
  
  // 节点半径（假设节点大小为100x100）
  const nodeRadius = 50
  // 箭头长度
  const arrowLength = 15
  
  // 计算从节点边缘延伸的方向单位向量
  const unitX = dx / distance
  const unitY = dy / distance
  
  // 计算连接点（节点边缘 + 箭头偏移）
  const edgeOffset = nodeRadius + arrowLength
  return {
    x: nodeCenterX + unitX * edgeOffset,
    y: nodeCenterY + unitY * edgeOffset
  }
}

// 更新连线位置
const updateLinks = () => {
  links.value = links.value.map(link => {
    const sourceNode = nodes.value.find(n => n.id === link.sourceId)
    const targetNode = nodes.value.find(n => n.id === link.targetId)
    if (sourceNode && targetNode) {
      // 使用保存的锚点边，或计算新的连接点
      link.source = calculateConnectionPoint(sourceNode, targetNode, link.sourceSide)
      link.target = calculateConnectionPoint(targetNode, sourceNode, link.targetSide)
    }
    return link
  })
}

// 处理连线双击事件
const handleLineDoubleClick = (event) => {
  const line = event.target
  if (line.tagName === 'line') {
    const linkIndex = parseInt(line.getAttribute('data-link-index'))
    if (linkIndex >= 0 && linkIndex < links.value.length) {
      editConnection(links.value[linkIndex])
    }
  }
}

// 显示节点菜单
const showNodeMenu = (event, node) => {
  selectedNode.value = node
  contextMenuPos.value = {
    x: event.clientX,
    y: event.clientY
  }
  showContextMenu.value = true
  
  // 点击其他地方关闭菜单
  setTimeout(() => {
    const closeMenu = (e) => {
      if (!e.target.closest('.context-menu') && e.target !== event.target) {
        showContextMenu.value = false
        document.removeEventListener('click', closeMenu)
      }
    }
    document.addEventListener('click', closeMenu)
  }, 0)
}

// 开始连接
const startConnecting = () => {
  if (!selectedNode.value) return
  connectingMode.value = true
  connectingFromNode.value = selectedNode.value
  showContextMenu.value = false
}

// 取消连接
const cancelConnecting = () => {
  connectingMode.value = false
  connectingFromNode.value = null
}

// 创建连接
const createConnection = (sourceNode, targetNode) => {
  // 检查连接是否已存在
  const existingLink = links.value.find(
    link => link.sourceId === sourceNode.id && link.targetId === targetNode.id
  )
  
  if (existingLink) {
    alert('连接已存在')
    return
  }

  // 创建新连接（使用计算连接点函数）
  const link = {
    id: `link-${sourceNode.id}-${targetNode.id}-${Date.now()}`,
    sourceId: sourceNode.id,
    targetId: targetNode.id,
    source: calculateConnectionPoint(sourceNode, targetNode),
    target: calculateConnectionPoint(targetNode, sourceNode),
    color: '#4ade80',
    weight: 10,
    length: 100,
    speed: 1000,
    sourceSide: null,
    targetSide: null
  }

  links.value.push(link)
  
  // 打开编辑连接对话框
  editingConnection.source = sourceNode
  editingConnection.target = targetNode
  editingConnection.weight = link.weight
  editingConnection.remoteWeight = link.weight
  editingConnection.length = link.length
  editingConnection.speed = link.speed
  showEditConnectionDialog.value = true
}

// 编辑节点属性
const editNodeProperties = () => {
  if (!selectedNode.value) return
  // 填充设备信息到表单
  editingNodeId.value = selectedNode.value.id
  newDevice.name = selectedNode.value.name
  newDevice.type = selectedNode.value.type === 'switch' ? 'Switch' : 'End-station'
  newDevice.typeRaw = selectedNode.value.type
  newDevice.model = selectedNode.value.model || ''
  newDevice.ipAddress = selectedNode.value.ipAddress || ''
  newDevice.portName = selectedNode.value.portName || ''
  newDevice.macAddress = selectedNode.value.macAddress || ''
  newDevice.x = selectedNode.value.x
  newDevice.y = selectedNode.value.y
  
  showContextMenu.value = false
  showAddDeviceDialog.value = true
}

// 删除节点
const deleteNode = () => {
  if (!selectedNode.value) return
  
  if (confirm(`确定要删除节点 "${selectedNode.value.name}" 吗？`)) {
    // 删除节点
    const index = nodes.value.findIndex(n => n.id === selectedNode.value.id)
    if (index > -1) {
      nodes.value.splice(index, 1)
    }
    
    // 删除相关连接
    links.value = links.value.filter(
      link => link.sourceId !== selectedNode.value.id && link.targetId !== selectedNode.value.id
    )
    
    selectedNode.value = null
    showContextMenu.value = false
  }
}

// 添加设备
const validateDevice = () => {
  errors.name = ''
  errors.ipAddress = ''
  errors.portName = ''
  errors.macAddress = ''

  if (!newDevice.name.trim()) {
    errors.name = '节点名称是必填项。'
    return false
  }

  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
  if (!ipRegex.test(newDevice.ipAddress)) {
    errors.ipAddress = '请更正 IP 地址格式。例如：0.0.0.0 - 255.255.255.255。'
    return false
  }

  if (!newDevice.portName.trim()) {
    errors.portName = '端口名称是必填项。'
    return false
  }

  const macRegex = /^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$/
  if (!macRegex.test(newDevice.macAddress)) {
    errors.macAddress = '请更正 MAC 地址格式。例如：00:00:00:00:00:00。'
    return false
  }

  return true
}

const addDevice = () => {
  if (!validateDevice()) return

  // 如果是编辑模式
  if (editingNodeId.value) {
    const nodeIndex = nodes.value.findIndex(n => n.id === editingNodeId.value)
    if (nodeIndex > -1) {
      // 更新现有节点
      nodes.value[nodeIndex] = {
        ...nodes.value[nodeIndex],
        name: newDevice.name,
        model: newDevice.model,
        ipAddress: newDevice.ipAddress,
        portName: newDevice.portName,
        macAddress: newDevice.macAddress
      }
    }
    editingNodeId.value = null
  } else {
    // 添加新节点
    const node = {
      id: Date.now().toString(),
      name: newDevice.name,
      x: newDevice.x || 100,
      y: newDevice.y || 100,
      ...newDevice,
      type: newDevice.typeRaw  // 确保使用 typeRaw 的值（'switch' 或 'end-station'），覆盖 newDevice.type
    }
    nodes.value.push(node)
  }

  closeDeviceDialog()
}

const closeDeviceDialog = () => {
  showAddDeviceDialog.value = false
  editingNodeId.value = null
  // 清空表单（保留类型相关字段用于重置）
  newDevice.name = ''
  newDevice.model = ''
  newDevice.ipAddress = ''
  newDevice.portName = ''
  newDevice.macAddress = ''
  newDevice.x = undefined
  newDevice.y = undefined
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
}

// 连接相关
const editConnection = (link) => {
  const sourceNode = nodes.value.find(n => n.id === link.sourceId)
  const targetNode = nodes.value.find(n => n.id === link.targetId)
  
  if (!sourceNode || !targetNode) return
  
  editingConnection.source = sourceNode
  editingConnection.target = targetNode
  editingConnection.port = link.port || ''
  editingConnection.remotePort = link.remotePort || ''
  editingConnection.weight = link.weight || 10
  editingConnection.remoteWeight = link.weight || 10
  editingConnection.length = link.length || 100
  editingConnection.speed = link.speed || 1000
  
  showEditConnectionDialog.value = true
}

const closeConnectionDialog = () => {
  showEditConnectionDialog.value = false
  editingConnection.source = null
  editingConnection.target = null
}

const saveConnection = () => {
  if (!editingConnection.source || !editingConnection.target) return
  
  // 更新连接信息
  const link = links.value.find(
    l => l.sourceId === editingConnection.source.id && l.targetId === editingConnection.target.id
  )
  
  if (link) {
    link.weight = editingConnection.weight
    link.length = editingConnection.length
    link.speed = editingConnection.speed
    link.port = editingConnection.port
    link.remotePort = editingConnection.remotePort
    // 确保保存后使用正确的锚点位置更新连线
    updateLinks()
  }
  
  closeConnectionDialog()
}

// Flow 相关
const closeFlowDialog = () => {
  showAddFlowDialog.value = false
  // 重置错误状态
  showFlowErrors.src = false
  showFlowErrors.dst = false
  Object.keys(newFlow).forEach(key => {
    if (key === 'length') newFlow[key] = 1500
    else if (key === 'period' || key === 'delay') newFlow[key] = 100000
    else if (key === 'color') newFlow[key] = '#000000'
    else newFlow[key] = ''
  })
}

const handleSelectFocus = () => {
  // 清除错误状态
  showFlowErrors.src = false
  showFlowErrors.dst = false
}

const saveFlow = () => {
  // 验证必填字段
  showFlowErrors.src = !newFlow.src
  showFlowErrors.dst = !newFlow.dst
  
  if (!newFlow.name || !newFlow.src || !newFlow.dst) {
    if (!newFlow.src || !newFlow.dst) {
      alert('请选择源节点和目标节点')
    } else {
      alert('请填写所有必填字段')
    }
    return
  }

  // 检查源节点和目标节点是否存在
  const sourceNode = nodes.value.find(n => n.name === newFlow.src)
  const targetNode = nodes.value.find(n => n.name === newFlow.dst)
  
  if (!sourceNode || !targetNode) {
    alert('未找到源节点或目标节点。请选择有效的节点。')
    return
  }

  // 检查是否是编辑模式
  const existingFlowIndex = flows.value.findIndex(f => f.id === newFlow.id)
  
  if (existingFlowIndex > -1) {
    // 更新现有flow
    flows.value[existingFlowIndex] = {
      ...flows.value[existingFlowIndex],
      ...newFlow
    }
  } else {
    // 创建新flow
    const flow = {
      id: `${newFlow.src}-${newFlow.dst}-${Date.now()}`,
      ...newFlow
    }
    flows.value.push(flow)
  }

  // 更新或创建连线（如果不存在）
  const existingLink = links.value.find(
    l => l.sourceId === sourceNode.id && l.targetId === targetNode.id
  )
  
  if (existingLink) {
    // 更新现有连线的颜色
    existingLink.color = newFlow.color
  } else {
    // 创建新连线（使用计算连接点函数）
    links.value.push({
      id: `link-${sourceNode.id}-${targetNode.id}-${Date.now()}`,
      sourceId: sourceNode.id,
      targetId: targetNode.id,
      source: calculateConnectionPoint(sourceNode, targetNode),
      target: calculateConnectionPoint(targetNode, sourceNode),
      color: newFlow.color,
      weight: 10,
      length: 100,
      speed: 1000
    })
  }

  // 更新所有相关连线的位置
  updateLinks()
  closeFlowDialog()
}

const editSelectedFlow = () => {
  if (!selectedFlow.value) {
    alert('请先选择一个流量')
    return
  }
  // 复制flow数据到表单
  newFlow.id = selectedFlow.value.id
  newFlow.name = selectedFlow.value.name
  newFlow.src = selectedFlow.value.src
  newFlow.dst = selectedFlow.value.dst
  newFlow.length = selectedFlow.value.length
  newFlow.period = selectedFlow.value.period
  newFlow.delay = selectedFlow.value.delay
  newFlow.color = selectedFlow.value.color
  showAddFlowDialog.value = true
}

const deleteFlow = () => {
  if (!selectedFlow.value) return
  const index = flows.value.findIndex(f => f.id === selectedFlow.value.id)
  if (index > -1) {
    flows.value.splice(index, 1)
    // 删除对应的连线
    const linkIndex = links.value.findIndex(
      l => l.sourceId === nodes.value.find(n => n.name === selectedFlow.value.src)?.id &&
           l.targetId === nodes.value.find(n => n.name === selectedFlow.value.dst)?.id
    )
    if (linkIndex > -1) {
      links.value.splice(linkIndex, 1)
    }
    selectedFlow.value = null
  }
}

// 处理查看结果
const handleSeeResults = () => {
  showResults.value = false  // 关闭 Done 对话框
  showGateControlList.value = true  // 显示 Gate Control List
}

// 仿真相关
const runSimulation = async () => {
  if (flows.value.length === 0) {
    alert('请先添加至少一个流量')
    return
  }

  if (nodes.value.length < 2) {
    alert('请添加至少 2 个节点以创建网络拓扑')
    return
  }

  computing.value = true
  showResults.value = false

  // 开始调度计算过程
  console.log('开始计算 TSN 调度...')
  console.log('节点数量:', nodes.value.length)
  console.log('流量数量:', flows.value.length)
  console.log('连接数量:', links.value.length)

  // 模拟计算延迟（实际应该调用后端API进行真实的TSN调度算法计算）
  await new Promise(resolve => setTimeout(resolve, 1500))

  const graph = buildTopologyGraph()
  const flowEdgeMap = new Map()
  const perFlowResults = flows.value.map(flow => {
    const sourceNode = nodes.value.find(n => n.name === flow.src)
    const targetNode = nodes.value.find(n => n.name === flow.dst)
    const pathInfo =
      sourceNode && targetNode
        ? findFlowPath(sourceNode.id, targetNode.id, graph)
        : { nodes: [], links: [] }

    flowEdgeMap.set(flow.id, pathInfo.links.map(link => link.id))
    const metrics = calculateFlowMetrics(flow, pathInfo)

    return {
      id: flow.id,
      name: flow.name,
      src: flow.src,
      dst: flow.dst,
      allowable: flow.delay || 100000,
      allowableUs: metrics.allowableUs,
      avgDelay: metrics.avgDelay,
      maxDelay: metrics.maxDelay,
      status: metrics.maxDelay <= metrics.allowableUs ? 'PASS' : 'FAIL',
      path: metrics.pathNames,
      latencySeries: metrics.latencySeries
    }
  })

  simulationResults.value = perFlowResults
  selectedResultFlow.value = perFlowResults[0] || null

  // 基于实际配置生成 Gate Control List
  gateControlList.value = generateGateControlList(flowEdgeMap)
  console.log('生成的 Gate Control List:', gateControlList.value)

  const worstCaseDelay = perFlowResults.length
    ? Math.max(...perFlowResults.map(item => item.maxDelay))
    : 0

  simulationResult.value = {
    delay: worstCaseDelay.toFixed(2),
    success: perFlowResults.every(item => item.status === 'PASS'),
    timestamp: new Date().toISOString()
  }

  computing.value = false
  showResults.value = true
  
  console.log('调度计算完成，端到端延迟:', simulationResult.value.delay + 'us')
  console.log('生成的 GCL 条目数:', gateControlList.value.length)
}

// 缩放
const zoomIn = () => {
  zoom.value = Math.min(zoom.value + 10, 200)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value - 10, 50)
}

// 导出拓扑
const exportTopology = () => {
  showProjectMenu.value = false
  
  const topologyData = {
    version: '1.0',
    exportTime: new Date().toISOString(),
    nodes: nodes.value,
    links: links.value,
    flows: flows.value
  }
  
  const dataStr = JSON.stringify(topologyData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `topology_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  alert('拓扑已成功导出！')
}

// 导入拓扑
const importTopology = () => {
  showProjectMenu.value = false
  
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const topologyData = JSON.parse(e.target.result)
        
        // 验证数据格式
        if (!topologyData.nodes || !Array.isArray(topologyData.nodes)) {
          throw new Error('无效的拓扑文件格式：缺少节点数据')
        }
        if (!topologyData.links || !Array.isArray(topologyData.links)) {
          throw new Error('无效的拓扑文件格式：缺少连接数据')
        }
        
        // 确认是否覆盖当前拓扑
        if (nodes.value.length > 0 || links.value.length > 0 || flows.value.length > 0) {
          if (!confirm('导入拓扑将覆盖当前拓扑图，是否继续？')) {
            return
          }
        }
        
        // 导入数据
        nodes.value = topologyData.nodes || []
        links.value = topologyData.links || []
        flows.value = topologyData.flows || []
        
        // 更新连线位置
        updateLinks()
        
        alert('拓扑已成功导入！')
      } catch (error) {
        console.error('导入拓扑失败:', error)
        alert('导入失败：' + error.message)
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

// 点击外部关闭项目菜单
const handleClickOutside = (event) => {
  if (showProjectMenu.value && !event.target.closest('.project-menu')) {
    showProjectMenu.value = false
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.tsn-configurator {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  color: #e6f1ff;
}

.top-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background: #0f1e2e;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.navbar-left .logo {
  font-size: 18px;
  font-weight: 600;
  color: #4ade80;
}

.navbar-menu {
  display: flex;
  gap: 8px;
}

.nav-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: #d6ecff;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-btn.active {
  background: #49c5ff;
  color: #0b2338;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.project-menu {
  position: relative;
}

.project-menu-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: #d6ecff;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: 14px;
}

.project-menu-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.menu-arrow {
  font-size: 10px;
  transition: transform 0.2s;
  display: inline-block;
}

.menu-arrow.open {
  transform: rotate(180deg);
}

.project-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #1e2a3a;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  min-width: 180px;
  overflow: hidden;
}

.dropdown-item {
  width: 100%;
  padding: 12px 16px;
  text-align: left;
  background: none;
  border: none;
  color: #e6f1ff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dropdown-item:hover {
  background: rgba(73, 197, 255, 0.2);
  color: #49c5ff;
}

.dropdown-item:first-child {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.dropdown-item:last-child {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.device-panel {
  width: 200px;
  background: #1e2a3a;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.device-list {
  padding: 16px;
}

.device-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s;
}

.device-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.device-item:active {
  cursor: grabbing;
}

.device-icon {
  width: 60px;
  height: 60px;
  margin-bottom: 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.device-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

.device-end-station {
  /* 背景色已移除，使用图片 */
}

.device-switch {
  /* 背景色已移除，使用图片 */
}

.canvas-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topology-view {
  flex: 1;
  position: relative;
}

.canvas {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: auto;
  background: #f9fafb;
  min-height: 500px;
}

.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.node {
  position: absolute;
  width: 100px;
  height: 100px;
  cursor: move;
  z-index: 10;
  transition: transform 0.2s;
}

.node:hover {
  transform: scale(1.05);
}

.node-selected {
  outline: 2px solid #49c5ff;
  outline-offset: 2px;
}

.node-connecting {
  outline: 2px solid #fbbf24;
  outline-offset: 2px;
  animation: pulse 1s infinite;
}

.node-connect-target {
  cursor: crosshair;
}

.node-connect-target:hover {
  outline: 2px dashed #4ade80;
  outline-offset: 2px;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.7);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(251, 191, 36, 0);
  }
}

.node-icon {
  width: 100%;
  height: 70px;
  border-radius: 4px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.node-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

.node-device {
  /* 背景色已移除，使用图片 */
}

.node-switch {
  /* 背景色已移除，使用图片 */
}

.node-label {
  text-align: center;
  font-size: 12px;
  color: #1a1a1a;
  font-weight: 500;
}

/* 节点锚点样式 */
.node-anchors {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
}

.node-anchor {
  position: absolute;
  width: 16px;
  height: 16px;
  background: #4ade80;
  border: 2px solid #fff;
  border-radius: 50%;
  cursor: crosshair;
  pointer-events: all;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
  z-index: 20;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.node:hover .node-anchor,
.node-selected .node-anchor {
  opacity: 1;
}

.node-anchor:hover {
  background: #22c55e;
  transform: scale(1.2);
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.6);
  border-color: #22c55e;
}

.anchor-top {
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
}

.anchor-top:hover {
  transform: translate(-50%, -50%) scale(1.2);
}

.anchor-right {
  top: 50%;
  right: 0;
  transform: translate(50%, -50%);
}

.anchor-right:hover {
  transform: translate(50%, -50%) scale(1.2);
}

.anchor-bottom {
  bottom: 0;
  left: 50%;
  transform: translate(-50%, 50%);
}

.anchor-bottom:hover {
  transform: translate(-50%, 50%) scale(1.2);
}

.anchor-left {
  top: 50%;
  left: 0;
  transform: translate(-50%, -50%);
}

.anchor-left:hover {
  transform: translate(-50%, -50%) scale(1.2);
}

/* 临时连线层 */
.temp-connection-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 15;
}

.scheduling-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  gap: 16px;
}

.flows-table-container {
  background: #1e2a3a;
  border-radius: 8px;
  padding: 16px 24px;
  flex: 0 0 auto;
  max-height: 35vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.table-header h3 {
  margin: 0;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-add, .btn-edit {
  background: #4ade80;
  color: #1a1a1a;
}

.btn-delete {
  background: #ef4444;
  color: #fff;
}

.btn-close {
  background: #49c5ff;
  color: #0b2338;
}

.btn-primary {
  background: #49c5ff;
  color: #0b2338;
}

.btn-secondary {
  background: #6b7280;
  color: #fff;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table-wrapper {
  overflow-y: auto;
  overflow-x: auto;
  flex: 1;
  max-height: calc(35vh - 80px);
}

.flows-table {
  width: 100%;
  border-collapse: collapse;
  background: #0f1e2e;
  min-width: 800px;
}

.flows-table th,
.flows-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.flows-table th {
  background: #1e2a3a;
  font-weight: 600;
}

.flows-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
}

.row-selected {
  background: rgba(73, 197, 255, 0.2) !important;
}

.empty-row {
  text-align: center;
  color: #6b7280;
  padding: 32px;
}

.color-indicator {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.topology-preview {
  flex: 1;
  background: #1e2a3a;
  border-radius: 8px;
  padding: 24px;
  overflow: auto;
  min-height: 0; /* 允许 flex 子项收缩 */
  display: flex;
  flex-direction: column;
}

.canvas-preview-container {
  width: 100%;
  height: 100%;
  overflow: auto;
  position: relative;
}

.canvas-preview {
  position: relative;
  background: #f9fafb;
  border-radius: 4px;
  min-width: 100%;
  min-height: 100%;
  transition: all 0.3s ease;
}

.node-preview {
  position: absolute;
  width: 80px;
  height: 80px;
  z-index: 10;
}

.simulation-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  align-items: center;
  justify-content: center;
  position: relative;
}

.simulation-results-table {
  width: 100%;
  max-width: 1000px;
  background: #0f1e2e;
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.simulation-results-table table {
  width: 100%;
  border-collapse: collapse;
}

.simulation-results-table th,
.simulation-results-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.simulation-results-table th {
  font-weight: 600;
  color: #9dbbd7;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 16px;
}

.results-header h3 {
  margin: 0;
}

.results-caption {
  margin: 4px 0 0 0;
  color: #9ca3af;
  font-size: 14px;
}

.results-summary {
  font-size: 14px;
  color: #e0f2ff;
  background: rgba(73, 197, 255, 0.15);
  padding: 6px 12px;
  border-radius: 999px;
}

.status-pill {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pass {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.status-fail {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.btn-ghost {
  background: transparent;
  color: #49c5ff;
  border: 1px solid rgba(73, 197, 255, 0.4);
}

.btn-ghost:hover {
  background: rgba(73, 197, 255, 0.15);
}

.path-cell {
  max-width: 260px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.simulation-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
}

.simulation-result {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 100;
}

.result-popup {
  background: #1e3a5f;
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
}

.result-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 24px;
}

.result-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #49c5ff 0%, #ef4444 60%, #49c5ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  position: relative;
}

.result-circle::before {
  content: '';
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: #1e3a5f;
}

.result-value {
  position: relative;
  z-index: 1;
  font-size: 36px;
  font-weight: 700;
}

.gate-control-list {
  background: #1e2a3a;
  border-radius: 8px;
  padding: 24px;
  max-height: 600px;
  overflow: auto;
}

.gcl-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.gcl-table {
  width: 100%;
  border-collapse: collapse;
}

.gcl-table th,
.gcl-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.gcl-table th {
  background: #0f1e2e;
  font-weight: 600;
}

.chart-dialog {
  max-width: 760px;
}

.chart-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-canvas {
  width: 100%;
  background: #0b1b2d;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-bg {
  fill: rgba(255, 255, 255, 0.02);
  stroke: rgba(255, 255, 255, 0.08);
  stroke-dasharray: 4;
}

.allowable-line {
  stroke: #f87171;
  stroke-width: 2;
  stroke-dasharray: 8 4;
}

.latency-polyline {
  stroke: #49c5ff;
  stroke-width: 3;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: space-between;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-delay {
  background: #49c5ff;
}

.legend-limit {
  background: #f87171;
}

.legend-range {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #c7d7e6;
}

/* 浮动底部控制栏 */
.bottom-controls-floating {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  pointer-events: none;
}

.controls-group {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: rgba(30, 42, 58, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  pointer-events: all;
}

.controls-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #e6f1ff;
  font-size: 14px;
  user-select: none;
}

.controls-group label input[type="checkbox"] {
  cursor: pointer;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px;
  padding-left: 16px;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  color: #e6f1ff;
  font-size: 14px;
}

.zoom-value {
  min-width: 45px;
  text-align: center;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.zoom-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Modal 样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  background: #1e2a3a;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
}

.modal-subtitle {
  margin: 8px 0 0 0;
  color: #9ca3af;
  font-size: 14px;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group .required {
  color: #ef4444;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  background: #0f1e2e;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #49c5ff;
}

.form-group input.error {
  border-color: #ef4444;
}

.error-message {
  display: block;
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

.connection-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #49c5ff;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background: #1e2a3a;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  min-width: 150px;
  padding: 4px;
}

.context-menu-item {
  width: 100%;
  padding: 10px 16px;
  text-align: left;
  background: none;
  border: none;
  color: #e6f1ff;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-menu-item:hover {
  background: rgba(73, 197, 255, 0.2);
  color: #49c5ff;
}

/* 连接模式提示 */
.connecting-hint {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 999;
  background: rgba(251, 191, 36, 0.95);
  color: #1a1a1a;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 16px;
  font-weight: 600;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

/* 颜色选择器样式 */
.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker-wrapper input[type="color"] {
  width: 60px;
  height: 40px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  background: none;
  padding: 2px;
}

.color-picker-wrapper input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
  border-radius: 4px;
  overflow: hidden;
}

.color-picker-wrapper input[type="color"]::-webkit-color-swatch {
  border: none;
  border-radius: 4px;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.color-preview {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.color-value {
  color: rgba(214, 232, 255, 0.85);
  font-size: 14px;
  font-family: monospace;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  min-width: 80px;
}

/* 增强箭头可见性 */
.connection-line {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

/* Gate Control List 居中显示 */
.gate-control-list {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1001;
  background: #1e2a3a;
  border-radius: 12px;
  padding: 24px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: auto;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>

