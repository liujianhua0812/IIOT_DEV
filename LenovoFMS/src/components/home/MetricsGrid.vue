<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({}),
  },
})

const adminBaseURL = import.meta.env.VITE_ADMIN_BASE_URL || 'http://localhost:10062'

const metricsList = computed(() => [
  {
    key: 'labelTypes',
    label: '标签类型',
    unit: '种',
    gradient: 'linear-gradient(135deg, #7f7bff, #5fd4ff)',
    clickable: true,
  },
  {
    key: 'deviceCount',
    label: '接入设备数',
    unit: '台',
    gradient: 'linear-gradient(135deg, #3d8bff, #1cb5e0)',
  },
  {
    key: 'modalTypes',
    label: '模态类型',
    unit: '类',
    gradient: 'linear-gradient(135deg, #4facfe, #00f2fe)',
  },
  {
    key: 'securityEvents',
    label: '安全防护次数',
    unit: '次',
    gradient: 'linear-gradient(135deg, #fa709a, #fee140)',
  },
  {
    key: 'dispatchTasks',
    label: '调度任务',
    unit: '项',
    gradient: 'linear-gradient(135deg, #84fab0, #8fd3f4)',
  },
])

const handleCardClick = (item) => {
  if (item.clickable && item.key === 'labelTypes') {
    window.open(`${adminBaseURL}/label-types`, '_blank', 'noopener')
  }
}
</script>

<template>
  <section class="metrics-grid">
    <article
      v-for="item in metricsList"
      :key="item.key"
      class="metric-card"
      :class="{ clickable: item.clickable }"
      @click="handleCardClick(item)"
    >
      <div class="metric-header" :style="{ backgroundImage: item.gradient }"></div>
      <div class="metric-body">
        <span class="metric-label">{{ item.label }}</span>
        <div class="metric-value">
          <strong>{{ props.metrics[item.key] ?? '--' }}</strong>
          <span class="metric-unit">{{ item.unit }}</span>
        </div>
      </div>
    </article>
  </section>
</template>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.metric-card {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  background: rgba(7, 27, 44, 0.7);
  border: 1px solid rgba(88, 178, 255, 0.08);
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(14px);
}

.metric-card.clickable {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card.clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 40px rgba(0, 0, 0, 0.35);
}

.metric-header {
  height: 110px;
  filter: saturate(125%);
}

.metric-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metric-label {
  color: rgba(214, 232, 255, 0.72);
  font-weight: 500;
  letter-spacing: 1px;
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: 10px;
  color: #eff6ff;
}

.metric-value strong {
  font-size: 36px;
  font-weight: 700;
  letter-spacing: 2px;
}

.metric-unit {
  font-size: 16px;
  opacity: 0.75;
}
</style>

