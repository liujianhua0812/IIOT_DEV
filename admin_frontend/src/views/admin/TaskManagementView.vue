<script setup>
const tasks = [
  {
    id: 'TSK-2201',
    name: '华北节点能耗调度',
    assignee: '智能调度引擎',
    status: '执行中',
    progress: 68,
    eta: '2025-11-13 19:20',
  },
  {
    id: 'TSK-2194',
    name: '多模态质检模型回传',
    assignee: '模型服务编排',
    status: '排队中',
    progress: 24,
    eta: '2025-11-13 18:00',
  },
  {
    id: 'TSK-2176',
    name: '西南节点安全巡检',
    assignee: '安全巡检机器人',
    status: '已完成',
    progress: 100,
    eta: '2025-11-13 16:45',
  },
]

const statusClassMap = {
  执行中: 'running',
  排队中: 'queued',
  已完成: 'done',
}
</script>

<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1>任务管理</h1>
        <p>统一调度平台任务，实时掌握任务流状态与执行效率。</p>
      </div>
      <button class="action">创建新任务</button>
    </header>

    <div class="task-list">
      <article v-for="task in tasks" :key="task.id" class="task-card">
        <header>
          <div>
            <h2>{{ task.name }}</h2>
            <span class="task-id">{{ task.id }}</span>
          </div>
          <span :class="['status', statusClassMap[task.status]]">{{ task.status }}</span>
        </header>

        <dl class="meta">
          <div>
            <dt>执行主体</dt>
            <dd>{{ task.assignee }}</dd>
          </div>
          <div>
            <dt>预计完成</dt>
            <dd>{{ task.eta }}</dd>
          </div>
        </dl>

        <div class="progress">
          <div class="progress-bar" :style="{ width: `${task.progress}%` }"></div>
        </div>
        <div class="progress-meta">
          <span>进度</span>
          <span>{{ task.progress }}%</span>
        </div>
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

.task-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.task-card {
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

.task-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #c0c4cc;
}

.task-card header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.task-card h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.task-id {
  display: inline-block;
  margin-top: 6px;
  padding: 4px 10px;
  border-radius: 4px;
  background: #f5f7fa;
  color: #909399;
  font-size: 12px;
}

.status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status.running {
  background: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.status.queued {
  background: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.status.done {
  background: #f0f9ff;
  color: #67c23a;
  border: 1px solid #b3e19d;
}

.meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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

.progress {
  position: relative;
  height: 8px;
  border-radius: 999px;
  background: #e4e7ed;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 999px;
  transition: width 0.6s ease;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}
</style>

