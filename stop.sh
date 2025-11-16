#!/bin/bash
# 停止所有服务脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}正在停止服务...${NC}"

# 停止后端
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}后端服务已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}后端服务未运行${NC}"
    fi
    rm -f logs/backend.pid
else
    # 尝试通过端口查找并停止（端口10060）
    BACKEND_PID=$(lsof -ti:10060 2>/dev/null || true)
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}后端服务已停止 (PID: $BACKEND_PID)${NC}"
    fi
fi

# 停止展示前端
if [ -f "logs/mmiiot_frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/mmiiot_frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}展示前端已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}展示前端未运行${NC}"
    fi
    rm -f logs/mmiiot_frontend.pid
else
    FRONTEND_PID=$(lsof -ti:10061 2>/dev/null || true)
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}展示前端已停止 (PID: $FRONTEND_PID)${NC}"
    fi
fi

# 停止管理前端
if [ -f "logs/admin_frontend.pid" ]; then
    ADMIN_PID=$(cat logs/admin_frontend.pid)
    if ps -p $ADMIN_PID > /dev/null 2>&1; then
        kill $ADMIN_PID 2>/dev/null || true
        echo -e "${GREEN}管理前端已停止 (PID: $ADMIN_PID)${NC}"
    else
        echo -e "${YELLOW}管理前端未运行${NC}"
    fi
    rm -f logs/admin_frontend.pid
else
    ADMIN_PID=$(lsof -ti:10062 2>/dev/null || true)
    if [ ! -z "$ADMIN_PID" ]; then
        kill $ADMIN_PID 2>/dev/null || true
        echo -e "${GREEN}管理前端已停止 (PID: $ADMIN_PID)${NC}"
    fi
fi

# 停止 LenovoFMS
if [ -f "logs/lenovofms.pid" ]; then
    FMS_PID=$(cat logs/lenovofms.pid)
    if ps -p $FMS_PID > /dev/null 2>&1; then
        kill $FMS_PID 2>/dev/null || true
        echo -e "${GREEN}LenovoFMS 已停止 (PID: $FMS_PID)${NC}"
    fi
    rm -f logs/lenovofms.pid
else
    FMS_PID=$(lsof -ti:10063 2>/dev/null || true)
    if [ ! -z "$FMS_PID" ]; then
        kill $FMS_PID 2>/dev/null || true
        echo -e "${GREEN}LenovoFMS 已停止 (PID: $FMS_PID)${NC}"
    fi
fi

# 停止 LenovoPLM
if [ -f "logs/lenovoplm.pid" ]; then
    PLM_PID=$(cat logs/lenovoplm.pid)
    if ps -p $PLM_PID > /dev/null 2>&1; then
        kill $PLM_PID 2>/dev/null || true
        echo -e "${GREEN}LenovoPLM 已停止 (PID: $PLM_PID)${NC}"
    fi
    rm -f logs/lenovoplm.pid
else
    PLM_PID=$(lsof -ti:10064 2>/dev/null || true)
    if [ ! -z "$PLM_PID" ]; then
        kill $PLM_PID 2>/dev/null || true
        echo -e "${GREEN}LenovoPLM 已停止 (PID: $PLM_PID)${NC}"
    fi
fi

# 停止 TellhowTraffic
if [ -f "logs/tellhowtraffic.pid" ]; then
    TRAFFIC_PID=$(cat logs/tellhowtraffic.pid)
    if ps -p $TRAFFIC_PID > /dev/null 2>&1; then
        kill $TRAFFIC_PID 2>/dev/null || true
        echo -e "${GREEN}TellhowTraffic 已停止 (PID: $TRAFFIC_PID)${NC}"
    fi
    rm -f logs/tellhowtraffic.pid
else
    TRAFFIC_PID=$(lsof -ti:10065 2>/dev/null || true)
    if [ ! -z "$TRAFFIC_PID" ]; then
        kill $TRAFFIC_PID 2>/dev/null || true
        echo -e "${GREEN}TellhowTraffic 已停止 (PID: $TRAFFIC_PID)${NC}"
    fi
fi

# 清理可能的残留进程
pkill -f "python.*run_dev.py" 2>/dev/null || true
pkill -f "python.*run_prod.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo -e "${GREEN}所有服务已停止${NC}"

