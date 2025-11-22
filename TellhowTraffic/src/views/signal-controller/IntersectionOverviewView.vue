<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('lane')
const selectedLane = ref(null)
const selectedCrosswalk = ref(null)

// 车道配置数据
const laneForm = ref({
  direction: '',
  movement: '',
  laneType: 'motor',
  signalGroup: '',
  detectors: [],
  saturationFlowRate: 1800
})

// 人行过街配置数据
const crosswalkForm = ref({
  crosswalkNumber: '',
  detectionMethod: 'button',
  maxWaitTime: 60,
  minGreenTime: 15,
  greenFlashTime: 3
})

const directionOptions = [
  { key: 'east', label: '东进口', movements: ['left', 'straight', 'right'] },
  { key: 'south', label: '南进口', movements: ['left', 'straight', 'right'] },
  { key: 'west', label: '西进口', movements: ['left', 'straight', 'right'] },
  { key: 'north', label: '北进口', movements: ['left', 'straight', 'right'] }
]

const movementOptions = {
  left: '左转',
  straight: '直行',
  right: '右转'
}

const laneTypeOptions = [
  { value: 'motor', label: '机动车' },
  { value: 'non-motor', label: '非机动车' },
  { value: 'bus', label: '公交专用' }
]

const signalGroups = ref([
  { value: '1', label: '通道1' },
  { value: '2', label: '通道2' },
  { value: '3', label: '通道3' },
  { value: '4', label: '通道4' }
])

const detectors = ref([
  { value: 'detector-1', label: '检测器1' },
  { value: 'detector-2', label: '检测器2' },
  { value: 'detector-3', label: '检测器3' }
])

const detectionMethods = [
  { value: 'button', label: '按钮' },
  { value: 'camera', label: '行人相机' },
  { value: 'none', label: '无检测（纯按时间）' }
]

const handleLaneClick = (direction, movement) => {
  selectedLane.value = { direction, movement }
  laneForm.value.direction = direction
  laneForm.value.movement = movement
  activeTab.value = 'lane'
}

const handleCrosswalkClick = (crosswalkId) => {
  selectedCrosswalk.value = crosswalkId
  crosswalkForm.value.crosswalkNumber = crosswalkId
  activeTab.value = 'crosswalk'
}

const saveLaneConfig = () => {
  console.log('保存车道配置:', laneForm.value)
  // TODO: 调用后台API保存配置
}

const saveCrosswalkConfig = () => {
  console.log('保存人行过街配置:', crosswalkForm.value)
  // TODO: 调用后台API保存配置
}

onMounted(() => {
  // TODO: 加载路口数据和配置
})
</script>

<template>
  <div class="intersection-overview">
    <header class="page-header">
      <h1>路口概览 & 拓扑配置</h1>
      <p>配置路口结构和检测器关联</p>
    </header>

    <!-- 路口图区域 -->
    <section class="intersection-diagram">
      <div class="diagram-container">
        <!-- 这里可以集成2D/3D路口图组件 -->
        <div class="diagram-placeholder">
          <p>路口俯视图（2D/3D）</p>
          <div class="mock-diagram">
            <div class="road horizontal"></div>
            <div class="road vertical"></div>
            <div class="lanes">
              <div 
                v-for="dir in directionOptions" 
                :key="dir.key"
                class="direction-group"
                :class="dir.key"
              >
                <button
                  v-for="mov in dir.movements"
                  :key="mov"
                  class="lane-btn"
                  @click="handleLaneClick(dir.key, mov)"
                >
                  {{ dir.label }}{{ movementOptions[mov] }}
                </button>
              </div>
            </div>
            <div class="crosswalks">
              <button
                v-for="i in 4"
                :key="i"
                class="crosswalk-btn"
                @click="handleCrosswalkClick(`crosswalk-${i}`)"
              >
                斑马线{{ i }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 配置表单区域 -->
    <section class="config-section">
      <div class="tabs">
        <button
          :class="['tab', { active: activeTab === 'lane' }]"
          @click="activeTab = 'lane'"
        >
          车道配置
        </button>
        <button
          :class="['tab', { active: activeTab === 'crosswalk' }]"
          @click="activeTab = 'crosswalk'"
        >
          人行过街配置
        </button>
      </div>

      <!-- 车道配置表单 -->
      <div v-if="activeTab === 'lane'" class="config-form">
        <div v-if="!selectedLane" class="empty-state">
          <p>请在上方路口图中点击车道进行配置</p>
        </div>
        <div v-else class="form-content">
          <h3>车道配置 - {{ directionOptions.find(d => d.key === selectedLane.direction)?.label }}{{ movementOptions[selectedLane.movement] }}</h3>
          
          <div class="form-group">
            <label>车道方向</label>
            <div class="direction-selector">
              <select v-model="laneForm.direction" class="form-control">
                <option value="">请选择</option>
                <option v-for="dir in directionOptions" :key="dir.key" :value="dir.key">
                  {{ dir.label }}
                </option>
              </select>
              <select v-model="laneForm.movement" class="form-control">
                <option value="">请选择</option>
                <option v-for="(label, key) in movementOptions" :key="key" :value="key">
                  {{ label }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>车道类型</label>
            <select v-model="laneForm.laneType" class="form-control">
              <option v-for="opt in laneTypeOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>关联信号灯组</label>
            <select v-model="laneForm.signalGroup" class="form-control">
              <option value="">请选择</option>
              <option v-for="group in signalGroups" :key="group.value" :value="group.value">
                {{ group.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>关联车检器（可多选）</label>
            <div class="checkbox-group">
              <label v-for="detector in detectors" :key="detector.value" class="checkbox-label">
                <input
                  type="checkbox"
                  :value="detector.value"
                  v-model="laneForm.detectors"
                />
                {{ detector.label }}
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>车道饱和流率（辆/小时·车道）</label>
            <input
              type="number"
              v-model.number="laneForm.saturationFlowRate"
              class="form-control"
              min="0"
            />
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="saveLaneConfig">保存配置</button>
            <button class="btn btn-secondary" @click="selectedLane = null">取消</button>
          </div>
        </div>
      </div>

      <!-- 人行过街配置表单 -->
      <div v-if="activeTab === 'crosswalk'" class="config-form">
        <div v-if="!selectedCrosswalk" class="empty-state">
          <p>请在上方路口图中点击斑马线进行配置</p>
        </div>
        <div v-else class="form-content">
          <h3>人行过街配置 - {{ selectedCrosswalk }}</h3>

          <div class="form-group">
            <label>所属人行过街编号</label>
            <input
              type="text"
              v-model="crosswalkForm.crosswalkNumber"
              class="form-control"
              placeholder="例如：crosswalk-1"
            />
          </div>

          <div class="form-group">
            <label>关联行人检测方式</label>
            <select v-model="crosswalkForm.detectionMethod" class="form-control">
              <option v-for="method in detectionMethods" :key="method.value" :value="method.value">
                {{ method.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>最大等待时间（秒）</label>
            <input
              type="number"
              v-model.number="crosswalkForm.maxWaitTime"
              class="form-control"
              min="0"
            />
          </div>

          <div class="form-group">
            <label>行人绿灯最小时间（秒）</label>
            <input
              type="number"
              v-model.number="crosswalkForm.minGreenTime"
              class="form-control"
              min="0"
            />
          </div>

          <div class="form-group">
            <label>行人绿闪时间（秒）</label>
            <input
              type="number"
              v-model.number="crosswalkForm.greenFlashTime"
              class="form-control"
              min="0"
            />
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="saveCrosswalkConfig">保存配置</button>
            <button class="btn btn-secondary" @click="selectedCrosswalk = null">取消</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.intersection-overview {
  padding: 32px 48px;
  min-height: calc(100vh - 80px);
  background: radial-gradient(circle at top, rgba(5, 26, 43, 0.95), rgba(3, 13, 23, 0.96));
  color: #e6f1ff;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.page-header p {
  color: rgba(214, 232, 255, 0.7);
  font-size: 14px;
}

.intersection-diagram {
  margin-bottom: 32px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 20px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  padding: 24px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
}

.diagram-container {
  width: 100%;
  min-height: 400px;
}

.diagram-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(214, 232, 255, 0.6);
}

.mock-diagram {
  position: relative;
  width: 600px;
  height: 600px;
  margin-top: 20px;
  background: rgba(7, 27, 44, 0.5);
  border-radius: 12px;
}

.road {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
}

.road.horizontal {
  top: 50%;
  left: 0;
  width: 100%;
  height: 120px;
  transform: translateY(-50%);
}

.road.vertical {
  left: 50%;
  top: 0;
  width: 120px;
  height: 100%;
  transform: translateX(-50%);
}

.lanes {
  position: absolute;
  inset: 0;
  z-index: 5;
  pointer-events: none;
}

.lanes > * {
  pointer-events: auto;
}

.direction-group {
  position: absolute;
  display: flex;
  gap: 10px;
  z-index: 10;
  pointer-events: auto;
}

.direction-group.east {
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  flex-direction: column;
}

.direction-group.west {
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  flex-direction: column;
}

.direction-group.north {
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: row;
}

.direction-group.south {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: row;
}

.lane-btn {
  padding: 10px 16px;
  background: rgba(88, 178, 255, 0.2);
  border: 1px solid rgba(88, 178, 255, 0.4);
  border-radius: 6px;
  color: #d6ecff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
  z-index: 10;
  position: relative;
  min-width: 80px;
}

.lane-btn:hover {
  background: rgba(88, 178, 255, 0.4);
  border-color: #58b2ff;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.3);
}

.lane-btn:active {
  transform: scale(0.98);
}

.crosswalks {
  position: absolute;
  inset: 0;
  z-index: 5;
  pointer-events: none;
}

.crosswalks > * {
  pointer-events: auto;
}

.crosswalk-btn {
  position: absolute;
  padding: 8px 12px;
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.4);
  border-radius: 6px;
  color: #ffc107;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  z-index: 10;
  min-width: 70px;
}

.crosswalk-btn:nth-child(1) {
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
}

.crosswalk-btn:nth-child(2) {
  right: 20%;
  top: 50%;
  transform: translateY(-50%);
}

.crosswalk-btn:nth-child(3) {
  bottom: 20%;
  left: 50%;
  transform: translateX(-50%);
}

.crosswalk-btn:nth-child(4) {
  left: 20%;
  top: 50%;
  transform: translateY(-50%);
}

.crosswalk-btn:hover {
  background: rgba(255, 193, 7, 0.4);
  border-color: #ffc107;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

.crosswalk-btn:active {
  transform: scale(0.98);
}

.config-section {
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 20px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  padding: 24px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
}

.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.2);
}

.tab {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: rgba(214, 232, 255, 0.7);
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s ease;
}

.tab:hover {
  color: #d6ecff;
}

.tab.active {
  color: #49c5ff;
  border-bottom-color: #49c5ff;
}

.config-form {
  min-height: 400px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: rgba(214, 232, 255, 0.5);
}

.form-content h3 {
  margin-bottom: 24px;
  font-size: 18px;
  color: #d6ecff;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(214, 232, 255, 0.8);
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  background: rgba(7, 27, 44, 0.8);
  border: 1px solid rgba(88, 178, 255, 0.3);
  border-radius: 8px;
  color: #d6ecff;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #49c5ff;
  box-shadow: 0 0 0 2px rgba(73, 197, 255, 0.2);
}

.direction-selector {
  display: flex;
  gap: 12px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(214, 232, 255, 0.8);
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(88, 178, 255, 0.2);
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  color: #0b2338;
  font-weight: 600;
}

.btn-primary:hover {
  box-shadow: 0 8px 20px rgba(73, 197, 255, 0.3);
  transform: translateY(-2px);
}

.btn-secondary {
  background: rgba(7, 27, 44, 0.8);
  color: #d6ecff;
  border: 1px solid rgba(88, 178, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(88, 178, 255, 0.15);
  border-color: rgba(88, 178, 255, 0.5);
}
</style>