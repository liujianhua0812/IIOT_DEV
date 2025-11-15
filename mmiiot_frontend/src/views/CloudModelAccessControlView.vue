<template>
  <div class="page-shell">
    <div class="container">
      <aside class="sidebar">
        <div class="system-header">
          <div class="system-title">细粒度访问控制系统</div>
        </div>

        <div 
          v-for="item in accessControlItems" 
          :key="item.name"
          class="device-category"
          :class="{ active: currentAccessControlType === item.name }"
          @click="navigateToAccessControl(item.name)"
        >
          <span class="category-icon">{{ item.icon }}</span> {{ item.name }}
        </div>
      </aside>

      <main class="main-content">
        <div class="content-placeholder">
          <h1>云侧模型访问控制</h1>
          <p>此功能正在开发中...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'CloudModelAccessControlView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const accessControlItems = [
      { name: '端侧模型访问控制', route: 'edge-model-access-control', icon: '⚙️' },
      { name: '云侧模型访问控制', route: 'cloud-model-access-control', icon: '☁️' },
      { name: '云上数据访问控制', route: 'cloud-data-access-control', icon: '💾' },
      { name: '链上数据访问控制', route: 'chain-data-access-control', icon: '⛓️' },
      { name: '视频数据访问控制', route: 'video-data-access-control', icon: '🎥' }
    ]
    
    const currentAccessControlType = ref('云侧模型访问控制')
    
    const navigateToAccessControl = (name) => {
      currentAccessControlType.value = name
      const item = accessControlItems.find(item => item.name === name)
      if (item && route.name !== item.route) {
        router.push({ name: item.route })
      }
    }

    return {
      accessControlItems,
      currentAccessControlType,
      navigateToAccessControl
    }
  }
}
</script>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(4, 21, 38, 0.96), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.container {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 200px);
}

.sidebar {
  width: 360px;
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.system-header {
  text-align: center;
  margin-bottom: 12px;
}

.system-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin-bottom: 6px;
}

.device-category {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  border-bottom: 1px solid rgba(88, 178, 255, 0.12);
  font-size: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 18px;
  line-height: 1;
}

.device-category:hover {
  background: rgba(128, 214, 255, 0.1);
}

.device-category.active {
  background: rgba(88, 178, 255, 0.2);
  border-color: rgba(88, 178, 255, 0.35);
  font-weight: 700;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-placeholder {
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 48px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.content-placeholder h1 {
  font-size: 32px;
  color: #e6f1ff;
  margin-bottom: 16px;
}

.content-placeholder p {
  font-size: 18px;
  color: rgba(214, 232, 255, 0.75);
}

@media (max-width: 1100px) {
  .main-content {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
  }
}
</style>

