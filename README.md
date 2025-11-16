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

- **开发模式/部署模式**（端口统一）：
  - 后端：http://localhost:10060 / http://166.111.80.127:10060
  - 展示前端：http://localhost:10061 / http://166.111.80.127:10061
  - 管理前端：http://localhost:10062 / http://166.111.80.127:10062
  - LenovoFMS：http://localhost:10063 / http://166.111.80.127:10063
  - LenovoPLM：http://localhost:10064 / http://166.111.80.127:10064
  - TellhowTraffic：http://localhost:10065 / http://166.111.80.127:10065

## 项目结构

```
MMIIoT/
├── mmiiot_frontend/   # 展示型 Vue 前端
│   ├── src/
│   └── package.json
├── admin_frontend/    # 管理端 Vue 前端
│   ├── src/
│   └── package.json
├── LenovoFMS/         # 联想设备管理系统
│   ├── src/
│   └── package.json
├── LenovoPLM/         # 联想产品生命周期管理
│   ├── src/
│   └── package.json
├── TellhowTraffic/    # 泰豪交通管理系统
│   ├── src/
│   └── package.json
├── backend/           # Flask 后端
│   ├── app.py         # 主应用
│   ├── database.py    # 数据库模型
│   ├── config.py      # 配置管理
│   └── requirements.txt
└── logs/              # 日志文件

```

## 环境变量

| 变量名 | 作用 | 默认值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | 前端访问后端 API 的基础地址 | `http://localhost:10060` |
| `VITE_ADMIN_BASE_URL` | 展示前端跳转后台管理站点的地址 | `http://localhost:10062` |

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
| 后端地址 | localhost:10060 | 166.111.80.127:10060 |
| 展示前端 | localhost:10061 | 166.111.80.127:10061 |
| 管理前端 | localhost:10062 | 166.111.80.127:10062 |
| LenovoFMS | localhost:10063 | 166.111.80.127:10063 |
| LenovoPLM | localhost:10064 | 166.111.80.127:10064 |
| TellhowTraffic | localhost:10065 | 166.111.80.127:10065 |
| CORS | 允许所有来源 | 限制来源 |
| Debug | 启用 | 关闭 |

## 许可证

MIT
