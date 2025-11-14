# 一键启动脚本说明

本项目提供了两种模式的一键启动脚本，可以同时启动前端和后端服务。

## 🚀 开发模式（Development）

### Linux/macOS
```bash
./start_dev.sh
```

### Windows
```cmd
start_dev.bat
```

**配置说明：**
- 后端：`http://localhost:10060`
- 展示前端：`http://localhost:10061` (`mmiiot_frontend`)
- 管理前端：`http://localhost:10062` (`admin_frontend`)
- LenovoFMS：`http://localhost:10063`
- LenonoPLM：`http://localhost:10064`
- TellhowTraffic：`http://localhost:10065`
- 数据库：`166.111.80.127:15432`（外部连接）
- 模式：开发模式，启用 Debug，允许所有 CORS

## 🏭 部署模式（Production）

### Linux/macOS
```bash
./start_prod.sh
```

### Windows
```cmd
start_prod.bat
```

**配置说明：**
- 后端：`http://166.111.80.127:10060`
- 展示前端：`http://166.111.80.127:10061`
- 管理前端：`http://166.111.80.127:10062`
- 数据库：`192.168.34.14:5432`（内网连接）
- 模式：部署模式，关闭 Debug，限制 CORS

## 🛑 停止服务

### Linux/macOS
```bash
./stop.sh
```

### Windows
按 `Ctrl+C` 或关闭对应的命令行窗口

## 📋 日志文件

启动后，日志文件保存在 `logs/` 目录：
- `logs/backend.log` - 后端日志
- `logs/mmiiot_frontend.log` - 展示前端日志
- `logs/admin_frontend.log` - 管理前端日志
- `logs/backend.pid` - 后端进程ID
- `logs/mmiiot_frontend.pid` - 展示前端进程ID
- `logs/admin_frontend.pid` - 管理前端进程ID

查看实时日志：
```bash
# 后端日志
tail -f logs/backend.log

# 展示前端日志
tail -f logs/mmiiot_frontend.log

# 管理前端日志
tail -f logs/admin_frontend.log
```

## 🔧 手动启动

如果一键启动脚本不工作，可以手动启动：

### 开发模式

**终端 1 - 启动后端：**
```bash
cd backend
source venv/bin/activate
export FLASK_ENV=development
python run_dev.py
```

**终端 2 - 启动展示前端：**
```bash
cd mmiiot_frontend
npm run dev
```

**终端 3 - 启动管理前端：**
```bash
cd admin_frontend
npm run dev
```

**终端 4-6 - 启动其他前端项目（可选）：**
```bash
# LenovoFMS
cd LenovoFMS
npm run dev

# LenonoPLM
cd LenonoPLM
npm run dev

# TellhowTraffic
cd TellhowTraffic
npm run dev
```

### 部署模式

**终端 1 - 启动后端：**
```bash
cd backend
source venv/bin/activate
export FLASK_ENV=production
python run_prod.py
```

**终端 2 - 启动展示前端：**
```bash
cd mmiiot_frontend
export VITE_API_BASE_URL=http://166.111.80.127:10060
npm run preview -- --port 10061
```

**终端 3 - 启动管理前端：**
```bash
cd admin_frontend
export VITE_API_BASE_URL=http://166.111.80.127:10060
npm run preview -- --port 10062
```

## ⚠️ 注意事项

1. **首次运行**：脚本会自动检查并安装依赖
2. **端口占用**：
   - 开发/部署模式：确保以下端口未被占用
     - 10060：后端
     - 10061：展示前端 (mmiiot_frontend)
     - 10062：管理前端 (admin_frontend)
     - 10063：LenovoFMS
     - 10064：LenonoPLM
     - 10065：TellhowTraffic
   - 部署模式访问地址：`http://166.111.80.127:10060-10065`
3. **数据库连接**：确保可以访问对应的数据库服务器
4. **权限问题**：Linux/macOS 需要给脚本添加执行权限：
   ```bash
   chmod +x start_dev.sh start_prod.sh stop.sh
   ```

## 🐛 故障排查

### 端口被占用
```bash
# 查看端口占用
lsof -i :10060  # 后端
lsof -i :10061  # 展示前端
lsof -i :10062  # 管理前端
lsof -i :10063  # LenovoFMS
lsof -i :10064  # LenonoPLM
lsof -i :10065  # TellhowTraffic

# 停止占用端口的进程
kill -9 <PID>
```

### 服务无法启动
1. 检查日志文件：`logs/backend.log` 和 `logs/frontend.log`
2. 检查依赖是否安装完整
3. 检查数据库连接是否正常
4. 检查虚拟环境是否正确激活

### 数据库连接失败
- 开发模式：检查是否可以访问 `166.111.80.127:15432`
- 部署模式：检查是否可以访问 `192.168.34.14:5432`
- 检查数据库用户名和密码是否正确

