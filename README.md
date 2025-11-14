# 多模态网络工业互联网平台 (MMIIoT)

## 项目简介

多模态网络工业互联网平台，采用 Vue 3 + Flask 架构，支持多模态设备管理、内生安全、融合调度等功能。

## 快速开始

### 一键启动（推荐）

#### 开发模式
```bash
./start_dev.sh
```

#### 部署模式
```bash
./start_prod.sh
```

#### 停止服务
```bash
./stop.sh
```

### 访问地址

- **开发模式**：
  - 前端：http://localhost:5173
  - 后端：http://localhost:5001

- **部署模式**：
  - 前端：http://166.111.80.127:10061
  - 后端：http://166.111.80.127:10060

## 项目结构

```
MMIIoT/
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── views/     # 页面视图
│   │   ├── components/# 组件
│   │   └── services/  # API 服务
│   └── package.json
├── backend/           # Flask 后端
│   ├── app.py         # 主应用
│   ├── database.py    # 数据库模型
│   ├── config.py      # 配置管理
│   └── requirements.txt
└── logs/              # 日志文件

```

## 详细文档

- [一键启动说明](./README_START_ALL.md) - 完整启动指南
- [后端启动说明](./backend/README_START.md) - 后端详细配置
- [数据库说明](./backend/README_DB.md) - 数据库配置和使用

## 技术栈

### 前端
- Vue 3
- Vue Router
- Axios
- ECharts
- Vite

### 后端
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-CORS

## 开发模式 vs 部署模式

| 特性 | 开发模式 | 部署模式 |
|------|---------|---------|
| 数据库 | 166.111.80.127:15432 | 192.168.34.14:5432 |
| 后端地址 | localhost:5001 | 166.111.80.127:10060 |
| 前端地址 | localhost:5173 | 166.111.80.127:10061 |
| CORS | 允许所有来源 | 限制来源 |
| Debug | 启用 | 关闭 |
| 前端 | 开发服务器 | 构建后预览 |

## 许可证

MIT
