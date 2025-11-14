<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>联想应用示范</h1>
      <p>携手联想打造多模态工业互联网标杆应用，验证方案在大型制造场景下的可持续价值。</p>
    </header>

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

