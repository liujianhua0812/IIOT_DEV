<script setup>
import { ref, computed, onMounted } from 'vue'

// 策略列表
const strategies = ref([
  { id: 1, name: '工作日白天', active: true },
  { id: 2, name: '晚高峰', active: false },
  { id: 3, name: '周末', active: false },
  { id: 4, name: '节假日', active: false }
])

const selectedStrategy = ref(strategies.value[0])

// 车流控制规则
const trafficControlMode = ref('adaptive') // 定周期 / 流量自适应
const minCycleTime = ref(60)
const maxCycleTime = ref(180)
const priority = ref('balanced') // 主干道优先 / 平衡东西南北 / 行人友好

// 方向流量配置
const directionConfigs = ref([
  {
    direction: 'north',
    label: '北向',
    lowThreshold: 300,
    midThreshold: 800,
    highThreshold: 1200,
    lowGreenStrategy: 'min',
    midGreenStrategy: 'base',
    highGreenMaxPercent: 80
  },
  {
    direction: 'east',
    label: '东向',
    lowThreshold: 300,
    midThreshold: 800,
    highThreshold: 1200,
    lowGreenStrategy: 'min',
    midGreenStrategy: 'base',
    highGreenMaxPercent: 80
  },
  {
    direction: 'south',
    label: '南向',
    lowThreshold: 300,
    midThreshold: 800,
    highThreshold: 1200,
    lowGreenStrategy: 'min',
    midGreenStrategy: 'base',
    highGreenMaxPercent: 80
  },
  {
    direction: 'west',
    label: '西向',
    lowThreshold: 300,
    midThreshold: 800,
    highThreshold: 1200,
    lowGreenStrategy: 'min',
    midGreenStrategy: 'base',
    highGreenMaxPercent: 80
  }
])

// 人行流量控制规则
const pedestrianMaxWait = ref({
  normal: 60,
  peak: 90,
  night: 120
})
const pedestrianRequestWindow = ref(5) // 行人请求合并时间窗（秒）
const pedestrianPriority = ref('normal') // 正常 / 高

const controlModeOptions = [
  { value: 'fixed', label: '定周期' },
  { value: 'adaptive', label: '流量自适应（推荐）' }
]

const priorityOptions = [
  { value: 'main', label: '主干道优先' },
  { value: 'balanced', label: '平衡东西/南北' },
  { value: 'pedestrian', label: '行人友好' }
]

const pedestrianPriorityOptions = [
  { value: 'normal', label: '正常' },
  { value: 'high', label: '高（如学校门口）' }
]

const selectStrategy = (strategy) => {
  selectedStrategy.value = strategy
  strategies.value.forEach(s => s.active = s.id === strategy.id)
  // 这里可以加载策略的配置数据
}

const saveStrategy = async () => {
  // 将策略转换为信号机参数
  const config = {
    controlMode: trafficControlMode.value,
    cycleRange: {
      min: minCycleTime.value,
      max: maxCycleTime.value
    },
    priority: priority.value,
    directionConfigs: directionConfigs.value,
    pedestrianConfig: {
      maxWait: pedestrianMaxWait.value,
      requestWindow: pedestrianRequestWindow.value,
      priority: pedestrianPriority.value
    }
  }
  
  console.log('保存策略配置:', config)
  // TODO: 调用后端API保存配置
}

const addStrategy = () => {
  const newId = Math.max(...strategies.value.map(s => s.id)) + 1
  const newStrategy = {
    id: newId,
    name: `策略${newId}`,
    active: false
  }
  strategies.value.push(newStrategy)
  selectStrategy(newStrategy)
}

const deleteStrategy = (strategy) => {
  if (strategies.value.length <= 1) {
    alert('至少需要保留一个策略')
    return
  }
  const index = strategies.value.findIndex(s => s.id === strategy.id)
  if (index > -1) {
    strategies.value.splice(index, 1)
    if (selectedStrategy.value.id === strategy.id) {
      selectStrategy(strategies.value[0])
    }
  }
}
</script>

<template>
  <div class="strategy-view">
    <header class="page-header">
      <h1>流量驱动控制策略</h1>
      <p>配置车流和人流控制规则，系统自动转换为信号机参数</p>
    </header>

    <div class="strategy-layout">
      <!-- 左侧：策略列表 -->
      <aside class="strategy-list">
        <div class="list-header">
          <h3>策略列表</h3>
          <button class="add-btn" @click="addStrategy">+ 新建</button>
        </div>
        <div class="strategy-items">
          <div
            v-for="strategy in strategies"
            :key="strategy.id"
            :class="['strategy-item', { active: strategy.active }]"
            @click="selectStrategy(strategy)"
          >
            <span class="strategy-name">{{ strategy.name }}</span>
            <button
              class="delete-btn"
              @click.stop="deleteStrategy(strategy)"
              v-if="strategies.length > 1"
            >
              ×
            </button>
          </div>
        </div>
      </aside>

      <!-- 右侧：策略配置 -->
      <main class="strategy-config">
        <div class="config-header">
          <h2>{{ selectedStrategy.name }}配置</h2>
          <button class="save-btn" @click="saveStrategy">保存配置</button>
        </div>

        <div class="config-content">
          <!-- 车流控制规则 -->
          <section class="config-section">
            <h3 class="section-title">车流控制规则</h3>
            
            <div class="form-group">
              <label>控制模式</label>
              <select v-model="trafficControlMode" class="form-control">
                <option v-for="opt in controlModeOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>最小周期（秒）</label>
                <input
                  type="number"
                  v-model.number="minCycleTime"
                  class="form-control"
                  min="30"
                  max="300"
                />
              </div>
              <div class="form-group">
                <label>最大周期（秒）</label>
                <input
                  type="number"
                  v-model.number="maxCycleTime"
                  class="form-control"
                  min="60"
                  max="300"
                />
              </div>
            </div>

            <div class="form-group">
              <label>优先级</label>
              <select v-model="priority" class="form-control">
                <option v-for="opt in priorityOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <!-- 方向级别配置 -->
            <div class="direction-configs">
              <h4 class="subsection-title">方向级别配置</h4>
              <div
                v-for="config in directionConfigs"
                :key="config.direction"
                class="direction-config-card"
              >
                <h5>{{ config.label }}</h5>
                <div class="form-row">
                  <div class="form-group">
                    <label>低流量阈值（辆/小时）</label>
                    <input
                      type="number"
                      v-model.number="config.lowThreshold"
                      class="form-control"
                    />
                  </div>
                  <div class="form-group">
                    <label>中流量阈值（辆/小时）</label>
                    <input
                      type="number"
                      v-model.number="config.midThreshold"
                      class="form-control"
                    />
                  </div>
                  <div class="form-group">
                    <label>高流量阈值（辆/小时）</label>
                    <input
                      type="number"
                      v-model.number="config.highThreshold"
                      class="form-control"
                    />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>低流量绿灯策略</label>
                    <select v-model="config.lowGreenStrategy" class="form-control">
                      <option value="min">贴近最小绿</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>中流量绿灯策略</label>
                    <select v-model="config.midGreenStrategy" class="form-control">
                      <option value="base">基准绿</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>高流量最大绿百分比</label>
                    <input
                      type="range"
                      v-model.number="config.highGreenMaxPercent"
                      class="form-control range-input"
                      min="50"
                      max="100"
                    />
                    <span class="range-value">{{ config.highGreenMaxPercent }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- 人行流量控制规则 -->
          <section class="config-section">
            <h3 class="section-title">人行流量控制规则</h3>

            <div class="form-group">
              <label>行人最大允许等待 - 常规（秒）</label>
              <input
                type="number"
                v-model.number="pedestrianMaxWait.normal"
                class="form-control"
                min="30"
                max="180"
              />
            </div>

            <div class="form-group">
              <label>行人最大允许等待 - 高峰（秒）</label>
              <input
                type="number"
                v-model.number="pedestrianMaxWait.peak"
                class="form-control"
                min="30"
                max="180"
              />
            </div>

            <div class="form-group">
              <label>行人最大允许等待 - 夜间（秒）</label>
              <input
                type="number"
                v-model.number="pedestrianMaxWait.night"
                class="form-control"
                min="30"
                max="180"
              />
            </div>

            <div class="form-group">
              <label>行人请求合并时间窗（秒）</label>
              <input
                type="number"
                v-model.number="pedestrianRequestWindow"
                class="form-control"
                min="1"
                max="30"
              />
              <small>连续请求在此时间窗内将合并为一次</small>
            </div>

            <div class="form-group">
              <label>行人优先级</label>
              <select v-model="pedestrianPriority" class="form-control">
                <option v-for="opt in pedestrianPriorityOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.strategy-view {
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
  color: #d6ecff;
}

.page-header p {
  color: rgba(214, 232, 255, 0.7);
  font-size: 14px;
}

.strategy-layout {
  display: flex;
  gap: 24px;
  height: calc(100vh - 200px);
}

.strategy-list {
  width: 280px;
  background: rgba(7, 27, 44, 0.7);
  border: 1px solid rgba(88, 178, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h3 {
  font-size: 18px;
  margin: 0;
}

.add-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  background: rgba(88, 178, 255, 0.1);
  color: #58b2ff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.add-btn:hover {
  background: rgba(88, 178, 255, 0.2);
}

.strategy-items {
  flex: 1;
  overflow-y: auto;
}

.strategy-item {
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: rgba(9, 26, 43, 0.5);
  border: 1px solid rgba(88, 178, 255, 0.1);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s;
}

.strategy-item:hover {
  background: rgba(88, 178, 255, 0.1);
  border-color: rgba(88, 178, 255, 0.3);
}

.strategy-item.active {
  background: linear-gradient(135deg, #58b2ff, #5be3ff);
  color: #03121f;
  border-color: transparent;
}

.strategy-name {
  font-weight: 500;
}

.delete-btn {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 77, 79, 0.2);
  color: #ff4d4f;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.delete-btn:hover {
  background: rgba(255, 77, 79, 0.4);
}

.strategy-config {
  flex: 1;
  background: rgba(7, 27, 44, 0.7);
  border: 1px solid rgba(88, 178, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
}

.config-header h2 {
  font-size: 22px;
  margin: 0;
}

.save-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #58b2ff, #5be3ff);
  color: #03121f;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.save-btn:hover {
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.3);
}

.config-content {
  flex: 1;
  overflow-y: auto;
}

.config-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
}

.subsection-title {
  font-size: 16px;
  margin: 20px 0 16px;
  color: rgba(214, 232, 255, 0.9);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: rgba(214, 232, 255, 0.8);
}

.form-group small {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid rgba(88, 178, 255, 0.2);
  background: rgba(9, 26, 43, 0.6);
  color: #d6ecff;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #58b2ff;
  box-shadow: 0 0 0 2px rgba(88, 178, 255, 0.2);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.direction-configs {
  margin-top: 24px;
}

.direction-config-card {
  padding: 20px;
  margin-bottom: 16px;
  background: rgba(9, 26, 43, 0.5);
  border: 1px solid rgba(88, 178, 255, 0.1);
  border-radius: 12px;
}

.direction-config-card h5 {
  font-size: 16px;
  margin: 0 0 16px;
  color: #58b2ff;
}

.range-input {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(88, 178, 255, 0.2);
  outline: none;
  -webkit-appearance: none;
}

.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #58b2ff;
  cursor: pointer;
}

.range-input::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #58b2ff;
  cursor: pointer;
  border: none;
}

.range-value {
  display: inline-block;
  margin-left: 12px;
  font-weight: 600;
  color: #58b2ff;
}
</style>

