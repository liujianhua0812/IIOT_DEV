<template>
  <div class="city-detail">
    <div class="header">
      <h2>{{ title }}</h2>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    <div class="content">
      <p v-html="content"></p> <!-- 支持HTML格式数据展示 -->
      <div class="county-info" v-if="counties && counties.length > 0">
        <h3>相关市县信息：</h3>
        <ul>
          <li v-for="county in counties" :key="county.name">
            <strong>{{ county.name }}</strong>: {{ county.info }}
          </li>
        </ul>
      </div>
    </div>
    <button class="action-btn" @click="$emit('close')">关闭</button>
  </div>
</template>

<script>
export default {
  props: {
    title: String,
    content: String,
    counties: {
      type: Array,
      default: () => []
    }
  },
  mounted() {
    this.$nextTick(() => {
      const contentElement = this.$el.querySelector('.content');
      if (contentElement) {
        contentElement.style.opacity = '1';
        contentElement.style.transform = 'translateY(0)';
      }
    });
  }
}
</script>

<style scoped>
.city-detail {
  position: fixed;
  top: 10%;
  right: 1%;
  width: 400px;
  height: 40%; /* 增加高度以适应更多内容展示 */
  background: linear-gradient(135deg, rgba(27, 39, 53, 0.8), rgba(9, 10, 15, 0.8)); /* 深色渐变背景，透明度为0.8 */
  box-shadow: -2px 0 30px rgba(0, 0, 0, 0.9); /* 更强的阴影效果 */
  padding: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-top: 3px solid #00d8ff; /* 发光边框加粗 */
  border-radius: 20px;
  border-image: linear-gradient(to bottom, #00d8ff, #007bff) 1;
  overflow: hidden;
  border-top: 3px solid #00d8ff;
  animation: border-glow 2s infinite alternate;
}
@keyframes border-glow {
  0% {
    border-color: #00d8ff;
    box-shadow: 0 0 20px rgba(0, 216, 255, 0.8);
  }
  100% {
    border-color: #007bff;
    box-shadow: 0 0 40px rgba(0, 123, 255, 0.8);
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  margin-bottom: 0; /* 增加与内容的间距 */
}

h2 {
  font-size: 2em; /* 增大标题字体 */
  margin: 0;
  color: #00d8ff; /* 科技感的亮蓝色标题 */
  font-family: '华文楷体','Orbitron', sans-serif; /* 科幻风格字体 */
  letter-spacing: 2px; /* 增加字母间距 */
  text-transform: uppercase; /* 字母大写 */
  text-shadow: 0 0 10px rgba(0, 216, 255, 0.8); /* 增加标题发光效果 */
}

.close-btn {
  background: none;
  border: none;
  font-size: 2em;
  cursor: pointer;
  color: #888;
  transition: color 0.3s ease, transform 0.3s ease;
}

.close-btn:active {
  transform: scale(0.9); /* 点击时缩小按钮 */
}
.action-btn:active {
  transform: translateY(-3px) scale(0.95); /* 点击时按钮稍微缩小并向上弹 */
  box-shadow: 0 8px 20px rgba(0, 216, 255, 0.5), 0 0 10px rgba(0, 216, 255, 0.5);
}
.close-btn:hover {
  color: #00d8ff; /* 悬停时与标题颜色一致 */
  transform: rotate(90deg) scale(1.2); /* 悬停时旋转并放大按钮 */
}

.content {
  flex: 1;
  padding: 20px 0;
  font-size: 1.2em; /* 增大内容字体，适应数据展示 */
  color: #f0f0f0; /* 更亮的灰色字体 */
  line-height: 1.8;
  font-family: 'Roboto', sans-serif;
  position: relative;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.city-detail-enter-active .content {
  opacity: 1;
  transform: translateY(0);
}
.content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(to right, transparent, #00d8ff);
  animation: scanning 5s linear infinite; /* 扫描线动画 */
}

@keyframes scanning {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

.action-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #00d8ff, #007bff);
  color: #1e1e1e;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  align-self: flex-end;
  transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 216, 255, 0.5), 0 0 10px rgba(0, 216, 255, 0.5); /* 发光按钮效果 */
}

.action-btn:hover {
  background-color: #0056b3;
  transform: translateY(-3px) scale(1.05); /* 悬停时微微上升并放大 */
  box-shadow: 0 8px 20px rgba(0, 216, 255, 0.8), 0 0 15px rgba(0, 216, 255, 0.8); /* 更强的发光效果 */
}

/* 新增的数字或数据展示样式 */
.data-display {
  font-family: 'Orbitron', sans-serif; /* 科幻风格字体 */
  color: #00d8ff; /* 亮蓝色字体 */
  font-size: 1.5em; /* 增大数据展示的字体 */
  text-shadow: 0 0 5px rgba(0, 216, 255, 0.7); /* 发光效果 */
  margin: 10px 0;
}

@media (max-width: 600px) {
  .city-detail {
    width: 100%;
    height: auto;
    bottom: 0;
    right: 0;
    top: auto;
  }
}

.county-info ul li {
  transition: transform 0.3s ease, color 0.3s ease;
}
.county-info ul li:hover {
  transform: scale(1.05);
  color: #00d8ff;
  text-shadow: 0 0 5px rgba(0, 216, 255, 0.7);
}
.city-detail:hover {
  box-shadow: -2px 0 40px rgba(0, 216, 255, 0.9);
}
</style>
