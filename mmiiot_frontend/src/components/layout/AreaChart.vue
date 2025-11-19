<template>
  <div id="AreaChart" style="width: 100%;height: 24%"></div>
</template>

<script setup>
import {ref, onMounted} from "vue";
import * as echarts from 'echarts';

// 动态生成算力变化数据
const generateComputeData = () => {
  let data = [];
  let baseValue = 300;
  let trend = 0.5; // 添加一个缓慢上升的趋势
  for (let i = 0; i < 30; i++) {
    let noise = Math.random() * 10 - 5; // 减少随机波动幅度
    let newValue = baseValue + trend + noise; // 正弦函数的周期性变化+趋势变化+随机波动
    if (newValue < 0) newValue = 0; // 确保数据为非负数
    data.push(newValue);
    baseValue = newValue; // 更新基准值为当前值，形成连续性
  }
  return data;
};

let ydata = generateComputeData();

// 基于准备好的dom，初始化echarts实例
onMounted(() => {
  var myChart = echarts.init(document.getElementById('AreaChart'));
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: 'rgba(0,0,0,0.7)',
        },
        lineStyle: {
          color: 'rgb(126,199,255)',
        },
      },
    },
    dataZoom: [
      {
        xAxisIndex: 0,
        show: false,
        type: "slider",
        startValue: 0,
        endValue: 4,
      },
    ],
    grid: {
      top: '20%',
      left: '15%',
      right: '5%',
      bottom: '15%',
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        axisLine: {
          show: true,
          lineStyle: {
            color: 'rgba(3,246,246,1)',
            width: 2
          },
        },
        axisLabel: {
          textStyle: {
            color: 'rgba(3,246,246,1)',
            fontSize: 14,
          },
        },
        splitLine: {
          show: false,
        },
        axisTick: {
          show: true,
        },
        data: Array.from({length: ydata.length}, (_, i) => `Time ${i + 1}`),
      },
    ],
    yAxis: [
      {
        name: "算力值",
        nameTextStyle: {
          color: "rgba(3,246,246,1)",
          fontSize: 16,
          fontWeight: 'bolder',
          padding: [0, 0, 0, 0]
        },
        type: 'value',
        min: 0, // 确保最小值为非负数
        splitLine: {
          show: true,
          lineStyle: {
            color: 'rgba(3,246,88,0.45)',
            type: 'dashed',
          },
        },
        axisLine: {
          show: true,
          lineStyle: {
            color: 'rgba(3,246,88,0.5)',
            width: 2,
          },
        },
        axisLabel: {
          show: true,
          textStyle: {
            color: 'rgb(2,255,62)',
            fontSize: 14
          }
        },
        axisTick: {
          show: false,
        },
      },
    ],
    series: [
      {
        name: '算力计算',
        type: 'line',
        showSymbol: false,
        symbol: 'circle',
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#06ED8DFF',
          shadowColor: 'rgba(0, 255, 255, 0.5)',
          shadowBlur: 10,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(2,255,62, 0.8)',
              },
              {
                offset: 0.4,
                color: 'rgba(2,241,221, 0.5)',
              },
              {
                offset: 0.8,
                color: 'rgba(2,241,221, 0.3)',
              },
              {
                offset: 1,
                color: 'rgba(3,246,246, 0.1)',
              },
            ],
            global: false,
          },
        },
        data: ydata,
      }
    ]
  };

  myChart.setOption(option);

  setInterval(function () {
    let noise = Math.random() * 10 - 5; // 减少随机波动幅度
    let newData = ydata[ydata.length - 1] + 0.5 + noise; // 去除正弦函数的周期性变化
    if (newData < 0) newData = 0; // 确保数据为非负数
    ydata.shift();
    ydata.push(newData);

    option.series[0].data = ydata;
    option.xAxis[0].data = Array.from({length: ydata.length}, (_, i) => `Time ${i + 1}`);
    myChart.setOption(option);
  }, 500); // 每500毫秒刷新一次数据
});
</script>


<style scoped>
#AreaChart {
  margin: 20px 0;
  background: linear-gradient(145deg, rgba(0, 0, 30, 0.9), rgba(0, 50, 100, 0.8));
  border: 2px solid #00ffcc;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), inset 0 0 10px rgba(0, 255, 204, 0.3);
  position: relative;
  overflow: hidden;
  animation: glowing 2s infinite;
}

#AreaChart::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: rgba(3, 246, 197, 0.2);
  border-radius: 15px;
  transform: translate(-50%, -50%);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    width: 100%;
    height: 100%;
    opacity: 0;
  }
  50% {
    width: 100%;
    height: 100%;
    opacity: 0.4;
  }
  100% {
    width: 100%;
    height: 100%;
    opacity: 0;
  }
}

@keyframes glowing {
  0% {
    box-shadow: 0 0 10px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 234, 255, 0.7), 0 0 30px rgba(0, 255, 204, 0.5);
  }
  100% {
    box-shadow: 0 0 10px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
  }
}
</style>
