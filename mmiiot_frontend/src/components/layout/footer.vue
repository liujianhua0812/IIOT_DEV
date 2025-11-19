<template>
  <div class="footer">
    <div class="icon icon-1">
      <img src="../../assets/image/globe-256.png" alt="" class="icon-img"/>
      <div class="text">
        <div class="number" style="color: #08f5d1;">3323</div>
        <div class="under_text" style="color: #08f5d1;">通用算力</div>
      </div>
    </div>
    <div class="icon icon-2">
      <img src="../../assets/image/computer-256.png" alt="" class="icon-img"/>
      <div class="text">
        <div class="number" style="color: #ef6715;">1361093</div>
        <div class="under_text" style="color: #ef6715;">智能算力</div>
      </div>
    </div>
    <div class="icon icon-3">
      <img src="../../assets/image/save-as-256.png" alt="" class="icon-img"/>
      <div class="text">
        <div class="number" style="color: #d2e80a;">73523</div>
        <div class="under_text" style="color: #d2e80a;">存储资源</div>
      </div>
    </div>
    <div class="icon icon-4">
      <img src="../../assets/image/network-256.png" alt="" class="icon-img"/>
      <div class="text">
        <div class="number" style="color: #06e46d;">32</div>
        <div class="under_text" style="color: #06e46d;">算力资源数量</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

onMounted(() => {
  const numberElements = document.getElementsByClassName('number');
  Array.from(numberElements).forEach(item => {
    const number = parseInt(item.textContent, 10);
    item.textContent = number.toLocaleString();
  });

  let currentIconIndex = 0;
  const icons = document.querySelectorAll('.icon');
  const totalIcons = icons.length;

  setInterval(() => {
    icons.forEach(icon => icon.classList.remove('hover'));
    icons[currentIconIndex].classList.add('hover');
    currentIconIndex = (currentIconIndex + 1) % totalIcons;
  }, 2000);
});
</script>

<style scoped>
.footer {
  z-index: 1;
  width: 60vw;
  bottom: -20vh;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  margin: -50px 60px;
  background: linear-gradient(135deg, rgba(1, 36, 80, 0.2), rgba(2, 48, 76, 0.2), rgba(2, 73, 110, 0.2), rgba(3, 118, 155, 0.2), rgba(0, 255, 204, 0.2));
  padding: 20px;
  border-radius: 15px;
  position: absolute;
  overflow: hidden;
  animation: gradientAnimation 10s ease infinite;
  border: 1px solid rgba(30, 187, 238, 0.6);
  box-shadow: 10px 0 40px rgba(2, 214, 251, 0.8);
}

.footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px solid rgba(30, 187, 238, 0.6);
  border-radius: 15px;
  background: rgba(30, 187, 238, 0.1);
  pointer-events: none;
  z-index: 1;
}

@keyframes gradientAnimation {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.icon {
  display: flex;
  align-items: center;
  color: #fff;
  transition: transform 0.5s, box-shadow 0.5s;
}

.icon.hover {
  transform: translateY(-5px);
 }

.icon:hover {
  transform: translateY(-5px);
 }

.icon-img {
  width: 65px;
  transition: transform 0.5s;
}

.icon.hover .icon-img {
  transform: rotate(10deg) scale(1.1);
}

.text {
  margin-left: 10px;
}

.number {
  font-weight: 600;
  font-family: 'DS-Digital', serif;
  font-size: 30px;
  font-style: italic;
  text-shadow: 0 0 5px rgba(0, 255, 204, 0.7);
  transition: color 0.3s, text-shadow 0.3s;
}

.icon.hover .number {
  transform: scale(1.2);
}

.text .under_text {
  font-size: 20px;
  font-family: '华文楷体', serif;
  font-weight: 700;
  display: flex;
  transition: color 0.3s;
}

@keyframes glowing {
  0% {
    text-shadow: 0 0 5px rgba(30, 187, 238, 0.7), 0 0 10px rgba(30, 187, 238, 0.4);
  }
  50% {
    text-shadow: 0 0 15px rgba(0, 234, 255, 1), 0 0 20px rgba(39, 198, 198, 0.6);
  }
  100% {
    text-shadow: 0 0 5px rgba(0, 255, 204, 0.7), 0 0 10px rgba(0, 255, 204, 0.4);
  }
}

.number {
  animation: glowing 1.5s infinite;
}
</style>
