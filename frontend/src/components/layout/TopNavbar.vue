<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuItems = [
  { label: '首页', route: { name: 'home' } },
  { label: '模态互联', route: { name: 'modal-connectivity' } },
  { label: '内生安全', route: { name: 'security' } },
  { label: '融合调度', route: { name: 'scheduling' } },
  { label: '联想应用示范', route: { name: 'demo-lianxiang' } },
  { label: '泰豪应用示范', route: { name: 'demo-taihao' } },
  { label: '后台管理', route: { name: 'admin-devices' }, isGroup: true },
]

const activeName = computed(() => route.name)

const navigateTo = (item) => {
  router.push(item.route)
}

const isActive = (item) => {
  if (!activeName.value) {
    return false
  }

  if (item.isGroup) {
    return activeName.value.toString().startsWith('admin-')
  }

  return activeName.value === item.route.name
}
</script>

<template>
  <header class="navbar">
    <div class="brand">
      <span class="brand-mark">MMI</span>
      <div class="brand-label">
        <strong>多模态网络工业互联网平台</strong>
        <small>Multi-Modal Industrial IoT Platform</small>
      </div>
    </div>

    <nav class="menu">
      <button v-for="item in menuItems" :key="item.label" :class="['menu-item', { active: isActive(item) }]" @click="navigateTo(item)">
        {{ item.label }}
      </button>
    </nav>

    <div class="actions">
      <button class="login-btn">登录</button>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  height: 80px;
  background: linear-gradient(135deg, #071b2c, #0a2d4a);
  color: #e6f1ff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.24);
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #0a1d2f;
  background: linear-gradient(145deg, #49c5ff, #36a3f7);
  box-shadow: 0 12px 24px rgba(54, 163, 247, 0.35);
}

.brand-label {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-label strong {
  font-size: 18px;
  letter-spacing: 1px;
}

.brand-label small {
  font-size: 12px;
  opacity: 0.72;
  letter-spacing: 0.5px;
}

.menu {
  display: flex;
  gap: 12px;
  align-items: center;
}

.menu-item {
  padding: 12px 20px;
  border-radius: 999px;
  border: none;
  background: transparent;
  color: inherit;
  font-size: 15px;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.menu-item:hover {
  background: rgba(73, 197, 255, 0.18);
  color: #80d6ff;
}

.menu-item.active {
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  color: #0b2338;
  box-shadow: 0 8px 18px rgba(73, 197, 255, 0.25);
}

.actions .login-btn {
  padding: 10px 22px;
  border-radius: 8px;
  border: 1px solid rgba(128, 214, 255, 0.5);
  background: rgba(4, 16, 27, 0.4);
  color: #dbefff;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.actions .login-btn:hover {
  background: rgba(128, 214, 255, 0.2);
  box-shadow: 0 6px 16px rgba(128, 214, 255, 0.2);
}
</style>

