<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { user, isAuthenticated, logout } = useAuth()

const showUserMenu = ref(false)
const menuRef = ref(null)

const adminBaseURL = import.meta.env.VITE_ADMIN_BASE_URL || 'http://localhost:10062'

const menuItems = [
  { label: '首页', route: { name: 'home' } },
  { label: '模态互联', route: { name: 'modal-connectivity' } },
  { label: '内生安全', route: { name: 'security' } },
  { label: '融合调度', route: { name: 'scheduling' } },
  { label: '后台管理', external: adminBaseURL },
]

const activeName = computed(() => route.name)

const navigateTo = (item) => {
  if (item.external) {
    window.open(item.external, '_blank', 'noopener')
  } else if (item.route) {
    router.push(item.route)
  }
}

const isActive = (item) => {
  if (!activeName.value) {
    return false
  }

  if (item.external) {
    return false
  }

  return activeName.value === item.route.name
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleEditProfile = () => {
  showUserMenu.value = false
  router.push({ name: 'profile' })
}

const handleLogout = () => {
  showUserMenu.value = false
  logout()
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 获取用户头像显示文字（用户名首字母）
const avatarText = computed(() => {
  if (!user.value || !user.value.username) return 'U'
  return user.value.username.charAt(0).toUpperCase()
})
</script>

<template>
  <header class="navbar">
    <div class="brand">
      <span class="brand-mark">PLM</span>
      <div class="brand-label">
        <strong>联想产品生命周期管理</strong>
        <small>Lenovo Product Lifecycle Management</small>
      </div>
    </div>

    <nav class="menu">
      <button v-for="item in menuItems" :key="item.label" :class="['menu-item', { active: isActive(item) }]" @click="navigateTo(item)">
        {{ item.label }}
      </button>
    </nav>

    <div class="actions">
      <button v-if="!isAuthenticated" class="login-btn" @click="router.push({ name: 'login' })">登录</button>
      <div v-else class="user-menu-wrapper" ref="menuRef">
        <button class="user-avatar" @click="toggleUserMenu">
          <span>{{ avatarText }}</span>
        </button>
        <div v-if="showUserMenu" class="user-menu">
          <div class="user-info">
            <div class="user-name">{{ user?.username }}</div>
            <div class="user-email">{{ user?.email }}</div>
          </div>
          <div class="menu-divider"></div>
          <button class="menu-item" @click="handleEditProfile">
            <span>编辑个人信息</span>
          </button>
          <button class="menu-item logout" @click="handleLogout">
            <span>登出</span>
          </button>
        </div>
      </div>
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

.user-menu-wrapper {
  position: relative;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(128, 214, 255, 0.5);
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  color: #0b2338;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.user-avatar:hover {
  border-color: #49c5ff;
  box-shadow: 0 0 12px rgba(73, 197, 255, 0.4);
  transform: scale(1.05);
}

.user-menu {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  min-width: 240px;
  background: linear-gradient(135deg, rgba(11, 38, 66, 0.95), rgba(6, 25, 44, 0.98));
  border: 1px solid rgba(88, 178, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  z-index: 1000;
}

.user-info {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(128, 214, 255, 0.1);
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #e6f1ff;
  margin-bottom: 4px;
}

.user-email {
  font-size: 13px;
  color: rgba(214, 232, 255, 0.7);
}

.menu-divider {
  height: 1px;
  background: rgba(128, 214, 255, 0.1);
  margin: 8px 0;
}

.user-menu .menu-item {
  width: 100%;
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: #d6ecff;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
}

.user-menu .menu-item:hover {
  background: rgba(73, 197, 255, 0.15);
  color: #49c5ff;
}

.user-menu .menu-item.logout {
  color: #ff9a9e;
}

.user-menu .menu-item.logout:hover {
  background: rgba(255, 154, 158, 0.15);
  color: #ff9a9e;
}
</style>

