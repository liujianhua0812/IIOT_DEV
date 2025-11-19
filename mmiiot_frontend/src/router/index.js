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
    path: '/demo/lenovo',
    name: 'demo-lenovo',
    component: () => import('../views/LianxiangDemoView.vue'),
  },
  {
    path: '/demo/tellhow',
    name: 'demo-tellhow',
    component: () => import('../views/TaihaoDemoView.vue'),
  },
  {
    path: '/security/edge-model-access-control',
    name: 'edge-model-access-control',
    component: () => import('../views/EdgeModelAccessControlView.vue'),
  },
  {
    path: '/security/cloud-model-access-control',
    name: 'cloud-model-access-control',
    component: () => import('../views/CloudModelAccessControlView.vue'),
  },
  {
    path: '/security/cloud-data-access-control',
    name: 'cloud-data-access-control',
    component: () => import('../views/CloudDataAccessControlView.vue'),
  },
  {
    path: '/security/chain-data-access-control',
    name: 'chain-data-access-control',
    component: () => import('../views/ChainDataAccessControlView.vue'),
  },
  {
    path: '/security/video-data-access-control',
    name: 'video-data-access-control',
    component: () => import('../views/VideoDataAccessControlView.vue'),
  },
  {
    path: '/security/device-verification/:deviceType?',
    name: 'device-verification',
    component: () => import('../views/DeviceVerificationView.vue'),
    path: '/tsn-configurator',
    name: 'tsn-configurator',
    component: () => import('../views/TSNConfiguratorView.vue'),
    meta: {
      standalone: true,
    },
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

