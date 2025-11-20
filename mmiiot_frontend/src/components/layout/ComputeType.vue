<template>
  <div class="main-container">
    <div class="module-container" v-if="currentView === 'pies'">
      <div id="pie1" class="pie-chart"></div>
      <div id="pie2" class="pie-chart"></div>
      <div id="pie3" class="pie-chart"></div>
    </div>
    <CPUComponent v-if="currentView === 'cpu'" class="module-container"/>
    <GPUComponent v-if="currentView === 'gpu'" class="module-container"/>
    <StorageComponent v-if="currentView === 'storage'" class="module-container"/>

    <div class="text">
      <button class="sci-fi-button" @click="showView('cpu')">CPU占用</button>
      <button class="sci-fi-button" @click="showView('gpu')">GPU占用</button>
      <button class="sci-fi-button" @click="showView('storage')">存储容量</button>
      <button class="sci-fi-button" @click="showView('pies')">返回总览</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from "vue";
import * as echarts from 'echarts';
import CPUComponent from "./CPUComponent.vue";
import GPUComponent from "./GPUComponent.vue";
import StorageComponent from './StorageComponent.vue';

const currentView = ref('pies');

function showView(view) {
  currentView.value = view;
}

const init = (mychart, value) => {
  const legend = {
    show: false,
  };
  const tooltip = {
    show: false,
  };
  const colors = ['#1d729f', '#05eca7', '#2BDCE3'];
  const innerRingColor = {
    type: 'linear',
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [0, .3, 1].map((offset, index) => ({offset, color: colors[index]})),
    global: false,
  };

  let option = {
    color: colors,
    tooltip: {},
    legend,
    series: [
      {
        name: '',
        type: 'pie',
        center: ['50%', '50%'],
        radius: ['5%', '60%'],
        avoidLabelOverlap: false,
        clockwise: false,
        startAngle: -90,
        label: {
          show: false,
        },
        data: [
          { value: value, name: '完成度', itemStyle: { color: innerRingColor, opacity: .2 } },
        ],
        emphasis: {
          scale: false,
        },
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicInOut',
      },
      {
        name: '',
        type: 'pie',
        center: ['50%', '50%'],
        radius: ['70%', '90%'],
        avoidLabelOverlap: false,
        clockwise: true,
        startAngle: -90,
        label: {
          show: true,
          position: 'center',
          formatter: '{d}%',
          fontSize: 20,
          fontWeight: 'bold',
          colors: '#fff'
        },
        data: [
          { value: value, name: '', itemStyle: { color: innerRingColor, opacity: 1 } },
          { value: 100 - value, name: '', itemStyle: { color: '#fd470f' } },
        ].sort((a, b) => b.value - a.value),
        emphasis: {
          scale: false,
        },
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicOut',
      },
    ],
  };
  mychart.setOption(option);

  setInterval(() => {
    const newValue = Math.floor(Math.random() * 100);
    option.series[1].data[0].value = newValue;
    option.series[1].data[1].value = 100 - newValue;
    mychart.setOption(option);
  }, 2000);
};

// 初始化图表
const initCharts = () => {
  nextTick(() => {
    var pie1 = echarts.init(document.getElementById('pie1'));
    var pie2 = echarts.init(document.getElementById('pie2'));
    var pie3 = echarts.init(document.getElementById('pie3'));

    init(pie1, 78);
    init(pie2, 80);
    init(pie3, 90);

    const pies = document.querySelectorAll('.pie-chart');
    let currentIndex = 0;
    const intervalTime = 2000; // 每个饼图悬停时间
    setInterval(() => {
      pies.forEach((pie, index) => {
        if (index === currentIndex) {
          pie.classList.add('hover');
        } else {
          pie.classList.remove('hover');
        }
      });
      currentIndex = (currentIndex + 1) % pies.length;
    }, intervalTime);
  });
};

onMounted(() => {
  initCharts();
});

// 监听视图变化，重新初始化图表
watch(currentView, (newValue) => {
  if (newValue === 'pies') {
    initCharts();
  }
});
</script>

<style scoped>
.main-container {
  width: 100%;
  height: 30%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: -5%;

}

.module-container {
  width: 100%;
  height: 25%;
  bottom: -5%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pie-chart {
  margin: 0 10px;
  width: 120px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  transform: rotateY(25deg) rotateX(15deg);
  transition: transform 0.5s, box-shadow 0.5s;
  box-shadow: 0 20px 40px rgba(0, 255, 204, 0.5), 0 10px 10px rgba(0, 255, 204, 0.3);
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.6), rgba(2, 14, 29, 0.7));
  border-radius: 10px;
  border: 2px solid #0ae8d5;
  position: relative;
}

.pie-chart::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  box-shadow: inset 0 0 20px rgba(0, 255, 204, 0.6), inset 0 0 30px rgba(0, 255, 204, 0.3);
  pointer-events: none;
}

.pie-chart.hover {
  transform: rotateY(0deg) rotateX(0deg);
  box-shadow: 0 20px 20px rgba(0, 255, 204, 0.7), 0 20px 20px rgba(0, 255, 204, 0.5);
}

.pie-chart:hover {
  transform: rotateY(0deg) rotateX(0deg);
  box-shadow: 0 20px 20px rgba(0, 255, 204, 0.7), 0 20px 20px rgba(0, 255, 204, 0.5);
}
.text {
  z-index: 1;
  align-content: center;
  justify-content: center;
  display: flex;
  text-align: center;
  margin-top: 7vh;
}

.sci-fi-button {
  width: 6vw;
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  color: #00ffcc;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.2), rgba(2, 14, 29, 0.2));
  border: 2px solid #00ffcc;
  border-radius: 15px;
  padding: 10px 5px;
  margin: 0 10px;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
  overflow: hidden;
  transition: color 0.5s, border 0.5s, box-shadow 0.5s, transform 0.5s;
  box-shadow: 0 20px 30px rgba(0, 255, 204, 0.5), 0 10px 6px rgba(0, 255, 204, 0.3);
  animation: glowing 2s infinite;
  bottom: -20px;
}

.sci-fi-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300%;
  height: 100%;
  background: rgba(0, 255, 204, 0.2);
  transition: width 0.4s, height 0.4s, top 0.4s, left 0.4s;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: ripple 1.5s infinite ease-in-out;
}

@keyframes ripple {
  0% {
    width: 0;
    height: 0;
    opacity: 1;
  }
  100% {
    width: 300%;
    height: 300%;
    opacity: 0;
  }
}

.sci-fi-button:hover::before {
  width: 0;
  height: 0;
  top: 50%;
  left: 50%;
}

.sci-fi-button:hover {
  color: #000;
  font-size: 14px;
  background: #00ffcc;
  border: 2px solid #06f6b5;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5), 0 6px 6px rgba(0, 0, 0, 0.3);
  transform: translateY(-5px);
  animation: gradient-shift 3s infinite;
}

.sci-fi-button:active {
  transform: translateY(5px);
  box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
}

@keyframes gradient-shift {
  0% {
    background: linear-gradient(45deg, #0de8c6, #0e9e96);
  }
  50% {
    background: linear-gradient(45deg, #0de8c6, #0e9e96);
  }
  100% {
    background: linear-gradient(45deg, #0de8c6, #0e9e96);
  }
}

@keyframes glowing {
  0% {
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
  }
  50% {
    box-shadow: 0 0 30px rgba(0, 234, 255, 0.7), 0 0 30px rgba(39, 198, 198, 0.5);
  }
  100% {
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 20px rgba(0, 255, 204, 0.3);
  }
}
</style>
