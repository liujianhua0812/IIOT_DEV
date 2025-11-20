<template>
  <div class="modal" :class="{ 'is-active': isActive }">
    <div class="modal-content">
      <span class="close" @click="closeModal">&times;</span>
      <div class="modal-body">
        <div class="modal-left">
          <h1 class="modal-title">{{ data.name }} 算力调度中心</h1>
          <p><strong>数值:</strong> {{ data.value }}</p>
          <p><strong>CPU 核心数:</strong> {{ data.cpuCores }}</p>
          <p><strong>内存容量:</strong> {{ data.memoryCapacity }} GB</p>
          <p><strong>存储容量:</strong> {{ data.storageCapacity }} TB</p>
          <p><strong>网络带宽:</strong> {{ data.networkBandwidth }} Gbps</p>
          <p><strong>任务队列长度:</strong> {{ data.taskQueueLength }}</p>
          <p><strong>平均任务完成时间:</strong> {{ data.averageTaskCompletionTime }} minutes</p>

          <!-- 左侧的图表 -->
          <div class="chart-item">
            <LevelPieChart :data="data"/>
          </div>

          <div class="flylines-container">
            <div ref="mapContainer" class="map-container"></div>
            <div class="labels-container">
              <div class="label">
                <span class="label-title">当前调度状态:</span>
                <span class="label-value" :class="statusColor">{{ dispatchStatus }}</span>
              </div>
              <div class="label">
                <span class="label-title">目标调度能力:</span>
                <span class="label-value">{{ targetDispatchCapacity }}%</span>
              </div>
              <div class="label">
                <span class="label-title">当前能力:</span>
                <span :class="['label-value', statusColor]">{{ (currentDispatchCapacity * 100).toFixed(2) }}%</span>
              </div>
            </div>
          </div>

        </div>

        <div class="modal-center">
          <!-- 引用新的地图组件 -->
          <MapComponent :lng="data.lng" :lat="data.lat"/>
        </div>


        <div class="modal-right">
          <div class="utilization-rates">
            <h3>资源利用率</h3>
            <p><strong>CPU:</strong> {{ data.utilizationRate.cpu }}%</p>
            <p><strong>内存:</strong> {{ data.utilizationRate.memory }}%</p>
            <p><strong>存储:</strong> {{ data.utilizationRate.storage }}%</p>
            <p><strong>网络:</strong> {{ data.utilizationRate.network }}%</p>
          </div>

          <!-- 右侧的图表 -->
          <div class="chart-item">
            <LevelBarChart :data="data"/>
          </div>
          <!--          <div class="chart-item">-->
          <!--            <LevelLineChart :data="data" />-->
          <!--          </div>-->
          <p class="region-info"><strong>区域:</strong> {{ data.areas.join(", ") }}</p>
        </div>
      </div>

      <div class="button-container">
        <button @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, watch, ref} from 'vue';
import LevelPieChart from "./LevelPieChart.vue";
import LevelBarChart from './LevelBarChart.vue';
import LevelLineChart from "./LevelLineChart.vue";
import MapComponent from "./MapComponent.vue";

const mapContainer = ref(null);
const currentDispatchCapacity = ref(Math.random());
const targetDispatchCapacity = ref(95); // 目标调度能力，百分比表示
const dispatchStatus = ref('');
const statusColor = ref('');
const emit = defineEmits(['close']);
const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    required: true
  }
});
const { data, isActive } = props;
const closeModal = () => {
  console.log('Close event is emitted');
  emit('close');
};

const updateStatus = () => {
  const diff = Math.abs(currentDispatchCapacity.value * 100 - targetDispatchCapacity.value);
  if (diff < 5) {
    dispatchStatus.value = '正常';
    statusColor.value = 'status-normal';
  } else if (diff < 20) {
    dispatchStatus.value = '警告';
    statusColor.value = 'status-warning';
  } else {
    dispatchStatus.value = '危险';
    statusColor.value = 'status-danger';
  }
};

onMounted(() => {
  updateStatus();

// 每隔2秒随机改变调度能力，并更新状态
  setInterval(() => {
    currentDispatchCapacity.value = Math.random(); // 模拟调度能力变化
    updateStatus();
  }, 2000);
});

watch(currentDispatchCapacity, updateStatus);
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap');

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow-y: hidden;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  z-index: 10;
  animation: starry 100s linear infinite;
  background-size: cover;
}

@keyframes starry {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 10000px 10000px;
  }
}

.modal-content {
  background: linear-gradient(135deg, #001f3f, #005f99, #007acc);
  margin: auto;
  padding: 20px;
  width: 90%;
  max-width: 90vw;
  height: 92vh;
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2), 0 6px 20px rgba(0, 0, 0, 0.19);
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  position: relative;
  animation: modalShow 0.5s ease-out, pulse 2s infinite;
}

@keyframes modalShow {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 15px rgba(0, 191, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 25px rgba(0, 191, 255, 0.7);
  }
  100% {
    box-shadow: 0 0 15px rgba(0, 191, 255, 0.5);
  }
}

.modal-body {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  height: 80vh;
}

.modal-left,
.modal-right {
  flex: 1;
  height: 89vh;
  padding: 10px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  margin: 0 10px;
}

.chart-item {
  margin-top: 10px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-center {
  flex: 2;
  margin: 0 10px;
  border-radius: 10px;
}

.utilization-rates {
  background: rgba(0, 0, 0, 0.6); /* 增加背景透明度，使内容更突出 */
  padding: 20px; /* 增加内边距，提升舒适度 */
  border-radius: 8px; /* 圆角样式，柔化外观 */
  margin-top: 20px; /* 增加与上方元素的间距 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2), inset 0 0 10px rgba(0, 0, 0, 0.3); /* 添加外部阴影和内部阴影，增强立体感 */
  border: 1px solid rgba(255, 255, 255, 0.2); /* 轻微边框，增强分割效果 */
}

.utilization-rates h3 {
  color: #00ffff; /* 亮蓝色标题，增强对比度 */
  margin-bottom: 15px; /* 增加标题与内容的间距 */
  text-align: center; /* 居中对齐 */
  font-size: 20px; /* 增大字体，增加强调 */
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.5); /* 增加轻微的文本阴影 */
  font-weight: bold; /* 加粗标题 */
}

.utilization-rates p {
  margin: 10px 0; /* 增加每项之间的间距 */
  font-size: 16px; /* 增加字体大小，提升可读性 */
  display: flex; /* 使用flex布局 */
  align-items: center; /* 图标和文本垂直居中 */
}

.utilization-rates p strong {
  color: #00e0ff; /* 强调文本颜色 */
  font-weight: bold; /* 加粗 */
  margin-right: 10px; /* 增加强调文本与具体值的间距 */
}

.utilization-rates p:before {
  content: ''; /* 占位符，确保每项前都有一个图标 */
  display: inline-block;
  width: 10px;
  height: 10px;
  background-color: #00e0ff; /* 默认图标颜色 */
  border-radius: 50%;
  margin-right: 8px; /* 图标与文本间距 */
}

.utilization-rates p:nth-child(2):before {
  background-color: #4dff4d; /* CPU 图标颜色 */
}

.utilization-rates p:nth-child(3):before {
  background-color: #ffa64d; /* 内存 图标颜色 */
}

.utilization-rates p:nth-child(4):before {
  background-color: #ff4d4d; /* 存储 图标颜色 */
}

.utilization-rates p:nth-child(5):before {
  background-color: #4d79ff; /* 网络 图标颜色 */
}


.region-info {
  margin-top: 30px; /* 上边距，确保与上方元素有适当间距 */
  padding: 5px 5px; /* 内边距，增大文字与边框的间距，提升阅读体验 */
  background: rgba(0, 0, 0, 0.5); /* 背景透明度稍微增加，使文本更加突出 */
  border-radius: 12px; /* 圆角略微加大，使得整体外观更柔和 */
  font-size: 15px; /* 字体大小保持18px，适合阅读 */
  color: #00e0ff; /* 字体颜色稍微亮一些，增强对比度 */
  text-align: center; /* 文本居中对齐，保持视觉平衡 */
  text-shadow: 0 0 8px #00e0ff, 0 0 12px rgba(0, 224, 255, 0.5); /* 增加层次感的阴影效果，突出文本 */
  border: 1px solid rgba(0, 224, 255, 0.5); /* 增加轻微的边框，定义区域边界 */
  box-shadow: 0 0 15px rgba(0, 224, 255, 0.3), inset 0 0 10px rgba(0, 224, 255, 0.2); /* 增加内外阴影，提升立体感 */
  transition: transform 0.3s ease, box-shadow 0.3s ease; /* 增加悬停效果的过渡动画 */
}

.region-info:hover {
  transform: scale(1.05); /* 悬停时轻微放大，增加交互感 */
  box-shadow: 0 0 25px rgba(0, 224, 255, 0.5), inset 0 0 15px rgba(0, 224, 255, 0.3); /* 悬停时阴影效果更明显 */
}

.button-container {
  z-index: 100;
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
  position: absolute;
  right: 20px;
  top: 20px;
  transition: color 0.3s ease;
  z-index: 10;
}

.close:hover,
.close:focus {
  color: #fff;
}

.modal-title {
  font-size: 23px;
  color: #00ccff; /* 使用亮青色，突出标题 */
  text-align: center; /* 居中对齐 */
  margin-bottom: 10px;
  font-weight: bold;
  text-transform: uppercase; /* 大写字母，增加力量感 */
  letter-spacing: 2px; /* 增大字母间距，增强未来感 */
  text-shadow: 0 0 10px #00ccff, 0 0 20px rgba(0, 204, 255, 0.7); /* 发光效果 */
  animation: pulse 2s infinite alternate; /* 轻微的脉动效果 */
}

@keyframes pulse {
  from {
    text-shadow: 0 0 10px #00ccff, 0 0 20px rgba(0, 204, 255, 0.7);
  }
  to {
    text-shadow: 0 0 20px #00ccff, 0 0 30px rgba(0, 204, 255, 1);
  }
}

.modal-content p {
  font-size: 18px;
  color: #eeeeee; /* 使用浅灰色，使内容在深色背景上清晰 */
  margin: 5px 0;
  padding: 5px;
  background: linear-gradient(135deg, rgba(0, 34, 64, 0.8), rgba(0, 64, 128, 0.8)); /* 深蓝色渐变背景 */
  border-radius: 10px;
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3), 0 0 30px rgba(0, 204, 255, 0.2); /* 发光边框 */
  display: flex;
  align-items: center;
}

.modal-content p strong {
  color: #00ccff; /* 强调文本使用亮青色 */
  font-size: 15px;
  font-weight: bold;
  margin: 0;
}

.modal-content p:before {
  content: ''; /* 占位符，确保每项前都有一个图标 */
  display: inline-block;
  width: 10px;
  height: 10px;
  background-color: #00ccff; /* 使用亮青色图标 */
  border-radius: 50%;
  margin-right: 12px; /* 图标与文本间距 */
  box-shadow: 0 0 10px #00ccff, 0 0 20px rgba(0, 204, 255, 0.7); /* 图标发光效果 */
}

.modal-content p:hover {
  background: linear-gradient(135deg, rgba(0, 64, 128, 0.8), rgba(0, 34, 64, 0.8)); /* 悬停时背景渐变反转 */
  color: #ffffff; /* 悬停时文字颜色加亮 */
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.5), 0 0 40px rgba(0, 204, 255, 0.4); /* 增强悬停时的发光效果 */
}

.modal-content p {
  font-size: 16px; /* 增大字体，提升可读性 */
  color: #ffffff; /* 白色文本，保持与整体风格一致 */
  margin: 10px 0; /* 调整段落之间的间距 */
  display: flex; /* 使用 flex 布局，使图标与文本居中对齐 */
  align-items: center;
}

.modal-content p strong {
  color: #00ffcc; /* 强调文本的颜色 */
  margin-right: 10px; /* 强调文本与后续内容之间的间距 */
  min-width: 120px; /* 设置最小宽度，使得内容对齐 */
  display: inline-block; /* 强制使强内容为块状元素 */
}

.modal-content p:before {
  content: ''; /* 占位符，确保每项前都有一个图标 */
  display: inline-block;
  width: 10px;
  height: 10px;
  background-color: #00e0ff; /* 默认图标颜色 */
  border-radius: 50%;
  margin-right: 10px; /* 图标与文本间距 */
  transition: background-color 0.3s ease; /* 添加颜色渐变效果 */
}

.modal-content p:nth-child(2):before {
  background-color: #4dff4d; /* 数值 图标颜色 */
}

.modal-content p:nth-child(3):before {
  background-color: #ffa64d; /* CPU核心数 图标颜色 */
}

.modal-content p:nth-child(4):before {
  background-color: #ff4d4d; /* 内存容量 图标颜色 */
}

.modal-content p:nth-child(5):before {
  background-color: #4d79ff; /* 存储容量 图标颜色 */
}

.modal-content p:nth-child(6):before {
  background-color: #ffcc00; /* 网络带宽 图标颜色 */
}

.modal-content p:nth-child(7):before {
  background-color: #ff66cc; /* 任务队列长度 图标颜色 */
}

.modal-content p:nth-child(8):before {
  background-color: #00ffcc; /* 平均任务完成时间 图标颜色 */
}

.modal-content p:hover:before {
  background-color: #00ff99; /* 悬停时图标颜色变化 */
}

.modal-content button {
  padding: 10px 12px;
  background: linear-gradient(145deg, #ff6a00, #ee0979);
  color: #fff;
  font-weight: bolder;
  border: none;
  width: 40%;
  border-radius: 5px;
  box-shadow: 0 4px 10px rgba(255, 106, 0, 0.7), 0 2px 4px rgba(255, 106, 0, 0.5), 0 0 10px rgba(255, 0, 102, 0.5);
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
  font-size: 16px;
  align-self: center;
  animation: neon-button 1.5s infinite alternate;
}

@keyframes neon-button {
  from {
    box-shadow: 0 4px 10px rgba(255, 106, 0, 0.7), 0 2px 4px rgba(255, 106, 0, 0.5), 0 0 10px rgba(255, 0, 102, 0.5);
  }
  to {
    box-shadow: 0 4px 20px rgba(255, 106, 0, 1), 0 2px 10px rgba(255, 106, 0, 1), 0 0 20px rgba(255, 0, 102, 1);
  }
}


.flylines-container {
  width: 100%;
  height: 25vh;
  flex-direction: column;
  align-items: center;
  display: flex;
  justify-content: center;
  background: transparent;
  bottom: 50px;
}

.labels-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: -35px;
}

.label {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.label-title {
  font-size: 15px;
  color: rgb(8, 237, 237);
  margin-bottom: 5px;
}

.label-value {
  font-size: 21px;
  font-weight: bold;
  color: rgb(8, 237, 237);
  font-family: DS-Digital, serif;
}

.status-normal {
  color: #4dff4d;
}

.status-warning {
  color: #ffa64d;
}

.status-danger {
  color: #ff4d4d;
}
</style>
