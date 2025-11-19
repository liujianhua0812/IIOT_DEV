import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
  },
  {
    path: '/modal-connectivity',
    name: 'modal-connectivity',
    component: () => import('../views/ModalConnectivityView.vue'),
  },
  {
    path: '/security',
    name: 'security',
    component: () => import('../views/SecurityView.vue'),
  },
  {
    path: '/scheduling',
    name: 'scheduling',
    component: () => import('../views/SchedulingView.vue'),
  },
  {
    path: '/ddos-check',
    name: 'ddos-check',
    component: () => import('../views/DdosCheckView.vue'),
  },
  {
    path: '/ddos/system-status',
    name: 'ddos-system-status',
    component: () => import('../views/DdosSystemStatusView.vue'),
  },
  {
    path: '/ddos/device-monitor',
    name: 'ddos-device-monitor',
    component: () => import('../views/DdosDeviceMonitorView.vue'),
  },
  {
    path: '/ddos-check',
    name: 'ddos-check',
    component: () => import('../views/DdosCheckView.vue'),
  },
  {
    path: '/ddos/system-status',
    name: 'ddos-system-status',
    component: () => import('../views/DdosSystemStatusView.vue'),
  },
  {
    path: '/ddos/device-monitor',
    name: 'ddos-device-monitor',
    component: () => import('../views/DdosDeviceMonitorView.vue'),
  },
  {
    path: '/demo/lenovo',
    name: 'demo-lenovo',
    component: () => import('../views/LianxiangDemoView.vue'),
  },
  {
    path: '/demo/tellhow',
    name: 'demo-tellhow',
    component: () => import('../views/TaihaoDemoView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router

