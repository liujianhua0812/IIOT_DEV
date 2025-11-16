<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import TopNavbar from './components/layout/TopNavbar.vue'

const route = useRoute()
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')
const showNavbar = computed(() => !isAuthPage.value)
</script>

<template>
  <div class="app-shell">
    <TopNavbar v-if="showNavbar" />
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: radial-gradient(circle at top, rgba(4, 17, 30, 0.98), rgba(3, 11, 20, 1));
}

.content {
  flex: 1;
}
</style>
