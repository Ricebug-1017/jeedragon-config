# 🦞 OpenClaw Mac 安装指南

> 在 macOS 上部署 OpenClaw 本地分身

---

## 📋 系统要求

- macOS 12.7 或更高版本
- Intel 芯片 (x86_64) 或 Apple Silicon (arm64)
- 管理员权限

---

## 🚀 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/Ricebug-1017/jeedragon-config/master/install-openclaw-mac.sh | bash
```

---

## 📝 手动安装（如遇问题）

### 步骤 1: 安装 Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 步骤 2: 配置环境变量

**Intel 芯片:**
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

**Apple Silicon:**
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 步骤 3: 安装 Node.js 22

```bash
brew install node@22
```

### 步骤 4: 安装 OpenClaw

```bash
npm install -g openclaw
```

### 步骤 5: 创建工作区

```bash
mkdir -p ~/OpenClaw-Workspace
cd ~/OpenClaw-Workspace
openclaw init
```

---

## ⚙️ 安装后配置

### 1. 配置模型和插件

```bash
cd ~/OpenClaw-Workspace
openclaw configure
```

**推荐配置:**
- 模型：`bailian/qwen3.5-plus` (百炼)
- 插件：`feishu` (飞书通信)

### 2. 启动网关

```bash
openclaw gateway start
```

### 3. 打开控制面板

```bash
openclaw dashboard
```

访问：http://localhost:18789

### 4. 测试通信

```bash
openclaw chat
```

---

## 📁 重要路径

| 项目 | 路径 |
|------|------|
| 工作区 | `~/OpenClaw-Workspace` |
| 配置文件 | `~/OpenClaw-Workspace/openclaw.json` |
| 凭证文件 | `~/OpenClaw-Workspace/.env` |
| 配置仓库 | `~/OpenClaw-Workspace/jeedragon-config` |

---

## 🔐 配置凭证

编辑 `.env` 文件：

```bash
nano ~/OpenClaw-Workspace/.env
```

添加你的 API Keys：

```env
# GitHub 配置
GITHUB_TOKEN=ghp_xxxxx

# 百炼 API 配置
BAI_LIAN_API_KEY=xxxxx

# 飞书 Bot 配置
FEISHU_APP_ID=xxxxx
FEISHU_APP_SECRET=xxxxx
```

设置文件权限：

```bash
chmod 600 ~/OpenClaw-Workspace/.env
```

---

## 🛠️ 常用命令

```bash
# 查看状态
openclaw status

# 重启网关
openclaw gateway restart

# 更新 OpenClaw
openclaw upgrade

# 查看日志
openclaw logs
```

---

## 🐛 常见问题

### Q: 安装脚本提示权限不足
**A:** 确保当前用户是管理员，或在命令前加 `sudo`

### Q: Homebrew 安装失败
**A:** 检查网络连接，或手动下载 Homebrew 安装脚本

### Q: Node.js 版本过低
**A:** 运行 `brew upgrade node@22` 升级

### Q: GitHub 推送失败
**A:** 检查 token 是否有效，或配置 SSH key

---

## 📞 获取帮助

- OpenClaw 官方文档：https://docs.openclaw.ai
- GitHub Issues: https://github.com/Ricebug-1017/jeedragon-config/issues
- 语雀工作空间：https://www.yuque.com/jeehyun2789/gwkml3/lgzc9ylmb1txisim

---

*最后更新：2026-03-23*
