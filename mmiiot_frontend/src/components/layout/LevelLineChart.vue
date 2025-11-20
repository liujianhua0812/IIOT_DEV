<template>
  <div id="LevelLineChart" class="chart-container"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const initChart = () => {
  const chartDom = document.getElementById('LevelLineChart');
  const myChart = echarts.init(chartDom);
  const option = {
    title: {
      text: '任务完成时间',
      left: 'center',
      textStyle: {
        color: '#00d1ff',
        fontSize: 20,
        fontFamily: 'Orbitron, sans-serif'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月'],
      axisLabel: {
        color: '#fff'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#fff'
      }
    },
    series: [
      {
        name: '完成时间',
        type: 'line',
        data: [
          props.data.averageTaskCompletionTime,
          props.data.averageTaskCompletionTime - 2,
          props.data.averageTaskCompletionTime + 1,
          props.data.averageTaskCompletionTime - 1,
          props.data.averageTaskCompletionTime + 3,
          props.data.averageTaskCompletionTime - 2
        ],
        itemStyle: {
          color: '#00d1ff'
        },
        lineStyle: {
          color: '#00d1ff'
        }
      }
    ]
  };
  option && myChart.setOption(option);
};

watch(() => props.data, (newVal) => {
  if (newVal && newVal.averageTaskCompletionTime) {
    initChart();
  }
});

onMounted(() => {
  initChart();
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}
</style>
