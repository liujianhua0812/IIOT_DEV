<template>
  <div class="page-shell">
    <header class="page-header">
      <h1>模态互联总览</h1>
      <p>构建统一的多模态感知通道，实现跨域设备、模型与数据的高效互联。</p>
    </header>

    <section class="grid">
      <article class="card emphasis">
        <h2>多模态采集</h2>
        <p>覆盖视觉、声学、振动、电磁等 12 类模态，统一接入协议，毫秒级同步。</p>
        <ul>
          <li>边缘智能网关快速编排</li>
          <li>实时状态监测与预警</li>
          <li>模态间语义转换与映射</li>
        </ul>
      </article>
      <article class="card">
        <h3>融合互联矩阵</h3>
        <p>支持跨工厂、跨区域的设备即插即用，动态扩缩保障广域互联。</p>
      </article>
      <article class="card">
        <h3>协议自适应</h3>
        <p>工业以太网、5G、TSN、OPC UA 等协议自适应，集成式可视化配置。</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.page-shell {
  padding: 32px 64px 64px;
  color: #e6f1ff;
  background: radial-gradient(circle at top, rgba(6, 25, 44, 0.94), rgba(3, 13, 23, 0.96));
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
  background: linear-gradient(160deg, rgba(11, 35, 59, 0.88), rgba(7, 27, 44, 0.9));
  border-radius: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.32);
}

.card h2,
.card h3 {
  font-size: 22px;
  margin-bottom: 12px;
}

.card p {
  color: rgba(214, 232, 255, 0.75);
  line-height: 1.7;
}

.card ul {
  margin-top: 18px;
  padding-left: 18px;
  color: rgba(214, 232, 255, 0.78);
  line-height: 1.6;
}

.emphasis {
  background: linear-gradient(135deg, rgba(21, 82, 132, 0.95), rgba(8, 37, 64, 0.9));
  border: 1px solid rgba(73, 197, 255, 0.3);
}
</style>

