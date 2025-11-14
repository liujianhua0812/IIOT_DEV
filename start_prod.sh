#!/bin/bash
# 部署模式一键启动脚本 - 同时启动前端和后端

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
echo -e "${BLUE}  启动部署模式 - 前端 + 后端${NC}"
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

# 部署服务器 IP
DEPLOY_IP="166.111.80.127"

# 检查前端是否已构建
if [ ! -d "frontend/dist" ]; then
    echo -e "${YELLOW}警告: 前端未构建，正在构建...${NC}"
    cd frontend
    npm install
    export VITE_API_BASE_URL=http://${DEPLOY_IP}:10060
    npm run build
    cd ..
fi

# 创建日志目录
mkdir -p logs

# 启动后端
echo -e "${GREEN}正在启动后端服务...${NC}"
cd backend
source venv/bin/activate
export FLASK_ENV=production
export DB_HOST=192.168.34.14
export DB_PORT=5432
export FLASK_PORT=10060
export CORS_ORIGINS="http://${DEPLOY_IP}:10061,http://localhost:10061"
nohup python run_prod.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "  日志文件: logs/backend.log"
echo "  API地址: http://${DEPLOY_IP}:10060"

# 等待后端启动
sleep 3

# 启动前端（使用预览模式，端口10061）
echo -e "${GREEN}正在启动前端服务...${NC}"
cd frontend
nohup npm run preview -- --port 10061 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo "  日志文件: logs/frontend.log"
echo "  访问地址: http://${DEPLOY_IP}:10061"

# 保存 PID 到文件
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}启动完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "前端: http://${DEPLOY_IP}:10061"
echo "后端: http://${DEPLOY_IP}:10060"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务: ./stop.sh"
echo ""

