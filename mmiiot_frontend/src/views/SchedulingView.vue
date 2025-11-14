<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>融合调度中心</h1>
      <p>全局视角统筹设备、资源与任务，打造柔性、智能的工业调度神经系统。</p>
    </header>

    <section class="grid">
      <article class="card">
        <h2>时空双域调度</h2>
        <p>结合空间布局与时间优先级，实现跨工厂、跨设备的动态资源调配。</p>
      </article>
      <article class="card highlight">
        <h3>智能编排引擎</h3>
        <p>融合强化学习与启发式算法，支持毫秒级响应的快速调度决策。</p>
        <div class="badge-group">
          <span class="badge">任务优先级智能排序</span>
          <span class="badge">调度冲突自解耦</span>
        </div>
      </article>
      <article class="card">
        <h3>任务生命周期</h3>
        <p>提供任务定义、调度、执行、反馈全链路闭环管理，透明可追踪。</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(5, 23, 40, 0.95), rgba(3, 13, 23, 0.95));
  min-height: calc(100vh - 80px);
}

.page-header h1 {
  font-size: 34px;
  margin-bottom: 12px;
  letter-spacing: 1.4px;
}

.page-header p {
  max-width: 660px;
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
  background: linear-gradient(155deg, rgba(9, 31, 52, 0.9), rgba(5, 24, 40, 0.92));
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

.highlight {
  background: linear-gradient(135deg, rgba(16, 72, 125, 0.96), rgba(8, 37, 62, 0.9));
  border: 1px solid rgba(73, 197, 255, 0.3);
}

.badge-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.badge {
  padding: 10px 16px;
  border-radius: 12px;
  background: rgba(128, 214, 255, 0.14);
  border: 1px solid rgba(128, 214, 255, 0.24);
  font-size: 13px;
  letter-spacing: 0.8px;
}
</style>

