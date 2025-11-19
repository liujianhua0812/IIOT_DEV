<template>
  <div id="LevelBarChart" class="chart-container"></div>
</template>

<script setup>
import { onMounted, watch, ref } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      utilizationRate: { cpu: 0, memory: 0, storage: 0, network: 0 }
    })
  }
});

const chartInstance = ref(null);

const initChart = () => {
  if (!props.data || !props.data.utilizationRate) return; // 安全检查

  const chartDom = document.getElementById('LevelBarChart');
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartDom);
  }

  const option = {
    title: {
      text: '资源使用情况',
      left: 'center',
      textStyle: {
        color: '#00d1ff',
        fontSize: 20,
        fontFamily: 'Orbitron, sans-serif'
      }
    },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['CPU', '内存', '存储', '网络'],
      axisLabel: { color: '#fff' }
    },
    yAxis: { type: 'value', axisLabel: { color: '#fff' } },
    series: [
      {
        name: '利用率',
        type: 'bar',
        data: [
          props.data.utilizationRate.cpu || 0,
          props.data.utilizationRate.memory || 0,
          props.data.utilizationRate.storage || 0,
          props.data.utilizationRate.network || 0
        ],
        itemStyle: {
          color: function (params) {
            const colorList = ['#00d1ff', '#3e82f7', '#04befe', '#89e6ff'];
            return colorList[params.dataIndex];
          }
        }
      }
    ]
  };

  chartInstance.value.setOption(option);
};

// 监听 data 的变化，深度更新图表
watch(() => props.data, (newVal) => {
  if (newVal && newVal.utilizationRate) {
    initChart();
  }
}, { deep: true });

onMounted(() => {
  initChart();
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 350px;
}
</style>
