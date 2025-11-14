# 快速启动指南

## 🚀 开发模式（推荐用于本地开发）

### 方法 1: 使用启动脚本
```bash
cd backend
./start_dev.sh
```

### 方法 2: 使用 Python 脚本
```bash
cd backend
source venv/bin/activate
python run_dev.py
```

### 方法 3: 直接运行
```bash
cd backend
source venv/bin/activate
export FLASK_ENV=development
python app.py
```

**数据库连接**: `166.111.80.127:15432`

---

## 🏭 部署模式（用于生产环境）

### 方法 1: 使用启动脚本
```bash
cd backend
./start_prod.sh
```

### 方法 2: 使用 Python 脚本
```bash
cd backend
source venv/bin/activate
python run_prod.py
```

### 方法 3: 直接运行
```bash
cd backend
source venv/bin/activate
export FLASK_ENV=production
python app.py
```

**数据库连接**: `192.168.34.14:5432`

---

## 📝 配置说明

- **开发模式**: 外部数据库，允许所有 CORS，启用 Debug
- **部署模式**: 内网数据库，限制 CORS，关闭 Debug

详细说明请查看 `README_START.md`

