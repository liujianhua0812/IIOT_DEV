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

# 构建展示前端
cd mmiiot_frontend
npm install
export VITE_API_BASE_URL=http://${DEPLOY_IP}:10060
npm run build
cd ..

# 构建管理前端
cd admin_frontend
npm install
export VITE_API_BASE_URL=http://${DEPLOY_IP}:10060
npm run build
cd ..

# 构建 LenovoFMS
cd LenovoFMS
npm install
export VITE_API_BASE_URL=http://${DEPLOY_IP}:10060
npm run build
cd ..

# 构建 LenovoPLM
cd LenovoPLM
npm install
export VITE_API_BASE_URL=http://${DEPLOY_IP}:10060
npm run build
cd ..

# 构建 TellhowTraffic
cd TellhowTraffic
npm install
export VITE_API_BASE_URL=http://${DEPLOY_IP}:10060
npm run build
cd ..



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
export CORS_ORIGINS="http://${DEPLOY_IP}:10061,http://${DEPLOY_IP}:10062,http://${DEPLOY_IP}:10063,http://${DEPLOY_IP}:10064,http://${DEPLOY_IP}:10065,http://localhost:10061,http://localhost:10062,http://localhost:10063,http://localhost:10064,http://localhost:10065,http://localhost:10075"
nohup python run_prod.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "  日志文件: logs/backend.log"
echo "  API地址: http://${DEPLOY_IP}:10060"

# 等待后端启动
sleep 3

# 启动展示前端（端口10061）
echo -e "${GREEN}正在启动展示前端 (mmiiot_frontend)...${NC}"
cd mmiiot_frontend
nohup npm run preview -- --port 10061 > ../logs/mmiiot_frontend.log 2>&1 &
MMI_PID=$!
cd ..
echo -e "${GREEN}展示前端已启动 (PID: $MMI_PID)${NC}"
echo "  日志文件: logs/mmiiot_frontend.log"
echo "  访问地址: http://${DEPLOY_IP}:10061"

# 启动管理前端（端口10062）
echo -e "${GREEN}正在启动管理前端 (admin_frontend)...${NC}"
cd admin_frontend
nohup npm run preview -- --port 10062 > ../logs/admin_frontend.log 2>&1 &
ADMIN_PID=$!
cd ..
echo -e "${GREEN}管理前端已启动 (PID: $ADMIN_PID)${NC}"
echo "  日志文件: logs/admin_frontend.log"
echo "  访问地址: http://${DEPLOY_IP}:10062"

# 启动 LenovoFMS（端口10063）
echo -e "${GREEN}正在启动 LenovoFMS...${NC}"
cd LenovoFMS
nohup npm run preview -- --port 10063 > ../logs/lenovofms.log 2>&1 &
FMS_PID=$!
cd ..
echo -e "${GREEN}LenovoFMS 已启动 (PID: $FMS_PID)${NC}"
echo "  日志文件: logs/lenovofms.log"
echo "  访问地址: http://${DEPLOY_IP}:10063"

# 启动 LenovoPLM（端口10064）
echo -e "${GREEN}正在启动 LenovoPLM...${NC}"
cd LenovoPLM
nohup npm run preview -- --port 10064 > ../logs/lenovoplm.log 2>&1 &
PLM_PID=$!
cd ..
echo -e "${GREEN}LenovoPLM 已启动 (PID: $PLM_PID)${NC}"
echo "  日志文件: logs/lenovoplm.log"
echo "  访问地址: http://${DEPLOY_IP}:10064"

# 启动 TellhowTraffic（端口10065）
echo -e "${GREEN}正在启动 TellhowTraffic...${NC}"
cd TellhowTraffic
nohup npm run preview -- --port 10065 > ../logs/tellhowtraffic.log 2>&1 &
TRAFFIC_PID=$!
cd ..
echo -e "${GREEN}TellhowTraffic 已启动 (PID: $TRAFFIC_PID)${NC}"
echo "  日志文件: logs/tellhowtraffic.log"
echo "  访问地址: http://${DEPLOY_IP}:10065"

<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> af3dc14effb2fb97c5ce3caff4b7ca60e68893ef
=======

>>>>>>> 67a6c12f36420bc41d31d5c2ebe62bb334f08ba5
# 保存 PID 到文件
echo "$BACKEND_PID" > logs/backend.pid
echo "$MMI_PID" > logs/mmiiot_frontend.pid
echo "$ADMIN_PID" > logs/admin_frontend.pid
echo "$FMS_PID" > logs/lenovofms.pid
echo "$PLM_PID" > logs/lenovoplm.pid
echo "$TRAFFIC_PID" > logs/tellhowtraffic.pid

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}启动完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "展示前端: http://${DEPLOY_IP}:10061"
echo "管理前端: http://${DEPLOY_IP}:10062"
echo "LenovoFMS: http://${DEPLOY_IP}:10063"
echo "LenovoPLM: http://${DEPLOY_IP}:10064"
echo "TellhowTraffic: http://${DEPLOY_IP}:10065"
echo "后端: http://${DEPLOY_IP}:10060"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  展示前端: tail -f logs/mmiiot_frontend.log"
echo "  管理前端: tail -f logs/admin_frontend.log"
echo "  LenovoFMS: tail -f logs/lenovofms.log"
echo "  LenovoPLM: tail -f logs/lenovoplm.log"
echo "  TellhowTraffic: tail -f logs/tellhowtraffic.log"
echo ""
echo "停止服务: ./stop.sh"
echo ""

