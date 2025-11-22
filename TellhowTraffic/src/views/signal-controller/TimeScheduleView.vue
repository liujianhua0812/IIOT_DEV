<script setup>
import { ref, computed, onMounted } from 'vue'

// 策略组合列表
const strategyGroups = ref([
  { id: 1, name: '工作日' },
  { id: 2, name: '周末' },
  { id: 3, name: '节假日' }
])

const selectedStrategyGroup = ref(strategyGroups.value[0])

// 一周7天
const weekDays = ref([
  { key: 'monday', label: '周一', value: 1 },
  { key: 'tuesday', label: '周二', value: 2 },
  { key: 'wednesday', label: '周三', value: 3 },
  { key: 'thursday', label: '周四', value: 4 },
  { key: 'friday', label: '周五', value: 5 },
  { key: 'saturday', label: '周六', value: 6 },
  { key: 'sunday', label: '周日', value: 0 }
])

const selectedDay = ref(weekDays.value[0])

// 时间轴配置（24小时，每30分钟一个时间段）
const timeSlots = computed(() => {
  const slots = []
  for (let hour = 0; hour < 24; hour++) {
    slots.push({
      hour,
      minute: 0,
      label: `${String(hour).padStart(2, '0')}:00`,
      value: hour * 60
    })
    slots.push({
      hour,
      minute: 30,
      label: `${String(hour).padStart(2, '0')}:30`,
      value: hour * 60 + 30
    })
  }
  return slots
})

// 时间段块
const timeBlocks = ref([
  {
    id: 1,
    day: 'monday',
    start: 0, // 00:00
    end: 360, // 06:00
    strategy: null,
    mode: 'normal'
  },
  {
    id: 2,
    day: 'monday',
    start: 360, // 06:00
    end: 540, // 09:00
    strategy: 1,
    mode: 'normal'
  },
  {
    id: 3,
    day: 'monday',
    start: 540, // 09:00
    end: 1080, // 18:00
    strategy: 1,
    mode: 'normal'
  },
  {
    id: 4,
    day: 'monday',
    start: 1080, // 18:00
    end: 1440, // 24:00
    strategy: 1,
    mode: 'normal'
  }
])

// 控制模式选项
const controlModes = [
  { value: 'normal', label: '正常（流量策略）' },
  { value: 'yellow-flash', label: '黄闪' },
  { value: 'all-red', label: '全红' }
]

// 当前选中的时间段块
const selectedBlock = ref(null)

// 特殊日期列表
const specialDates = ref([
  { date: '2024-01-01', label: '元旦', schedule: [] },
  { date: '2024-05-01', label: '劳动节', schedule: [] }
])

// 获取某一天的时间块
const getDayBlocks = (dayKey) => {
  return timeBlocks.value.filter(block => block.day === dayKey)
    .sort((a, b) => a.start - b.start)
}

// 添加时间段块
const addTimeBlock = () => {
  const existingBlocks = getDayBlocks(selectedDay.value.key)
  const lastBlock = existingBlocks[existingBlocks.length - 1]
  const newStart = lastBlock ? lastBlock.end : 0
  const newEnd = Math.min(newStart + 120, 1440) // 默认2小时

  const newBlock = {
    id: Date.now(),
    day: selectedDay.value.key,
    start: newStart,
    end: newEnd,
    strategy: selectedStrategyGroup.value.id,
    mode: 'normal'
  }
  timeBlocks.value.push(newBlock)
  selectedBlock.value = newBlock
}

// 删除时间段块
const deleteTimeBlock = (block) => {
  const index = timeBlocks.value.findIndex(b => b.id === block.id)
  if (index > -1) {
    timeBlocks.value.splice(index, 1)
    if (selectedBlock.value?.id === block.id) {
      selectedBlock.value = null
    }
  }
}

// 计算时间段块在时间轴上的位置和宽度
const getBlockStyle = (block) => {
  const startPercent = (block.start / 1440) * 100
  const widthPercent = ((block.end - block.start) / 1440) * 100
  return {
    left: `${startPercent}%`,
    width: `${widthPercent}%`
  }
}

// 获取时间段块的标签
const getBlockLabel = (block) => {
  const startHour = Math.floor(block.start / 60)
  const startMin = block.start % 60
  const endHour = Math.floor(block.end / 60)
  const endMin = block.end % 60
  return `${String(startHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')} - ${String(endHour).padStart(2, '0')}:${String(endMin).padStart(2, '0')}`
}

// 保存时间计划
const saveSchedule = async () => {
  const schedule = {
    strategyGroup: selectedStrategyGroup.value.id,
    daySchedules: weekDays.value.map(day => ({
      day: day.key,
      blocks: getDayBlocks(day.key)
    })),
    specialDates: specialDates.value
  }
  
  console.log('保存时间计划:', schedule)
  // TODO: 调用后端API保存
}

// 复制某一天的配置到其他天
const copyDaySchedule = (fromDay, toDays) => {
  const fromBlocks = getDayBlocks(fromDay.key)
  toDays.forEach(toDay => {
    // 删除目标天的现有块
    timeBlocks.value = timeBlocks.value.filter(b => b.day !== toDay.key)
    // 复制块
    fromBlocks.forEach(block => {
      timeBlocks.value.push({
        ...block,
        id: Date.now() + Math.random(),
        day: toDay.key
      })
    })
  })
}
</script>

<template>
  <div class="schedule-view">
    <header class="page-header">
      <h1>时间计划</h1>
      <p>配置不同时间段使用的控制策略</p>
    </header>

    <div class="schedule-layout">
      <!-- 左侧：日期选择 -->
      <aside class="date-selector">
        <div class="selector-section">
          <h3>策略组合</h3>
          <select v-model="selectedStrategyGroup" class="form-control">
            <option
              v-for="group in strategyGroups"
              :key="group.id"
              :value="group"
            >
              {{ group.name }}
            </option>
          </select>
        </div>

        <div class="selector-section">
          <h3>工作日</h3>
          <div class="day-list">
            <button
              v-for="day in weekDays"
              :key="day.key"
              :class="['day-btn', { active: selectedDay.key === day.key }]"
              @click="selectedDay = day"
            >
              {{ day.label }}
            </button>
          </div>
        </div>

        <div class="selector-section">
          <h3>特殊日期</h3>
          <div class="special-dates">
            <div
              v-for="special in specialDates"
              :key="special.date"
              class="special-date-item"
            >
              <span>{{ special.label }}</span>
              <span class="date-text">{{ special.date }}</span>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="action-btn" @click="copyDaySchedule(selectedDay, weekDays.filter(d => d.key !== selectedDay.key))">
            复制到所有天
          </button>
        </div>
      </aside>

      <!-- 右侧：时间轴编辑器 -->
      <main class="timeline-editor">
        <div class="editor-header">
          <h2>{{ selectedDay.label }}时间计划</h2>
          <div class="header-actions">
            <button class="add-block-btn" @click="addTimeBlock">+ 添加时间段</button>
            <button class="save-btn" @click="saveSchedule">保存计划</button>
          </div>
        </div>

        <div class="timeline-container">
          <!-- 时间轴刻度 -->
          <div class="timeline-ruler">
            <div
              v-for="slot in timeSlots"
              :key="slot.value"
              class="time-marker"
              :style="{ left: `${(slot.value / 1440) * 100}%` }"
            >
              <span class="marker-line"></span>
              <span class="marker-label">{{ slot.label }}</span>
            </div>
          </div>

          <!-- 时间段块 -->
          <div class="timeline-blocks">
            <div
              v-for="block in getDayBlocks(selectedDay.key)"
              :key="block.id"
              :class="['time-block', { selected: selectedBlock?.id === block.id }]"
              :style="getBlockStyle(block)"
              @click="selectedBlock = block"
            >
              <div class="block-content">
                <div class="block-time">{{ getBlockLabel(block) }}</div>
                <div class="block-info">
                  <span class="block-strategy">策略{{ block.strategy || '未设置' }}</span>
                  <span class="block-mode">{{ controlModes.find(m => m.value === block.mode)?.label }}</span>
                </div>
              </div>
              <button class="block-delete" @click.stop="deleteTimeBlock(block)">×</button>
            </div>
          </div>
        </div>

        <!-- 选中块的配置表单 -->
        <div v-if="selectedBlock" class="block-config">
          <h3>时间段配置</h3>
          <div class="form-group">
            <label>开始时间</label>
            <input
              type="time"
              :value="`${String(Math.floor(selectedBlock.start / 60)).padStart(2, '0')}:${String(selectedBlock.start % 60).padStart(2, '0')}`"
              @change="(e) => {
                const [h, m] = e.target.value.split(':').map(Number)
                selectedBlock.start = h * 60 + m
              }"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label>结束时间</label>
            <input
              type="time"
              :value="`${String(Math.floor(selectedBlock.end / 60)).padStart(2, '0')}:${String(selectedBlock.end % 60).padStart(2, '0')}`"
              @change="(e) => {
                const [h, m] = e.target.value.split(':').map(Number)
                selectedBlock.end = h * 60 + m
              }"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label>使用策略</label>
            <select
              v-model.number="selectedBlock.strategy"
              class="form-control"
            >
              <option :value="null">未设置</option>
              <option
                v-for="group in strategyGroups"
                :key="group.id"
                :value="group.id"
              >
                {{ group.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>控制模式</label>
            <select v-model="selectedBlock.mode" class="form-control">
              <option
                v-for="mode in controlModes"
                :key="mode.value"
                :value="mode.value"
              >
                {{ mode.label }}
              </option>
            </select>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.schedule-view {
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

.schedule-layout {
  display: flex;
  gap: 24px;
  height: calc(100vh - 200px);
}

.date-selector {
  width: 280px;
  background: rgba(7, 27, 44, 0.7);
  border: 1px solid rgba(88, 178, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.selector-section h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: #58b2ff;
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

.day-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.day-btn {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid rgba(88, 178, 255, 0.2);
  background: rgba(9, 26, 43, 0.5);
  color: #d6ecff;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.day-btn:hover {
  background: rgba(88, 178, 255, 0.1);
  border-color: rgba(88, 178, 255, 0.4);
}

.day-btn.active {
  background: linear-gradient(135deg, #58b2ff, #5be3ff);
  color: #03121f;
  border-color: transparent;
}

.special-dates {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.special-date-item {
  padding: 10px;
  border-radius: 8px;
  background: rgba(9, 26, 43, 0.5);
  border: 1px solid rgba(88, 178, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-text {
  font-size: 12px;
  color: rgba(214, 232, 255, 0.6);
}

.actions {
  margin-top: auto;
}

.action-btn {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid rgba(88, 178, 255, 0.3);
  background: rgba(88, 178, 255, 0.1);
  color: #58b2ff;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: rgba(88, 178, 255, 0.2);
}

.timeline-editor {
  flex: 1;
  background: rgba(7, 27, 44, 0.7);
  border: 1px solid rgba(88, 178, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(88, 178, 255, 0.1);
}

.editor-header h2 {
  font-size: 22px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.add-block-btn,
.save-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.add-block-btn {
  background: rgba(88, 178, 255, 0.1);
  color: #58b2ff;
  border: 1px solid rgba(88, 178, 255, 0.3);
}

.add-block-btn:hover {
  background: rgba(88, 178, 255, 0.2);
}

.save-btn {
  background: linear-gradient(135deg, #58b2ff, #5be3ff);
  color: #03121f;
  font-weight: 600;
}

.save-btn:hover {
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.3);
}

.timeline-container {
  position: relative;
  margin-bottom: 24px;
  min-height: 120px;
  background: rgba(9, 26, 43, 0.5);
  border-radius: 12px;
  padding: 20px;
}

.timeline-ruler {
  position: relative;
  height: 40px;
  border-bottom: 2px solid rgba(88, 178, 255, 0.3);
}

.time-marker {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
}

.marker-line {
  display: block;
  width: 2px;
  height: 20px;
  background: rgba(88, 178, 255, 0.5);
}

.marker-label {
  display: block;
  font-size: 11px;
  color: rgba(214, 232, 255, 0.7);
  margin-top: 4px;
  white-space: nowrap;
}

.timeline-blocks {
  position: relative;
  margin-top: 20px;
  height: 60px;
}

.time-block {
  position: absolute;
  top: 0;
  height: 100%;
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.3), rgba(91, 227, 255, 0.3));
  border: 2px solid rgba(88, 178, 255, 0.5);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
}

.time-block:hover {
  background: linear-gradient(135deg, rgba(88, 178, 255, 0.4), rgba(91, 227, 255, 0.4));
  border-color: #58b2ff;
  z-index: 10;
}

.time-block.selected {
  background: linear-gradient(135deg, #58b2ff, #5be3ff);
  border-color: #58b2ff;
  box-shadow: 0 4px 12px rgba(88, 178, 255, 0.4);
  z-index: 20;
}

.block-content {
  flex: 1;
  padding: 8px;
  text-align: center;
}

.block-time {
  font-size: 11px;
  font-weight: 600;
  color: #03121f;
  margin-bottom: 4px;
}

.block-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 10px;
  color: rgba(3, 18, 31, 0.8);
}

.block-delete {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 77, 79, 0.9);
  color: white;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.block-delete:hover {
  background: #ff4d4f;
  transform: scale(1.1);
}

.block-config {
  padding: 20px;
  background: rgba(9, 26, 43, 0.5);
  border: 1px solid rgba(88, 178, 255, 0.1);
  border-radius: 12px;
}

.block-config h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: #58b2ff;
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
</style>

