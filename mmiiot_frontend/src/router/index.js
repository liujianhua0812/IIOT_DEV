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
    path: '/demo/lianxiang',
    name: 'demo-lianxiang',
    component: () => import('../views/LianxiangDemoView.vue'),
  },
  {
    path: '/demo/taihao',
    name: 'demo-taihao',
    component: () => import('../views/TaihaoDemoView.vue'),
  },
  {
    path: '/security/edge-model-access-control',
    name: 'edge-model-access-control',
    component: () => import('../views/EdgeModelAccessControlView.vue'),
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

