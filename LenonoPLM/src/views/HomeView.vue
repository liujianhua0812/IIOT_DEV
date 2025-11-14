<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MetricsGrid from '../components/home/MetricsGrid.vue'
import DeploymentMap from '../components/home/DeploymentMap.vue'
import { fetchHomeDeployments, fetchHomeOverview } from '../services/api'

const router = useRouter()

const metrics = ref({})
const deployments = ref([])
const loading = ref(true)
const errorMessage = ref('')

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const [overviewResponse, deploymentsResponse] = await Promise.all([
      fetchHomeOverview(),
      fetchHomeDeployments(),
    ])

    metrics.value = overviewResponse.data
    deployments.value = deploymentsResponse.data.deployments || []
  } catch (error) {
    errorMessage.value = '数据加载出现波动，请稍后重试。'
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="home-view">
    <section class="hero">
      <div class="hero-content">
        <h1>构建可信、敏捷的多模态工业互联</h1>
        <p>
          聚焦多模态感知、内生安全与智能调度，打造一体化的工业互联网中枢。实时掌握设备态势，跨模态协同运行，赋能产业数字化升级。
        </p>
        <div class="hero-actions">
          <button class="primary" @click="router.push({ name: 'login' })">立即登录</button>
          <button class="secondary">查看方案白皮书</button>
        </div>
      </div>
      <div class="hero-visual">
        <div class="pulse"></div>
        <div class="orb"></div>
        <div class="grid"></div>
      </div>
    </section>

    <MetricsGrid :metrics="metrics" />

    <section v-if="loading" class="loading">数据加载中...</section>
    <section v-else-if="errorMessage" class="error">{{ errorMessage }}</section>
    <DeploymentMap v-else :deployments="deployments" />
  </div>
</template>

<style scoped>
.home-view {
  padding: 32px 64px 64px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(5, 26, 43, 0.95), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 48px;
  padding: 42px 48px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.85), rgba(6, 25, 44, 0.9));
  border-radius: 24px;
  border: 1px solid rgba(88, 178, 255, 0.08);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.32);
}

.hero-content h1 {
  font-size: 36px;
  margin-bottom: 18px;
  letter-spacing: 1.6px;
}

.hero-content p {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(214, 232, 255, 0.78);
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-actions .primary,
.hero-actions .secondary {
  padding: 12px 28px;
  border-radius: 999px;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hero-actions .primary {
  border: none;
  color: #0b2338;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  box-shadow: 0 16px 32px rgba(73, 197, 255, 0.25);
}

.hero-actions .primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 38px rgba(73, 197, 255, 0.35);
}

.hero-actions .secondary {
  background: transparent;
  color: #80d6ff;
  border: 1px solid rgba(128, 214, 255, 0.36);
}

.hero-actions .secondary:hover {
  background: rgba(128, 214, 255, 0.18);
}

.hero-visual {
  position: relative;
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-visual .grid {
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  border: 1px solid rgba(128, 214, 255, 0.18);
  background-image: radial-gradient(circle, rgba(128, 214, 255, 0.15) 1px, transparent 1px);
  background-size: 12px 12px;
}

.hero-visual .orb {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(73, 197, 255, 0.65), rgba(11, 38, 66, 0));
  filter: blur(2px);
  animation: orbit 12s linear infinite;
}

.hero-visual .pulse {
  position: relative;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(41, 131, 251, 0.8), rgba(6, 25, 44, 0.1));
  box-shadow: 0 0 30px rgba(41, 131, 251, 0.6);
  animation: pulse 3.5s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}

@keyframes orbit {
  0% {
    transform: rotate(0deg) translateX(40px) rotate(0deg);
  }
  100% {
    transform: rotate(360deg) translateX(40px) rotate(-360deg);
  }
}

.loading,
.error {
  padding: 18px 24px;
  border-radius: 12px;
  background: rgba(7, 27, 44, 0.8);
  border: 1px solid rgba(88, 178, 255, 0.12);
  font-size: 15px;
  letter-spacing: 0.8px;
}

.error {
  color: #ff9a9e;
}
</style>

