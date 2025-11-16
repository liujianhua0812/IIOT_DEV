<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>泰豪应用示范</h1>
      <p>与泰豪集团共同打造能源与装备产业的多模态协同示范，促成业务全链路协同。</p>
    </header>

    <section class="systems-section">
      <h2 class="section-title">应用系统</h2>
      <div class="systems-grid">
        <div 
          class="system-card" 
          @click="openSystem('http://166.111.80.127:10065')"
        >
          <div class="system-image-container">
            <img src="/tellhow_traffic.webp" alt="Tellhow Traffic" class="system-image" />
          </div>
          <h3>Tellhow Traffic</h3>
          <p>泰豪交通管理系统</p>
          <div class="system-link">
            <span>访问系统</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
        <div 
          class="system-card" 
          @click="openSystem('http://166.111.80.127:10073/')"
        >
          <div class="system-image-container">
            <img src="/tellhow_iron.png" alt="安全能源生产系统（钢铁）" class="system-image" />
          </div>
          <h3>安全能源生产系统（钢铁）</h3>
          <p>面向钢铁行业的能源安全生产管理系统</p>
          <div class="system-link">
            <span>访问系统</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
        <div 
          class="system-card" 
          @click="openSystem('http://166.111.80.127:10073/')"
        >
          <div class="system-image-container">
            <img src="/tellhow_fire.jpg" alt="安全能源生产系统（火电）" class="system-image" />
          </div>
          <h3>安全能源生产系统（火电）</h3>
          <p>面向火电行业的能源安全生产管理系统</p>
          <div class="system-link">
            <span>访问系统</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <section class="grid">
      <article class="card focus">
        <h2>能源协同调度</h2>
        <p>实现发、输、配各环节数据互联，支撑能源负荷智能平衡与峰谷自动调节。</p>
      </article>
      <article class="card">
        <h3>装备数字孪生</h3>
        <p>构建关键装备多模态数字孪生体，实现运维状态高度仿真与预测。</p>
      </article>
      <article class="card">
        <h3>生态联动</h3>
        <p>与合作伙伴共建生态，在新能源、储能、工业服务等场景快速复制推广。</p>
      </article>
    </section>
  </div>
</template>

<script setup>
const openSystem = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(5, 22, 38, 0.95), rgba(3, 13, 23, 0.95));
  min-height: calc(100vh - 80px);
}

.page-header h1 {
  font-size: 34px;
  margin-bottom: 12px;
  letter-spacing: 1.2px;
}

.page-header p {
  max-width: 680px;
  color: rgba(214, 232, 255, 0.74);
  line-height: 1.8;
}

.systems-section {
  margin-top: 48px;
}

.section-title {
  font-size: 28px;
  margin-bottom: 24px;
  letter-spacing: 1px;
  color: #e6f1ff;
}

.systems-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 550px));
  gap: 48px;
  margin-bottom: 48px;
  justify-content: center;
}

.system-card {
  background: linear-gradient(160deg, rgba(10, 30, 50, 0.92), rgba(6, 22, 36, 0.92));
  border-radius: 20px;
  padding: 0;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.32);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.system-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(88, 178, 255, 0.5), rgba(73, 197, 255, 0.8));
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.system-card:hover {
  transform: translateY(-4px);
  border-color: rgba(73, 197, 255, 0.4);
  box-shadow: 0 32px 56px rgba(0, 0, 0, 0.4);
}

.system-card:hover::before {
  transform: scaleX(1);
}

.system-image-container {
  width: 100%;
  height: 320px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
  position: relative;
  border-radius: 20px 20px 0 0;
}

.system-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.system-card:hover .system-image {
  transform: scale(1.08);
}

.system-card h3,
.system-card p,
.system-card .system-link {
  padding: 0 32px;
}

.system-card h3 {
  margin-top: 24px;
}

.system-card p {
  margin-bottom: 24px;
  flex-grow: 1;
}

.system-card .system-link {
  margin-bottom: 32px;
  padding-bottom: 0;
}

.system-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, rgba(17, 72, 116, 0.8), rgba(6, 28, 48, 0.9));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #58b2ff;
  margin-bottom: 20px;
  border: 1px solid rgba(88, 178, 255, 0.2);
}

.system-card h3 {
  font-size: 24px;
  margin-bottom: 12px;
  color: #e6f1ff;
}

.system-card p {
  color: rgba(214, 232, 255, 0.75);
  line-height: 1.7;
  margin-bottom: 20px;
}

.system-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #58b2ff;
  font-size: 14px;
  font-weight: 500;
  margin-top: auto;
  transition: gap 0.3s ease;
}

.system-card:hover .system-link {
  gap: 12px;
}

.system-link svg {
  transition: transform 0.3s ease;
}

.system-card:hover .system-link svg {
  transform: translateX(4px);
}

.grid {
  margin-top: 32px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.card {
  background: linear-gradient(160deg, rgba(10, 30, 50, 0.92), rgba(6, 22, 36, 0.92));
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.32);
}

.card h2,
.card h3 {
  font-size: 22px;
  margin-bottom: 14px;
}

.card p {
  color: rgba(214, 232, 255, 0.75);
  line-height: 1.7;
}

.focus {
  background: linear-gradient(135deg, rgba(17, 72, 116, 0.94), rgba(6, 28, 48, 0.92));
  border: 1px solid rgba(73, 197, 255, 0.3);
}
</style>

