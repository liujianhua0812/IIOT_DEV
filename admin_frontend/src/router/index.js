import { createRouter, createWebHistory } from 'vue-router'

const routes = [
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
    path: '/',
    component: () => import('../views/admin/AdminView.vue'),
    children: [
      {
        path: '',
        redirect: { name: 'devices' },
      },
      {
        path: 'devices',
        name: 'devices',
        component: () => import('../views/admin/DeviceManagementView.vue'),
      },
      {
        path: 'device-types',
        name: 'device-types',
        component: () => import('../views/admin/DeviceTypeManagementView.vue'),
      },
      {
        path: 'models',
        name: 'models',
        component: () => import('../views/admin/ModelManagementView.vue'),
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: () => import('../views/admin/TaskManagementView.vue'),
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('../views/admin/ProfileView.vue'),
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

