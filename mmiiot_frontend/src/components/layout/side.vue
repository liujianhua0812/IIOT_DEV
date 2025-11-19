<template>
  <div class="card-side">
    <titleCard :title="'算力资源池排名'" />
    <div class="track">总算力数量<span id="number">1754</span>台</div>
    <BarsChart />
    <titleCard :title="'算力类型占比'" />
    <ComputeType />
    <titleCard :title="'算力变化趋势'" />
    <AreaChart />
  </div>
</template>

<script setup >
import { ref, onMounted } from "vue";
import AreaChart from '../../components/layout/AreaChart.vue'
import titleCard from '../../components/layout/title.vue'
import ComputeType from "@/components/layout/ComputeType.vue";
import BarsChart from "@/components/layout/BarsChart.vue";

onMounted(() => {
  const numberElement = document.getElementById('number');
  const number = parseInt(numberElement.textContent, 10);
  numberElement.textContent = number.toLocaleString();
})

</script>

<style>
.card-side {
  height: 100%;
  width: 30vw;
  background: linear-gradient(135deg, rgba(0, 8, 24, 0.9), rgba(3, 27, 78, 0.8));
  padding: 5px 20px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 10px rgba(0, 255, 204, 0.3);
  overflow: hidden;
  position: relative;
  animation: glow 3s infinite alternate;
}

@keyframes glow {
  0% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), 0 0 10px rgba(0, 255, 204, 0.3); }
  100% { box-shadow: 0 0 30px rgba(0, 255, 204, 0.8), 0 0 15px rgba(0, 255, 204, 0.5); }
}

.card-side::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(0, 255, 204, 0.2), rgba(0, 8, 24, 0) 70%);
  animation: rotate 6s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.track {
  margin: 0 20px;
  color: #08f5d1;
  font-family: 华文楷体, serif;
  font-size: 18px;
  text-shadow: 0 0 10px rgba(8, 245, 209, 0.5);
  display: flex;
  align-items: center;
  animation: trackGlow 2s infinite alternate;
}

@keyframes trackGlow {
  0% { text-shadow: 0 0 10px rgba(8, 245, 209, 0.5); }
  100% { text-shadow: 0 0 20px rgba(8, 245, 209, 1); }
}

#number {
  color: #369bc1;
  font-weight: 700;
  font-family: DS-Digital, serif;
  font-size: 30px;
  margin: 0 15px;
  font-style: italic;
  text-shadow: 0 0 10px rgba(54, 155, 193, 0.5);
  animation: blink 1s infinite alternate;
}

@keyframes blink {
  0% { text-shadow: 0 0 10px rgba(54, 155, 193, 0.5); }
  100% { text-shadow: 0 0 20px rgba(54, 155, 193, 1); }
}

/* 粒子效果 */
.card-side::after {
  content: '';
  position: absolute;
  left: 0;
  width: 80vw;
  height: 100%;
  pointer-events: none;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><rect width="100%" height="100%" fill="transparent"/><circle cx="10%" cy="20%" r="1" fill="rgba(0,255,204,0.6)" /><circle cx="50%" cy="50%" r="2" fill="rgba(0,255,204,0.6)" /><circle cx="90%" cy="80%" r="1" fill="rgba(0,255,204,0.6)" /><circle cx="30%" cy="70%" r="1" fill="rgba(0,255,204,0.6)" /></svg>');
  animation: particles 6s linear infinite;
}

@keyframes particles {
  0% { background-position: 0 0; }
  100% { background-position: 100% 100%; }
}
</style>
