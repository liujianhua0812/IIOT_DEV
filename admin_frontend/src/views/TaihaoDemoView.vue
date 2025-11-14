<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>泰豪应用示范</h1>
      <p>与泰豪集团共同打造能源与装备产业的多模态协同示范，促成业务全链路协同。</p>
    </header>

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

