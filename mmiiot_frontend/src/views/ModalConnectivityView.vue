<script setup>
const baseURL = (import.meta.env.BASE_URL || '/').replace(/\/$/, '')
const tsnConfiguratorURL = `${baseURL}/tsn-configurator`

const openTSNConfigurator = () => {
  window.open(tsnConfiguratorURL, '_blank', 'noopener')
}
</script>

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

    <!-- TSN Configurator, Scheduler and Simulator 板块 -->
    <section class="tsn-section">
      <header class="section-header">
        <div class="section-header-content">
          <div>
            <h2>TSN 配置器、调度器与仿真器</h2>
            <p>基于浏览器的 TSN 网络配置、调度计算与仿真平台，支持可视化拓扑设计和时间敏感网络调度优化。</p>
          </div>
          <button type="button" class="tsn-launch-btn" @click="openTSNConfigurator">
            <span>🚀</span>
            启动 TSN Configurator
          </button>
        </div>
      </header>

      <div class="tsn-grid">
        <article class="tsn-card">
          <div class="tsn-icon">📐</div>
          <h3>网络场景创建</h3>
          <p>可视化拖拽式网络拓扑设计，支持终端站和交换机的灵活配置与连接管理。</p>
          <ul>
            <li>交互式拓扑画布设计</li>
            <li>设备参数配置（IP、MAC、端口等）</li>
            <li>链路属性设置（速度、长度、权重）</li>
          </ul>
        </article>

        <article class="tsn-card">
          <div class="tsn-icon">⚙️</div>
          <h3>TSN 调度计算</h3>
          <p>基于网络拓扑和流量需求，自动生成 TSN 调度表与门控列表（GCL）配置。</p>
          <ul>
            <li>自动生成超周期调度表</li>
            <li>门控状态与时隙配置</li>
            <li>BE 周期、保护带、TSN 流周期分配</li>
          </ul>
        </article>

        <article class="tsn-card">
          <div class="tsn-icon">🔬</div>
          <h3>网络仿真</h3>
          <p>实时仿真验证调度方案的性能指标，包括端到端延迟、抖动等关键参数。</p>
          <ul>
            <li>端到端延迟分析</li>
            <li>流量路径可视化</li>
            <li>性能指标评估与报告</li>
          </ul>
        </article>

        <article class="tsn-card feature-highlight">
          <div class="tsn-icon">🌐</div>
          <h3>浏览器架构</h3>
          <p>无需安装客户端，基于 Web 技术实现跨平台访问与协作。</p>
          <ul>
            <li>跨平台 Web 应用</li>
            <li>实时协作支持</li>
            <li>在线配置与导出</li>
          </ul>
        </article>
      </div>
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

/* TSN 板块样式 */
.tsn-section {
  margin-top: 64px;
  padding-top: 48px;
  border-top: 1px solid rgba(88, 178, 255, 0.15);
}

.section-header {
  margin-bottom: 40px;
}

.section-header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 32px;
}

.section-header h2 {
  font-size: 32px;
  margin-bottom: 16px;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #58b2ff, #7db8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-header p {
  max-width: 800px;
  color: rgba(214, 232, 255, 0.74);
  line-height: 1.8;
  font-size: 16px;
}

.tsn-launch-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #49c5ff, #36a3f7);
  color: #0b2338;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(73, 197, 255, 0.3);
  white-space: nowrap;
  border: none;
  cursor: pointer;
}

.tsn-launch-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(73, 197, 255, 0.4);
}

.tsn-launch-btn span {
  font-size: 20px;
}

.tsn-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 28px;
}

.tsn-card {
  background: linear-gradient(160deg, rgba(11, 35, 59, 0.88), rgba(7, 27, 44, 0.9));
  border-radius: 20px;
  padding: 28px 32px;
  border: 1px solid rgba(88, 178, 255, 0.12);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.32);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.tsn-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 32px 56px rgba(88, 178, 255, 0.15);
  border-color: rgba(88, 178, 255, 0.25);
}

.tsn-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.tsn-card h3 {
  font-size: 24px;
  margin-bottom: 14px;
  color: #e6f1ff;
}

.tsn-card p {
  color: rgba(214, 232, 255, 0.75);
  line-height: 1.8;
  margin-bottom: 16px;
}

.tsn-card ul {
  margin-top: 18px;
  padding-left: 20px;
  color: rgba(214, 232, 255, 0.78);
  line-height: 1.8;
}

.tsn-card ul li {
  margin-bottom: 8px;
}

.tsn-card.feature-highlight {
  background: linear-gradient(135deg, rgba(21, 82, 132, 0.95), rgba(8, 37, 64, 0.9));
  border: 1px solid rgba(73, 197, 255, 0.3);
}
</style>

