<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>内生安全体系</h1>
      <p>以内生可信为核心，贯穿数据、模型、任务全生命周期的纵深防护体系。</p>
    </header>

    <section class="grid">
      <article class="card radar">
        <h2>设备认证</h2>
        <p>融合链路、设备、模型、任务多维指标，实时安全态势感知。</p>
        <div class="chip-group">
          <span class="chip">零信任访问控制</span>
          <span class="chip">模型安全沙箱</span>
          <span class="chip">异常行为画像</span>
        </div>
      </article>
      <article class="card">
        <h3>自适应防护策略</h3>
        <p>安全策略自学习迭代，自动编排边云协同防护链路。</p>
      </article>
      <article class="card">
        <h3>可信审计</h3>
        <p>分布式审计账本，全链路可追溯，确保安全策略可验证、可证明。</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(4, 21, 38, 0.96), rgba(3, 13, 23, 0.96));
  min-height: calc(100vh - 80px);
}

.page-header h1 {
  font-size: 34px;
  margin-bottom: 12px;
  letter-spacing: 1.4px;
}

.page-header p {
  max-width: 640px;
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
  background: linear-gradient(160deg, rgba(9, 32, 56, 0.92), rgba(4, 19, 34, 0.9));
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.36);
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

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.chip {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid rgba(128, 214, 255, 0.2);
  background: rgba(128, 214, 255, 0.12);
  font-size: 13px;
  letter-spacing: 0.8px;
}

.radar {
  background: linear-gradient(135deg, rgba(14, 54, 88, 0.95), rgba(4, 28, 48, 0.9));
  border: 1px solid rgba(73, 197, 255, 0.28);
}
</style>

