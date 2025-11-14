# 数据库配置和使用说明

## 数据库连接信息

- **服务器地址**: 166.111.80.127
- **端口**: 15432 (映射到容器内的 5432)
- **数据库名**: iiot_platform
- **用户名**: admin
- **密码**: iiotAdmin123

## 表结构

### organizations (组织表)

已存在的表，包含以下字段：
- `id` (INTEGER, PRIMARY KEY) - 组织ID
- `name` (VARCHAR(200), NOT NULL) - 组织名称
- `code` (VARCHAR(100), NOT NULL) - 组织代码
- `parent_id` (INTEGER) - 父组织ID
- `level` (INTEGER) - 组织层级
- `region` (VARCHAR(100)) - 所属区域
- `address` (VARCHAR(500)) - 地址
- `contact` (VARCHAR(100)) - 联系人
- `phone` (VARCHAR(20)) - 联系电话
- `description` (TEXT) - 组织描述
- `is_active` (BOOLEAN) - 是否激活
- `created_at` (TIMESTAMP) - 创建时间
- `updated_at` (TIMESTAMP) - 更新时间

### applications (应用表)

**已创建完成**，包含以下字段：
- `id` (INTEGER, PRIMARY KEY) - 应用ID
- `name` (VARCHAR(100), NOT NULL) - **应用名称**
- `english_name` (VARCHAR(100)) - **应用英文名**
- `organization_id` (INTEGER, NOT NULL, FOREIGN KEY) - **所属组织ID** (外键关联 organizations.id)
- `description` (TEXT) - 应用描述
- `created_at` (TIMESTAMP) - 创建时间
- `updated_at` (TIMESTAMP) - 更新时间

**外键约束**: `organization_id` -> `organizations.id` (ON DELETE CASCADE)

## 使用方法

### 1. 安装依赖

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

如果需要修改数据库连接信息，可以设置环境变量：

```bash
export DB_HOST=166.111.80.127
export DB_PORT=15432
export DB_USER=admin
export DB_PASSWORD=iiotAdmin123
export DB_NAME=iiot_platform
```

### 3. 使用数据库模型

```python
from database import SessionLocal, Organization, Application

# 获取数据库会话
db = SessionLocal()

# 创建应用
app = Application(
    name="我的应用",
    english_name="My Application",
    organization_id=1,  # 组织ID
    description="应用描述"
)
db.add(app)
db.commit()

# 查询应用（包含组织信息）
apps = db.query(Application).all()
for app in apps:
    print(f"{app.name} ({app.english_name}) - 组织: {app.organization.name}")

db.close()
```

### 4. 测试数据库连接

```bash
python test_db.py
```

### 5. 初始化数据库表（如果需要重新创建）

```bash
python init_db.py
```

## 文件说明

- `config.py` - 数据库配置
- `database.py` - 数据库模型定义
- `init_db.py` - 数据库初始化脚本
- `init_tables.sql` - SQL 初始化脚本（备用）
- `test_db.py` - 数据库测试脚本

## 注意事项

1. `applications` 表已创建完成，可以直接使用
2. `organizations` 表已存在，请使用现有的表结构
3. 外键约束已设置，删除组织时会级联删除相关应用
4. 建议在生产环境中使用环境变量管理数据库密码

