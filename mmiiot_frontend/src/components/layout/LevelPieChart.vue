<template>
  <div id="LevelPieChart" class="chart-container"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import * as echarts from 'echarts';

// 定义接收的props
const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const initChart = () => {
  const chartDom = document.getElementById('LevelPieChart');
  const myChart = echarts.init(chartDom);
  const option = {
    title: {
      text: '资源利用率',
      left: 'center',
      textStyle: {
        color: '#00d1ff',
        fontSize: 20,
        fontFamily: 'Orbitron, sans-serif'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      left: 'left',
      top: '10%',
      textStyle: {
        color: '#fff',
        fontSize: 15,
        fontFamily: 'Orbitron, sans-serif'
      }
    },
    series: [
      {
        name: '利用率',
        type: 'pie',
        radius: ['10%', '40%'], // 调整饼图大小
        center: ['50%', '60%'], // 调整图表相对位置
        data: [
          { value: props.data.utilizationRate.cpu, name: `CPU (${props.data.utilizationRate.cpu}%)` },
          { value: props.data.utilizationRate.memory, name: `内存 (${props.data.utilizationRate.memory}%)` },
          { value: props.data.utilizationRate.storage, name: `存储 (${props.data.utilizationRate.storage}%)` },
          { value: props.data.utilizationRate.network, name: `网络 (${props.data.utilizationRate.network}%)` }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          normal: {
            color: function (params) {
              const colorList = ['#00d1ff', '#3e82f7', '#04befe', '#89e6ff'];
              return colorList[params.dataIndex];
            }
          }
        },
        label: {
          color: '#fff',
          formatter: '{b}',
          textStyle: {
            fontSize: 15,
            fontFamily: 'Orbitron, sans-serif'
          }
        }
      }
    ]
  };
  option && myChart.setOption(option);
};

watch(() => props.data, (newVal) => {
  if (newVal && newVal.utilizationRate) {
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
  height: 300px;
}
</style>
