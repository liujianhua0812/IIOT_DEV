#!/bin/bash

echo "=== 配置 GitHub SSH 密钥 ==="

# 1. 检查是否已有 SSH 密钥
if [ -f ~/.ssh/id_rsa.pub ]; then
    echo "检测到已存在 SSH 密钥:"
    cat ~/.ssh/id_rsa.pub
    echo ""
    read -p "是否要生成新密钥? (y/n): " generate_new
    if [ "$generate_new" != "y" ]; then
        echo "使用现有密钥"
        cat ~/.ssh/id_rsa.pub
        exit 0
    fi
fi

# 2. 生成新的 SSH 密钥
echo "请输入您的 GitHub 邮箱:"
read email

echo "生成 SSH 密钥..."
ssh-keygen -t rsa -b 4096 -C "$email" -f ~/.ssh/id_rsa -N ""

# 3. 启动 ssh-agent
echo "启动 ssh-agent..."
eval "$(ssh-agent -s)"

# 4. 添加密钥到 ssh-agent
echo "添加密钥到 ssh-agent..."
ssh-add ~/.ssh/id_rsa

# 5. 显示公钥
echo ""
echo "=== 您的 SSH 公钥如下 ==="
cat ~/.ssh/id_rsa.pub
echo ""
echo "=== 下一步操作 ==="
echo "1. 复制上面的公钥"
echo "2. 打开 https://github.com/settings/keys"
echo "3. 点击 'New SSH key'"
echo "4. 粘贴公钥并保存"
echo "5. 运行以下命令测试连接:"
echo "   ssh -T git@github.com"
echo ""
echo "6. 然后切换远程仓库 URL:"
echo "   git remote set-url origin git@github.com:ZDYFProject/MMIIoT.git"
