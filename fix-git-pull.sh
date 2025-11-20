#!/bin/bash

echo "=== 修复 Git 配置并拉取更新 ==="

# 优化 Git 配置以提高速度
echo "优化 Git 配置..."
git config --global core.compression 0
git config --global http.postBuffer 1048576000
git config --global pack.windowMemory 256m
git config --global pack.packSizeLimit 256m
git config --global pack.threads 1

# 询问是否使用代理(私人仓库加速的最佳方法)
echo ""
echo "是否配置代理以加速访问? (推荐用于私人仓库)"
echo "1) 使用 Clash 代理 (默认端口 7890)"
echo "2) 使用自定义代理"
echo "3) 不使用代理"
read -p "请选择 (1/2/3): " proxy_choice

case $proxy_choice in
    1)
        # Clash 默认配置
        CLASH_PORT=7890
        read -p "Clash HTTP 代理端口 [默认 7890]: " input_port
        CLASH_PORT=${input_port:-7890}
        
        proxy_url="http://127.0.0.1:$CLASH_PORT"
        git config --global http.proxy "$proxy_url"
        git config --global https.proxy "$proxy_url"
        echo "✓ 已配置 Clash 代理: $proxy_url"
        
        # 测试代理连接
        echo "测试代理连接..."
        if curl -x "$proxy_url" -s --connect-timeout 3 https://www.google.com > /dev/null 2>&1; then
            echo "✓ 代理连接正常"
        else
            echo "⚠ 代理连接失败,请确认 Clash 是否运行"
        fi
        ;;
    2)
        read -p "请输入代理地址 (例如: http://127.0.0.1:7890): " proxy_url
        git config --global http.proxy "$proxy_url"
        git config --global https.proxy "$proxy_url"
        echo "✓ 已配置代理: $proxy_url"
        ;;
    3)
        echo "跳过代理配置"
        # 清除可能存在的代理配置
        git config --global --unset http.proxy 2>/dev/null
        git config --global --unset https.proxy 2>/dev/null
        ;;
    *)
        echo "无效选择,跳过代理配置"
        ;;
esac

# 1. 检查远程仓库配置
echo "当前远程仓库配置:"
git remote -v

# 强制使用 HTTPS 远程地址
TARGET_URL="https://github.com/seeclong/MMIIoT_Security.git"
CURRENT_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ "$CURRENT_URL" != "$TARGET_URL" ]; then
    echo "将 origin 设置为 HTTPS: $TARGET_URL"
    git remote set-url origin "$TARGET_URL"
fi
echo "使用 HTTPS 连接"
# HTTPS 优化与凭据
git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000
git config --global credential.helper store

# 2. 获取当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

# 3. 使用增量 fetch 提高速度
echo "获取远程更新(使用增量模式)..."
GIT_TRACE_PACKET=0 GIT_TRACE=0 GIT_CURL_VERBOSE=0 \
git -c core.compression=0 \
    -c pack.threads=1 \
    fetch origin $CURRENT_BRANCH --depth=1 --no-tags --progress

if [ $? -ne 0 ]; then
    echo "浅克隆失败,尝试完整 fetch..."
    git fetch origin $CURRENT_BRANCH --progress
fi

# 4. 拉取更新
echo "拉取更新..."
git pull origin $CURRENT_BRANCH

echo "=== 完成 ==="
