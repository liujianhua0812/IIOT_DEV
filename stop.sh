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
    # 尝试通过端口查找并停止（开发模式5001，部署模式10060）
    BACKEND_PID=$(lsof -ti:5001 2>/dev/null || lsof -ti:10060 2>/dev/null || true)
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}后端服务已停止 (PID: $BACKEND_PID)${NC}"
    fi
fi

# 停止前端
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}前端服务已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}前端服务未运行${NC}"
    fi
    rm -f logs/frontend.pid
else
    # 尝试通过端口查找并停止（开发模式5173，部署模式10061）
    FRONTEND_PID=$(lsof -ti:5173 2>/dev/null || lsof -ti:4173 2>/dev/null || lsof -ti:10061 2>/dev/null || true)
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}前端服务已停止 (PID: $FRONTEND_PID)${NC}"
    fi
fi

# 清理可能的残留进程
pkill -f "python.*run_dev.py" 2>/dev/null || true
pkill -f "python.*run_prod.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo -e "${GREEN}所有服务已停止${NC}"

