<template>
  <div class="main-layout">
    <el-container class="layout-container">
      <el-aside :width="sidebarWidth" class="sidebar" :style="{ width: sidebarWidth }">
        <div class="logo">
          <h2 v-if="!isCollapse" class="logo-text">后台管理中心</h2>
          <h2 v-else class="logo-text-collapsed">MMI</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="#001529"
          text-color="rgba(255, 255, 255, 0.65)"
          active-text-color="#ffffff"
          router
        >
          <el-menu-item :index="`/${item.name}`" v-for="item in menuItems" :key="item.name">
            <el-icon><component :is="item.iconComponent" /></el-icon>
            <template #title>
              <span>{{ item.label }}</span>
            </template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container class="main-container">
        <el-header class="header">
          <div style="flex: 1; display: flex; align-items: center; justify-content: space-between;">
            <el-button
              :icon="isCollapse ? Expand : Fold"
              @click="isCollapse = !isCollapse"
              text
            />
            <div style="display: flex; align-items: center; gap: 20px;">
              <el-dropdown @command="handleCommand">
                <span style="cursor: pointer; display: flex; align-items: center; gap: 8px;">
                  <el-avatar :size="32">{{ avatarText }}</el-avatar>
                  <span>{{ user?.username || '用户' }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">编辑个人信息</el-dropdown-item>
                    <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <el-main class="content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import {
  Monitor,
  Setting,
  Document,
  Expand,
  Fold,
  ArrowDown,
  Grid
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { user, logout } = useAuth()

const isCollapse = ref(false)

const menuItems = [
  { label: '设备管理', name: 'devices', iconComponent: Monitor },
  { label: '设备类型', name: 'device-types', iconComponent: Grid },
  { label: '模型管理', name: 'models', iconComponent: Setting },
  { label: '任务管理', name: 'tasks', iconComponent: Document },
]

const activeMenu = computed(() => {
  // 使用路由路径，el-menu 的 router 属性会自动匹配
  return route.path || '/devices'
})

const sidebarWidth = computed(() => isCollapse.value ? '64px' : '200px')

const avatarText = computed(() => {
  if (!user.value || !user.value.username) return 'U'
  return user.value.username.charAt(0).toUpperCase()
})

const handleCommand = (command) => {
  if (command === 'logout') {
    logout()
  } else if (command === 'profile') {
    router.push({ name: 'profile' })
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.layout-container {
  height: 100%;
  display: flex;
  flex-direction: row;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* 强制设置侧边栏宽度 */
:deep(.el-aside.sidebar) {
  width: v-bind(sidebarWidth) !important;
  min-width: v-bind(sidebarWidth) !important;
  max-width: v-bind(sidebarWidth) !important;
  transition: width 0.3s, min-width 0.3s, max-width 0.3s;
  flex-shrink: 0;
}

.sidebar {
  background: #001529;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.3s;
  position: relative;
  flex-shrink: 0;
}

.logo {
  border-bottom: 1px solid #1f2937;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logo-text {
  color: #fff;
  padding: 0;
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
  width: 100%;
}

.logo-text-collapsed {
  color: #fff;
  padding: 0;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  text-align: center;
  width: 100%;
  letter-spacing: 1px;
}

/* Element Plus菜单折叠样式优化 */
:deep(.el-menu) {
  border-right: none;
  width: 100%;
}

:deep(.el-menu--collapse) {
  width: 100%;
}

:deep(.el-menu--collapse .el-menu-item),
:deep(.el-menu--collapse .el-sub-menu__title) {
  padding: 0 !important;
  text-align: center;
  justify-content: center;
}

:deep(.el-menu--collapse .el-menu-item .el-icon),
:deep(.el-menu--collapse .el-sub-menu__title .el-icon) {
  margin-right: 0;
  margin-left: 0;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

:deep(.el-menu-item.is-active) {
  background-color: #1890ff !important;
  color: #ffffff !important;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #ffffff !important;
}

:deep(.el-menu-item.is-active span) {
  color: #ffffff !important;
  font-weight: 600;
}

/* 确保活动菜单项的所有文字和图标都是白色 */
:deep(.el-menu-item.is-active *) {
  color: #ffffff !important;
}

/* 悬停状态优化 */
:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
}

:deep(.el-menu-item:hover .el-icon) {
  color: #ffffff !important;
}

/* 确保菜单项在折叠时居中 */
:deep(.el-menu--collapse .el-menu-item) {
  display: flex;
  justify-content: center;
  align-items: center;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 60px;
}

.content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
</style>
