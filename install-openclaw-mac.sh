#!/bin/bash
# OpenClaw 一键安装脚本 (macOS Intel)
# 作者：杠杠 🦞
# 适用：macOS 12.7+, Intel 芯片 (x86_64)
# 使用方法：curl -fsSL https://raw.githubusercontent.com/Ricebug-1017/jeedragon-config/main/install-openclaw-mac.sh | bash

set -e

echo "🦞 开始安装 OpenClaw..."
echo "================================"

# 检测芯片类型
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    BREW_PATH="/usr/local/bin/brew"
    NODE_PATH="/usr/local/opt/node@22/bin"
    echo "   检测到 Intel 芯片 ($ARCH)"
elif [ "$ARCH" = "arm64" ]; then
    BREW_PATH="/opt/homebrew/bin/brew"
    NODE_PATH="/opt/homebrew/opt/node@22/bin"
    echo "   检测到 Apple Silicon ($ARCH)"
else
    echo "   ⚠ 未知芯片类型：$ARCH"
    BREW_PATH="/usr/local/bin/brew"
    NODE_PATH="/usr/local/opt/node@22/bin"
fi

# 1. 检查并安装 Homebrew
echo "📦 步骤 1/5: 安装 Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "   未检测到 Homebrew，正在安装..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 根据芯片类型配置环境变量
    if [ "$ARCH" = "arm64" ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    echo "   ✓ Homebrew 安装完成"
else
    echo "   ✓ Homebrew 已安装 ($(brew --version | head -1))"
fi

# 2. 安装 Node.js 22+
echo "📦 步骤 2/5: 安装 Node.js 22..."
if ! command -v node &> /dev/null; then
    echo "   正在安装 Node.js 22..."
    brew install node@22
    
    # 配置 PATH
    if ! grep -q "node@22" ~/.zshrc 2>/dev/null; then
        echo "export PATH=\"$NODE_PATH:\$PATH\"" >> ~/.zshrc
        export PATH="$NODE_PATH:$PATH"
    fi
    echo "   ✓ Node.js 安装完成 ($(node --version))"
elif [ $(node --version | cut -d'v' -f2 | cut -d'.' -f1) -lt 22 ]; then
    echo "   Node.js 版本过低，正在升级..."
    brew upgrade node@22
    echo "   ✓ Node.js 已升级 ($(node --version))"
else
    echo "   ✓ Node.js 已安装 ($(node --version))"
fi

# 3. 安装 OpenClaw
echo "📦 步骤 3/5: 安装 OpenClaw..."
if ! command -v openclaw &> /dev/null; then
    echo "   正在安装 OpenClaw..."
    npm install -g openclaw
    echo "   ✓ OpenClaw 安装完成 ($(openclaw --version 2>/dev/null || echo 'latest'))"
else
    echo "   ✓ OpenClaw 已安装"
    echo "   检查更新..."
    openclaw upgrade 2>/dev/null || true
fi

# 4. 创建工作区
echo "📦 步骤 4/5: 配置工作区..."
WORKSPACE_DIR="$HOME/OpenClaw-Workspace"
if [ ! -d "$WORKSPACE_DIR" ]; then
    mkdir -p "$WORKSPACE_DIR"
    echo "   ✓ 创建工作区：$WORKSPACE_DIR"
else
    echo "   ✓ 工作区已存在"
fi

# 5. 初始化配置
echo "📦 步骤 5/5: 初始化配置..."
cd "$WORKSPACE_DIR"
if [ ! -f "openclaw.json" ]; then
    echo "   正在初始化配置..."
    openclaw init
    echo "   ✓ 配置已初始化"
else
    echo "   ✓ 配置已存在"
fi

# 6. 同步 jeedragon-config
echo "🔄 同步 jeedragon-config 配置..."
CONFIG_DIR="$WORKSPACE_DIR/jeedragon-config"
if [ ! -d "$CONFIG_DIR" ]; then
    if command -v git &> /dev/null; then
        git clone https://github.com/Ricebug-1017/jeedragon-config.git "$CONFIG_DIR" 2>/dev/null && {
            echo "   ✓ 配置仓库已克隆"
        } || {
            echo "   ⚠ Git 仓库无法访问，跳过同步"
        }
    else
        echo "   ⚠ 未安装 Git，跳过同步"
    fi
else
    echo "   ✓ 配置仓库已存在"
    cd "$CONFIG_DIR" && git pull 2>/dev/null || true
fi

echo ""
echo "================================"
echo "✅ 安装完成！"
echo ""
echo "📍 工作区位置：$WORKSPACE_DIR"
echo ""
echo "下一步："
echo "1. 配置模型和插件：cd $WORKSPACE_DIR && openclaw configure"
echo "2. 启动网关：openclaw gateway start"
echo "3. 开始使用：openclaw chat"
echo ""
echo "🦞 杠杠已就位！大哥随时召唤！"
