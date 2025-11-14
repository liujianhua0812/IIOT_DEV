#!/bin/bash
# 重启部署模式服务

echo "正在停止所有服务..."
./stop.sh

sleep 2

echo "正在启动部署模式..."
./start_prod.sh

