# 启动说明

本项目支持两种运行模式：**开发模式**和**部署模式**。

## 运行模式说明

### 开发模式 (Development)
- **数据库连接**: 外部服务器 `166.111.80.127:15432`
- **CORS**: 允许所有来源（方便开发调试）
- **Debug**: 启用调试模式
- **用途**: 本地开发环境

### 部署模式 (Production)
- **数据库连接**: 内网服务器 `192.168.34.14:5432`
- **CORS**: 限制跨域来源（通过环境变量配置）
- **Debug**: 关闭调试模式
- **用途**: 生产环境部署

## 启动方式

### 方式一：使用启动脚本（推荐）

#### 开发模式
```bash
cd backend
chmod +x start_dev.sh
./start_dev.sh
```

或者直接运行 Python 脚本：
```bash
cd backend
source venv/bin/activate
python run_dev.py
```

#### 部署模式
```bash
cd backend
chmod +x start_prod.sh
./start_prod.sh
```

或者直接运行 Python 脚本：
```bash
cd backend
source venv/bin/activate
python run_prod.py
```

### 方式二：使用环境变量

#### 开发模式
```bash
cd backend
source venv/bin/activate
export FLASK_ENV=development
export DB_HOST=166.111.80.127
export DB_PORT=15432
python app.py
```

#### 部署模式
```bash
cd backend
source venv/bin/activate
export FLASK_ENV=production
export DB_HOST=192.168.34.14
export DB_PORT=5432
python app.py
```

### 方式三：使用 .env 文件（可选）

创建 `.env` 文件（参考 `.env.example`）：

```bash
# 开发模式配置
FLASK_ENV=development
DB_HOST=166.111.80.127
DB_PORT=15432
DB_USER=admin
DB_PASSWORD=iiotAdmin123
DB_NAME=iiot_platform
FLASK_PORT=5001

# 部署模式配置
# FLASK_ENV=production
# DB_HOST=192.168.34.14
# DB_PORT=5432
# CORS_ORIGINS=http://your-domain.com
```

然后运行：
```bash
cd backend
source venv/bin/activate
python app.py
```

## 环境变量说明

| 变量名 | 说明 | 开发模式默认值 | 部署模式默认值 |
|--------|------|---------------|---------------|
| `FLASK_ENV` | 运行模式 | `development` | `production` |
| `DB_HOST` | 数据库主机 | `166.111.80.127` | `192.168.34.14` |
| `DB_PORT` | 数据库端口 | `15432` | `5432` |
| `DB_USER` | 数据库用户 | `admin` | `admin` |
| `DB_PASSWORD` | 数据库密码 | `iiotAdmin123` | `iiotAdmin123` |
| `DB_NAME` | 数据库名称 | `iiot_platform` | `iiot_platform` |
| `FLASK_PORT` | Flask 服务端口 | `5001` | `5001` |
| `CORS_ORIGINS` | 允许的跨域来源（仅部署模式） | - | `http://localhost:5173` |

## 验证启动

启动成功后，访问健康检查接口：
```bash
curl http://localhost:5001/health
```

应该返回：
```json
{"status":"ok"}
```

## 注意事项

1. **开发模式**：使用外部数据库连接，确保网络可以访问 `166.111.80.127:15432`
2. **部署模式**：使用内网数据库连接，确保服务器可以访问 `192.168.34.14:5432`
3. 首次运行前，请确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 如果使用 `.env` 文件，需要安装 `python-dotenv`：
   ```bash
   pip install python-dotenv
   ```

