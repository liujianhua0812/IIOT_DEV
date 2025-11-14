#!/bin/bash
# 部署模式启动脚本

cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 设置部署模式环境变量
export FLASK_ENV=production
export DB_HOST=192.168.34.14
export DB_PORT=5432

echo "=========================================="
echo "启动部署模式"
echo "=========================================="
echo "数据库: $DB_HOST:$DB_PORT"
echo "=========================================="

# 运行部署模式脚本
python run_prod.py

