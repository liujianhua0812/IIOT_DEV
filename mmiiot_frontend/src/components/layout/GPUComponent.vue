<!-- GPUComponent.vue -->
<template>
  <div class="module-container">
    <div id="gpu-chart" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { onMounted } from 'vue';

export default {
  name: 'GPUComponent',
  setup() {
    let chartInstance;
    const dataLength = 10;
    let chartData = {
      labels: [],
      usage: [],
      temperature: [],
      memoryUsage: []
    };

    const initChart = () => {
      const chartDom = document.getElementById('gpu-chart');
      chartInstance = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          borderColor: '#0ff3ae',
          borderWidth: 1,
          textStyle: {
            color: '#0ff3ae'
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(item => {
              result += item.seriesName + ': ' + item.value + (item.seriesName === 'GPU 温度' ? '°C' : '%') + '<br/>';
            });
            return result;
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: chartData.labels,
          axisLine: {
            lineStyle: {
              color: '#0ff3ae'
            }
          },
          axisLabel: {
            color: '#0ff3ae',
            fontSize: 15
          }
        },
        yAxis: [
          {
            type: 'value',
            max: 100,
            min: 0,
            axisLine: {
              lineStyle: {
                color: '#0ff3ae'
              }
            },
            axisLabel: {
              color: '#0ff3ae',
              fontSize: 14,
              formatter: '{value}%'
            },
            splitLine: {
              lineStyle: {
                color: 'rgba(15, 243, 174, 0.2)',
                type: 'dashed',
              }
            }
          },
          {
            type: 'value',
            max: 100,
            min: 0,
            axisLine: {
              lineStyle: {
                color: '#ff3a50'
              }
            },
            axisLabel: {
              color: '#ff3a50',
              fontSize: 14,
              formatter: '{value}°C'
            },
            splitLine: {
              show: false
            }
          }
        ],
        series: [
          {
            name: 'GPU 使用率',
            type: 'line',
            data: chartData.usage,
            areaStyle: {
              color: 'rgba(15, 243, 174, 0.3)'
            },
            lineStyle: {
              color: '#0ff3ae',
              width: 2
            },
            itemStyle: {
              color: '#0ff3ae',
              borderWidth: 2,
              borderColor: '#fff'
            },
            showSymbol: false,
            animationDuration: 2000,
            animationEasing: 'linear',
          },
          {
            name: 'GPU 温度',
            type: 'line',
            data: chartData.temperature,
            yAxisIndex: 1,
            lineStyle: {
              color: '#ff3a50',
              width: 2
            },
            itemStyle: {
              color: '#ff3a50',
              borderWidth: 2,
              borderColor: '#fff'
            },
            showSymbol: false,
            animationDuration: 2000,
            animationEasing: 'linear',
          },
          {
            name: '显存使用率',
            type: 'line',
            data: chartData.memoryUsage,
            areaStyle: {
              color: 'rgba(195, 185, 3, 0.3)'
            },
            lineStyle: {
              color: '#d1df04',
              width: 2
            },
            itemStyle: {
              color: '#eef600',
              borderWidth: 2,
              borderColor: '#fff'
            },
            showSymbol: false,
            animationDuration: 2000,
            animationEasing: 'linear',
          },
        ],
      };

      chartInstance.setOption(option);

      setInterval(() => {
        updateChartData();
        chartInstance.setOption({
          xAxis: {
            data: chartData.labels
          },
          series: [
            {
              data: chartData.usage
            },
            {
              data: chartData.temperature
            },
            {
              data: chartData.memoryUsage
            },
            {
              data: chartData.usage.map((value, index) => [chartData.labels[index], value])
            }
          ]
        });
      }, 5000); // 修改刷新间隔为5秒
    };

    const updateChartData = () => {
      const now = new Date();
      const timeStr = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;

      if (chartData.labels.length >= dataLength) {
        chartData.labels.shift();
        chartData.usage.shift();
        chartData.temperature.shift();
        chartData.memoryUsage.shift();
      }

      chartData.labels.push(timeStr);
      chartData.usage.push(Math.floor(Math.random() * 21) + 50); // 保持在50-70之间
      chartData.temperature.push(Math.floor(Math.random() * 21) + 60); // 保持在60-80之间
      chartData.memoryUsage.push(Math.floor(Math.random() * 21) + 40); // 保持在40-60之间
    };

    onMounted(() => {
      for (let i = 0; i < dataLength; i++) {
        updateChartData();
      }
      initChart();
    });

    return {};
  }
};
</script>

<style scoped>
.module-container {
  top: 3vh;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.chart {
  height: 30vh;
  width: 100%;
  position: absolute;
  margin: 30px 0;
}
</style>
