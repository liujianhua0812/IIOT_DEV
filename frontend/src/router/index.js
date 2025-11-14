import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
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
    path: '/admin',
    component: () => import('../views/admin/AdminView.vue'),
    children: [
      {
        path: '',
        redirect: { name: 'admin-devices' },
      },
      {
        path: 'devices',
        name: 'admin-devices',
        component: () => import('../views/admin/DeviceManagementView.vue'),
      },
      {
        path: 'models',
        name: 'admin-models',
        component: () => import('../views/admin/ModelManagementView.vue'),
      },
      {
        path: 'tasks',
        name: 'admin-tasks',
        component: () => import('../views/admin/TaskManagementView.vue'),
      },
    ],
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

