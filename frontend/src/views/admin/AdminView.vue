<script setup>
import { computed } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuItems = [
  { label: '设备管理', name: 'admin-devices', description: '统一管理工业终端设备资产' },
  { label: '模型管理', name: 'admin-models', description: '模型版本、部署与监控全流程' },
  { label: '任务管理', name: 'admin-tasks', description: '调度任务编排与执行监控' },
]

const activeName = computed(() => route.name)

const navigate = (name) => {
  router.push({ name })
}
</script>

<template>
  <div class="admin-shell">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>后台管理中心</h2>
        <p>运维中枢 · 实时掌控平台运行状态</p>
      </div>

      <nav class="sidebar-menu">
        <button
          v-for="item in menuItems"
          :key="item.name"
          :class="['menu-item', { active: activeName === item.name }]"
          @click="navigate(item.name)"
        >
          <span class="label">{{ item.label }}</span>
          <small>{{ item.description }}</small>
        </button>
      </nav>
    </aside>

    <section class="admin-content">
      <RouterView />
    </section>
  </div>
</template>

<style scoped>
.admin-shell {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
  background: #ffffff;
  color: #303133;
}

.sidebar {
  padding: 32px 24px;
  border-right: 1px solid #e4e7ed;
  background: #ffffff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.sidebar-header {
  padding-bottom: 24px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h2 {
  font-size: 22px;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
  color: #303133;
  font-weight: 600;
}

.sidebar-header p {
  margin: 0;
  color: #909399;
  font-size: 13px;
  line-height: 1.5;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.menu-item {
  padding: 16px 18px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: #f5f7fa;
  color: #606266;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 14px;
}

.menu-item .label {
  font-weight: 500;
  color: #303133;
}

.menu-item small {
  color: #909399;
  font-size: 12px;
  line-height: 1.4;
}

.menu-item:hover {
  background: #ecf5ff;
  border-color: #b3d8ff;
  color: #409eff;
}

.menu-item:hover .label {
  color: #409eff;
}

.menu-item:hover small {
  color: #66b1ff;
}

.menu-item.active {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.menu-item.active .label {
  color: #ffffff;
  font-weight: 600;
}

.menu-item.active small {
  color: rgba(255, 255, 255, 0.85);
}

.admin-content {
  padding: 32px 40px;
  overflow-y: auto;
  background: #f5f7fa;
}
</style>

