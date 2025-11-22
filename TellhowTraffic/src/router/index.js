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
    path: '/signal-controller',
    name: 'signal-controller',
    redirect: { name: 'signal-controller-overview' },
  },
  {
    path: '/signal-controller/overview',
    name: 'signal-controller-overview',
    component: () => import('../views/signal-controller/IntersectionOverviewView.vue'),
  },
  {
    path: '/signal-controller/strategy',
    name: 'signal-controller-strategy',
    component: () => import('../views/signal-controller/TrafficStrategyView.vue'),
  },
  {
    path: '/signal-controller/schedule',
    name: 'signal-controller-schedule',
    component: () => import('../views/signal-controller/TimeScheduleView.vue'),
  },
  {
    path: '/signal-controller/monitoring',
    name: 'signal-controller-monitoring',
    component: () => import('../views/signal-controller/RealTimeMonitoringView.vue'),
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

