<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import TopNavbar from './components/layout/TopNavbar.vue'

const route = useRoute()
const isAdminPage = computed(() => route.path.startsWith('/admin'))
</script>

<template>
  <div class="app-shell" :class="{ 'admin-mode': isAdminPage }">
    <TopNavbar v-if="!isAdminPage" />
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

.app-shell.admin-mode {
  background: #f5f7fa;
}

.content {
  flex: 1;
}
</style>
