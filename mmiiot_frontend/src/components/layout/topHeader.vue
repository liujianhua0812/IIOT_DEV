<template>
  <div id="top-header">



    <div style="width: 48vw;top: 10px"/>
    <div class="center-title">融合算力地图调度中心</div>


    <!--时间-->
    <div id="top">
      <div class="right topBar">
        <div class="topTime">{{ nowTime }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import getTime from '../../assets/js/time'

export default {
  data() {
    return {
      fullscreenLoading: false,
      nowTime: ''
    }
  },
  beforeMount() {
    this.nowTime = getTime()
    setInterval(() => {
      this.nowTime = getTime()
    }, 1000)
  },
  methods: {

  }
}
</script>

<style scoped>

#top-header {
  position: relative;
  width: 100%;
  height: 70px;
  display: flex;
  align-content: center;
  overflow-x: hidden;
  overflow-y: hidden;
  z-index: 0;


  .center-title {
    position: absolute;
    height: 100%;
    width: 100%;
    left: 55vw;
    justify-content: center;
    font-size: 35px;
    font-family: 华文楷体, serif;
    font-weight: bold;
    transform: translateX(-50%);
    color: #08f5d1;
  }
}

/* 设置流光 */
@keyframes sun {
  100% {
    /* 以x轴为基准向左移动4个自身大小 */
    background-position: -400% 0;
  }
}

.right {
  float: right;
}

#top .topBar {
  height: 100%;
  width: 100%;

}

#top .topBar .topTime {
  position: relative;
  top: 10px;
  font-family: 'led regular', serif;
  font-size: 25px;
  color: #08f5d1;
  float: right;
  left: 1vw;
}


</style>
