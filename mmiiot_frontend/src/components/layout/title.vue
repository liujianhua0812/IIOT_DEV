<template>
  <div class="title">
    <div class="line"></div>
    <div>{{ title }}</div>
  </div>
</template>

<script setup >

const props = defineProps({
  title: {
    type: String,
    required: true
  }
});
</script>


<style>
.title {
  background: linear-gradient(to right, rgba(48, 82, 174, 0.5), rgba(48, 82, 174, 0));
  font-size: 24px;
  color: #08f5d1;
  margin-top: 10px;
  margin-left: 2%;
  font-family: '华文楷体', serif;
  font-weight: bold;
  padding-left: 3%;
  text-align: left;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.line {
  width: 10px;
  height: 40px;
  background: #00ffcc;
  margin-right: 10px;
  position: relative;
  z-index: 0;
}

.title-text {
  position: relative;
  z-index: 1;
  animation: textGlow 2s infinite alternate;
}

@keyframes textGlow {
  0% { text-shadow: 0 0 5px #08f5d1, 0 0 10px #08f5d1, 0 0 15px #08f5d1, 0 0 20px #08f5d1; }
  100% { text-shadow: 0 0 10px #08f5d1, 0 0 20px #08f5d1, 0 0 30px #08f5d1, 0 0 40px #08f5d1; }
}

.title::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, transparent, rgba(8, 245, 209, 0.2), transparent);
  animation: shine 3s infinite linear;
}

@keyframes shine {
  0% { left: -100%; }
  100% { left: 100%; }
}

.title::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(8, 245, 209, 0.1), transparent 70%);
  opacity: 0.6;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 0.6; }
}
</style>

