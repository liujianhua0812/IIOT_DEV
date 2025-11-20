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
    label: '支持标签类型',
    unit: '种',
    gradient: 'linear-gradient(135deg, #7f7bff, #5fd4ff)',
    clickable: true,
  },
  {
    key: 'supportedLaptops',
    label: '支持笔记本型号',
    unit: '款',
    gradient: 'linear-gradient(135deg, #ff9a9e, #fad0c4)',
  }, 
  {
    key: 'stableDays',
    label: '稳定运行天数',
    unit: '天',
    gradient: 'linear-gradient(135deg, #ffecd2, #fcb69f)',
  },
  {
    key: 'completedOrders',
    label: '已完成订单数',
    unit: '单',
    gradient: 'linear-gradient(135deg, #a18cd1, #fbc2eb)',
  },
  {
    key: 'completedProducts',
    label: '已完成产品数',
    unit: '件',
    gradient: 'linear-gradient(135deg, #f6d365, #fda085)',
  },
  {
    key: 'labelQcAlarms',
    label: '贴标质检告警数',
    unit: '次',
    gradient: 'linear-gradient(135deg, #f093fb, #f5576c)',
  },
  {
    key: 'dailyCycleTime',
    label: '平均节拍',
    unit: '秒',
    gradient: 'linear-gradient(135deg, #96fbc4, #f9f586)',
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

