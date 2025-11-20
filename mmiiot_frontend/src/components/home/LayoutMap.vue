<template>
  <div class="container">
    <Side />
    <div class="main">
      <TopHeader />
      <Main />
      <Bottom />
    </div>
  </div>
</template>

<script setup >
import Side from '../layout/side.vue'
import TopHeader from '../layout/topHeader.vue'
import Bottom from '../layout/footer.vue'
import Main from './Main.vue'
import {defineComponent} from "vue";

// 使用 defineOptions 来命名组件

defineComponent({
  name: 'LayoutMap'
})
</script>

<style scoped>
.container {
  height: 100%;
  display: flex;
}
.main {
  flex: 1;
}
.container {
  background: url("@/assets/image/black_earth.jpg") no-repeat;
  background-size: 100% 100%;
  overflow: hidden;
}
</style>
