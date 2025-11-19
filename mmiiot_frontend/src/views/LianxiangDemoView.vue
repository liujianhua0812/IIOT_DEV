<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>联想应用示范</h1>
      <p>携手联想打造多模态工业互联网标杆应用，验证方案在大型制造场景下的可持续价值。</p>
    </header>

    <section class="systems-section">
      <h2 class="section-title">应用系统</h2>
      <div class="systems-grid">
        <div 
          class="system-card" 
          @click="openSystem('http://166.111.80.127:10063')"
        >
          <div class="system-image-container">
            <img src="/lenovo_fms.png" alt="Lenovo FMS" class="system-image" />
          </div>
          <h3>Lenovo FMS</h3>
          <p>联想设备管理系统</p>
          <div class="system-link">
            <span>访问系统</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
        <div 
          class="system-card" 
          @click="openSystem('http://166.111.80.127:10064')"
        >
          <div class="system-image-container">
            <img src="/lenovo_plm.png" alt="Lenovo PLM" class="system-image" />
          </div>
          <h3>Lenovo PLM</h3>
          <p>联想产品生命周期管理系统</p>
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
      <article class="card spotlight">
        <h2>示范场景</h2>
        <p>面向联想智慧工厂，实现设备全生命周期管理与多模态质量检测。</p>
        <ul>
          <li>生产节拍实时精准控制</li>
          <li>多模态质检模型推理</li>
          <li>边云协同数据发布</li>
        </ul>
      </article>
      <article class="card">
        <h3>核心成果</h3>
        <p>生产效率提升 18%，设备故障平均预警提前 72 小时，多模态模型部署效率提升 40%。</p>
      </article>
      <article class="card">
        <h3>未来计划</h3>
        <p>进一步覆盖供应链协同、绿色能源调度与跨区域协同运维场景。</p>
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
  background: radial-gradient(circle at top, rgba(6, 23, 40, 0.94), rgba(3, 13, 23, 0.95));
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
  background: linear-gradient(160deg, rgba(12, 35, 58, 0.9), rgba(7, 25, 42, 0.92));
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
  background: linear-gradient(135deg, rgba(24, 88, 150, 0.8), rgba(8, 32, 54, 0.9));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
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
  background: linear-gradient(160deg, rgba(12, 35, 58, 0.9), rgba(7, 25, 42, 0.92));
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

.card ul {
  margin-top: 18px;
  padding-left: 18px;
  color: rgba(214, 232, 255, 0.8);
  line-height: 1.6;
}

.spotlight {
  background: linear-gradient(135deg, rgba(24, 88, 150, 0.95), rgba(8, 32, 54, 0.92));
  border: 1px solid rgba(73, 197, 255, 0.3);
}
</style>

