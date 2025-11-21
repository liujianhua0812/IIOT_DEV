<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({}),
  },
})

const metricsList = computed(() => [
  {
    key: 'congestionIndex',
    label: '实时拥堵指数',
    unit: '',
    gradient: 'linear-gradient(135deg, #ff7eb3, #ff758c)',
  },
  {
    key: 'avgSpeed',
    label: '路口平均车速',
    unit: 'km/h',
    gradient: 'linear-gradient(135deg, #43cea2, #185a9d)',
  },
  {
    key: 'queueLength',
    label: '排队长度',
    unit: 'm',
    gradient: 'linear-gradient(135deg, #f7971e, #ffd200)',
  },
])
</script>

<template>
  <section class="metrics-grid">
    <article v-for="item in metricsList" :key="item.key" class="metric-card">
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

