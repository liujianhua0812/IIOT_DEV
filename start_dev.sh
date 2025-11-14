#!/bin/bash
# 开发模式一键启动脚本 - 同时启动前端和后端

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  启动开发模式 - 前端 + 后端${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查后端虚拟环境
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}警告: 后端虚拟环境不存在，正在创建...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}警告: 前端依赖未安装，正在安装...${NC}"
    cd frontend
    npm install
    cd ..
fi

# 创建日志目录
mkdir -p logs

# 启动后端
echo -e "${GREEN}正在启动后端服务...${NC}"
cd backend
source venv/bin/activate
export FLASK_ENV=development
export DB_HOST=166.111.80.127
export DB_PORT=15432
nohup python run_dev.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "  日志文件: logs/backend.log"
echo "  API地址: http://localhost:5001"

# 等待后端启动
sleep 3

# 启动前端
echo -e "${GREEN}正在启动前端服务...${NC}"
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo "  日志文件: logs/frontend.log"
echo "  访问地址: http://localhost:5173"

# 保存 PID 到文件
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}启动完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "前端: http://localhost:5173"
echo "后端: http://localhost:5001"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务: ./stop.sh"
echo ""

