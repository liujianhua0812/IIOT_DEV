#!/bin/bash
# 开发模式启动脚本

cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 设置开发模式环境变量
export FLASK_ENV=development
# 使用本地数据库（如果外部数据库不可用，会自动回退到本地）
# 如果需要使用外部数据库，可以在启动前设置环境变量
export DB_HOST=${DB_HOST:-192.168.34.14}
export DB_PORT=${DB_PORT:-5432}

echo "=========================================="
echo "启动开发模式"
echo "=========================================="
echo "数据库: $DB_HOST:$DB_PORT"
echo "=========================================="

# 运行开发模式脚本
python run_dev.py

