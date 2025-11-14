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

# 检查展示前端依赖
if [ ! -d "mmiiot_frontend/node_modules" ]; then
    echo -e "${YELLOW}警告: 展示前端依赖未安装，正在安装...${NC}"
    cd mmiiot_frontend
    npm install
    cd ..
fi

# 检查管理前端依赖
if [ ! -d "admin_frontend/node_modules" ]; then
    echo -e "${YELLOW}警告: 管理前端依赖未安装，正在安装...${NC}"
    cd admin_frontend
    npm install
    cd ..
fi

# 检查 LenovoFMS 依赖
if [ ! -d "LenovoFMS/node_modules" ]; then
    echo -e "${YELLOW}警告: LenovoFMS 依赖未安装，正在安装...${NC}"
    cd LenovoFMS
    npm install
    cd ..
fi

# 检查 LenonoPLM 依赖
if [ ! -d "LenonoPLM/node_modules" ]; then
    echo -e "${YELLOW}警告: LenonoPLM 依赖未安装，正在安装...${NC}"
    cd LenonoPLM
    npm install
    cd ..
fi

# 检查 TellhowTraffic 依赖
if [ ! -d "TellhowTraffic/node_modules" ]; then
    echo -e "${YELLOW}警告: TellhowTraffic 依赖未安装，正在安装...${NC}"
    cd TellhowTraffic
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
echo "  API地址: http://localhost:10060"

# 等待后端启动
sleep 3

# 启动展示前端
echo -e "${GREEN}正在启动展示前端 (mmiiot_frontend)...${NC}"
cd mmiiot_frontend
nohup npm run dev > ../logs/mmiiot_frontend.log 2>&1 &
MMI_PID=$!
cd ..
echo -e "${GREEN}展示前端已启动 (PID: $MMI_PID)${NC}"
echo "  日志文件: logs/mmiiot_frontend.log"
echo "  访问地址: http://localhost:10061"

# 启动管理前端
echo -e "${GREEN}正在启动管理前端 (admin_frontend)...${NC}"
cd admin_frontend
nohup npm run dev > ../logs/admin_frontend.log 2>&1 &
ADMIN_PID=$!
cd ..
echo -e "${GREEN}管理前端已启动 (PID: $ADMIN_PID)${NC}"
echo "  日志文件: logs/admin_frontend.log"
echo "  访问地址: http://localhost:10062"

# 启动 LenovoFMS
echo -e "${GREEN}正在启动 LenovoFMS...${NC}"
cd LenovoFMS
nohup npm run dev > ../logs/lenovofms.log 2>&1 &
FMS_PID=$!
cd ..
echo -e "${GREEN}LenovoFMS 已启动 (PID: $FMS_PID)${NC}"
echo "  日志文件: logs/lenovofms.log"
echo "  访问地址: http://localhost:10063"

# 启动 LenonoPLM
echo -e "${GREEN}正在启动 LenonoPLM...${NC}"
cd LenonoPLM
nohup npm run dev > ../logs/lenonoplm.log 2>&1 &
PLM_PID=$!
cd ..
echo -e "${GREEN}LenonoPLM 已启动 (PID: $PLM_PID)${NC}"
echo "  日志文件: logs/lenonoplm.log"
echo "  访问地址: http://localhost:10064"

# 启动 TellhowTraffic
echo -e "${GREEN}正在启动 TellhowTraffic...${NC}"
cd TellhowTraffic
nohup npm run dev > ../logs/tellhowtraffic.log 2>&1 &
TRAFFIC_PID=$!
cd ..
echo -e "${GREEN}TellhowTraffic 已启动 (PID: $TRAFFIC_PID)${NC}"
echo "  日志文件: logs/tellhowtraffic.log"
echo "  访问地址: http://localhost:10065"

# 保存 PID 到文件
echo "$BACKEND_PID" > logs/backend.pid
echo "$MMI_PID" > logs/mmiiot_frontend.pid
echo "$ADMIN_PID" > logs/admin_frontend.pid
echo "$FMS_PID" > logs/lenovofms.pid
echo "$PLM_PID" > logs/lenonoplm.pid
echo "$TRAFFIC_PID" > logs/tellhowtraffic.pid

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}启动完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "展示前端: http://localhost:10061"
echo "管理前端: http://localhost:10062"
echo "LenovoFMS: http://localhost:10063"
echo "LenonoPLM: http://localhost:10064"
echo "TellhowTraffic: http://localhost:10065"
echo "后端: http://localhost:10060"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  展示前端: tail -f logs/mmiiot_frontend.log"
echo "  管理前端: tail -f logs/admin_frontend.log"
echo "  LenovoFMS: tail -f logs/lenovofms.log"
echo "  LenonoPLM: tail -f logs/lenonoplm.log"
echo "  TellhowTraffic: tail -f logs/tellhowtraffic.log"
echo ""
echo "停止服务: ./stop.sh"
echo ""

