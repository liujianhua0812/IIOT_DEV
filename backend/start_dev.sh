#!/bin/bash
# 开发模式启动脚本

cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 设置开发模式环境变量
export FLASK_ENV=development
export DB_HOST=166.111.80.127
export DB_PORT=15432

echo "=========================================="
echo "启动开发模式"
echo "=========================================="
echo "数据库: $DB_HOST:$DB_PORT"
echo "=========================================="

# 运行开发模式脚本
python run_dev.py

