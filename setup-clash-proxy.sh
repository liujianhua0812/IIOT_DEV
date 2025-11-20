#!/bin/bash

echo "=== 配置 Clash 代理 ==="

# 默认 Clash 端口
CLASH_HTTP_PORT=7890
CLASH_SOCKS_PORT=7891

echo "Clash 默认端口配置:"
echo "  HTTP/HTTPS: 7890"
echo "  SOCKS5: 7891"
echo ""

read -p "HTTP 代理端口 [默认 7890]: " input_http_port
CLASH_HTTP_PORT=${input_http_port:-7890}

# 配置 Git 使用 Clash 代理
echo "配置 Git 代理..."
git config --global http.proxy "http://127.0.0.1:$CLASH_HTTP_PORT"
git config --global https.proxy "http://127.0.0.1:$CLASH_HTTP_PORT"

# 配置 SSH 使用 Clash 代理 (SOCKS5)
echo "配置 SSH 代理..."
mkdir -p ~/.ssh
if ! grep -q "Host github.com" ~/.ssh/config 2>/dev/null; then
    cat >> ~/.ssh/config << EOF

# GitHub through Clash proxy
Host github.com
    ProxyCommand nc -X 5 -x 127.0.0.1:$CLASH_SOCKS_PORT %h %p
    ServerAliveInterval 60
EOF
    echo "✓ SSH 代理配置已添加到 ~/.ssh/config"
else
    echo "⚠ SSH 配置已存在,请手动检查 ~/.ssh/config"
fi

# 配置环境变量代理(可选)
echo ""
echo "是否配置终端环境变量代理? (y/n)"
read -p "这将影响所有命令行工具: " setup_env

if [ "$setup_env" = "y" ]; then
    # 添加到 .bashrc 或 .zshrc
    SHELL_RC="$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if ! grep -q "Clash proxy" "$SHELL_RC" 2>/dev/null; then
        cat >> "$SHELL_RC" << EOF

# Clash proxy
export http_proxy="http://127.0.0.1:$CLASH_HTTP_PORT"
export https_proxy="http://127.0.0.1:$CLASH_HTTP_PORT"
export all_proxy="socks5://127.0.0.1:$CLASH_SOCKS_PORT"
export no_proxy="localhost,127.0.0.1"
EOF
        echo "✓ 环境变量已添加到 $SHELL_RC"
        echo "  运行 'source $SHELL_RC' 或重启终端生效"
    fi
fi

# 测试代理
echo ""
echo "测试代理连接..."
if curl -x "http://127.0.0.1:$CLASH_HTTP_PORT" -s --connect-timeout 5 https://www.google.com > /dev/null 2>&1; then
    echo "✓ HTTP 代理连接正常"
else
    echo "✗ HTTP 代理连接失败"
    echo "  请确认:"
    echo "  1. Clash 是否正在运行"
    echo "  2. 允许局域网连接已开启"
    echo "  3. 端口号是否正确"
fi

echo ""
echo "=== 配置完成 ==="
echo "当前 Git 代理配置:"
git config --global --get http.proxy
git config --global --get https.proxy

echo ""
echo "如需取消代理,运行:"
echo "  git config --global --unset http.proxy"
echo "  git config --global --unset https.proxy"
