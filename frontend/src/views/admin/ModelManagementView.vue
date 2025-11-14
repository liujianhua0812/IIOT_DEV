<script setup>
const models = [
  {
    name: '多模态缺陷检测模型',
    version: 'v2.3.1',
    status: '已部署',
    accuracy: '98.3%',
    lastUpdated: '2025-10-08',
  },
  {
    name: '声学异常识别模型',
    version: 'v1.7.4',
    status: '调试中',
    accuracy: '95.6%',
    lastUpdated: '2025-09-28',
  },
  {
    name: '能源预测调度模型',
    version: 'v3.0.0',
    status: '上线准备',
    accuracy: '97.1%',
    lastUpdated: '2025-10-15',
  },
]

const statusColorMap = {
  已部署: 'status-deployed',
  调试中: 'status-tuning',
  上线准备: 'status-ready',
}
</script>

<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1>模型管理</h1>
        <p>管理平台各类多模态模型的版本、部署状态与关键性能指标。</p>
      </div>
      <button class="action">发布新模型</button>
    </header>

    <div class="model-list">
      <article v-for="model in models" :key="model.name" class="model-card">
        <header>
          <h2>{{ model.name }}</h2>
          <span :class="['status', statusColorMap[model.status]]">{{ model.status }}</span>
        </header>
        <dl>
          <div>
            <dt>版本</dt>
            <dd>{{ model.version }}</dd>
          </div>
          <div>
            <dt>精确率</dt>
            <dd>{{ model.accuracy }}</dd>
          </div>
          <div>
            <dt>更新时间</dt>
            <dd>{{ model.lastUpdated }}</dd>
          </div>
        </dl>
        <footer>
          <button class="ghost">查看详情</button>
          <button class="ghost">部署记录</button>
        </footer>
      </article>
    </div>
  </div>
</template>

<style scoped>
.panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px 36px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #303133;
  font-weight: 600;
}

.panel-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.action {
  padding: 10px 24px;
  border-radius: 6px;
  border: none;
  background: #409eff;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.action:hover {
  background: #66b1ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.model-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.model-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px 28px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.25s ease;
}

.model-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #c0c4cc;
}

.model-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-card h2 {
  font-size: 18px;
  margin: 0;
  flex: 1;
  margin-right: 16px;
  color: #303133;
  font-weight: 600;
}

.status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-deployed {
  background: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.status-tuning {
  background: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.status-ready {
  background: #f0f9ff;
  color: #67c23a;
  border: 1px solid #b3e19d;
}

dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
}

dt {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

dd {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

footer {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

.ghost {
  flex: 1;
  padding: 8px 0;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #606266;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 13px;
}

.ghost:hover {
  background: #ecf5ff;
  border-color: #b3d8ff;
  color: #409eff;
}
</style>

