# OpenClaw 完整配置指南

> **当前稳定版本**: OpenClaw 2026.4.23 · macOS 12.7.6 · Node.js v24.0.0
> 
> **主模型**: bailian/qwen3.6-plus（阿里云百炼）
> 
> **更新时间**: 2026-04-25

---

## 目录

1. [系统环境要求](#1-系统环境要求)
2. [安装 OpenClaw](#2-安装-openclaw)
3. [模型配置 — 阿里云百炼 (Bailian)](#3-模型配置--阿里云百炼-bailian)
4. [配置 qwen3.6-plus 模型（重点）](#4-配置-qwen36-plus-模型重点)
5. [飞书双机器人配置](#5-飞书双机器人配置)
6. [Gateway 服务配置](#6-gateway-服务配置)
7. [升级 OpenClaw](#7-升级-openclaw)
8. [常见问题排查](#8-常见问题排查)
9. [备份与恢复](#9-备份与恢复)

---

## 1. 系统环境要求

| 项目 | 要求 |
|------|------|
| OS | macOS 12+ / Linux / Windows (WSL2) |
| Node.js | v24.0.0+ (推荐用 nvm 管理) |
| npm | 11.0.0+ |
| 网络 | 需要访问 dashscope.aliyuncs.com |

**检查环境：**
```bash
node -v        # 应输出 v24.x.x
npm -v         # 应输出 11.x.x
```

---

## 2. 安装 OpenClaw

```bash
# 全局安装最新版本
npm install -g openclaw@latest

# 验证安装
openclaw --version

# 首次运行配置向导（可选，推荐新手使用）
openclaw onboard
```

**安装位置：**
- 可执行文件：`~/.npm-global/bin/openclaw`
- 配置目录：`~/.openclaw/`
- 工作目录：`~/.openclaw/workspace/`

---

## 3. 模型配置 — 阿里云百炼 (Bailian)

### 3.1 获取 API Key

1. 登录 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 进入「API-KEY 管理」页面
3. 创建新的 API Key，复制保存（格式：`sk-sp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### 3.2 配置认证

OpenClaw 使用 `auth-profiles.json` 存储认证信息：

```bash
# 文件位置
~/.openclaw/agents/main/agent/auth-profiles.json
```

```json
{
  "version": 1,
  "profiles": {
    "bailian:default": {
      "type": "api_key",
      "provider": "bailian",
      "key": "sk-sp-YOUR_API_KEY_HERE"
    }
  }
}
```

> ⚠️ **重要**: 不要用 `modelstudio` 作为 provider name！新版 OpenClaw 使用 `bailian`。

### 3.3 Provider 端点说明

阿里云百炼有**两个不同的端点**：

| 端点 | 用途 | 说明 |
|------|------|------|
| `https://dashscope.aliyuncs.com/v1` | 百炼标准端点 | 普通模型调用 |
| `https://coding.dashscope.aliyuncs.com/v1` | 编码助手端点 | **我们当前使用的** |

当前配置使用的是 **coding 端点**，因为部分模型（如 qwen3.6-plus）在该端点下表现更稳定。

---

## 4. 配置 qwen3.6-plus 模型（重点）

### 4.1 完整配置示例

主配置文件 `~/.openclaw/openclaw.json` 中需要同时配置三个部分：

```json
{
  "auth": {
    "profiles": {
      "bailian:default": {
        "provider": "bailian",
        "mode": "api_key"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.6-plus",
            "name": "qwen3.6-plus",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.6-plus"
      },
      "models": {
        "bailian/qwen3.6-plus": {}
      }
    }
  }
}
```

### 4.2 关键配置项说明

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `auth.profiles` 的 provider | `bailian` | **不能写 modelstudio**，新版用 bailian |
| `models.providers` 的 key | `bailian` | 必须与 auth profile 的 provider 一致 |
| `baseUrl` | `https://coding.dashscope.aliyuncs.com/v1` | 编码助手端点 |
| `agents.defaults.model.primary` | `bailian/qwen3.6-plus` | 格式: `provider/model-id` |
| `agents.defaults.models` | 必须包含主模型 | 这是模型的**允许列表** |

### 4.3 模型引用格式

- **完整格式**: `provider/model-id`
- **示例**: `bailian/qwen3.6-plus`
- **切换模型**: `/model bailian/qwen3.6-plus`

### 4.4 ⚠️ 常见陷阱

#### 陷阱 1: provider 名称不对

```
❌ 错误: "modelstudio"  ← 旧版名称
✅ 正确: "bailian"      ← 新版名称
```

如果用了 `modelstudio`，会报错：`Unknown model: modelstudio/qwen3.6-plus`

#### 陷阱 2: models 允许列表遗漏

`agents.defaults.models` 是一个**允许列表**，如果主模型不在这个列表里，它不会被加载。

```json
"models": {
  "bailian/qwen3.6-plus": {},  // 必须有这一行！
  "bailian/qwen3.5-plus": {}
}
```

#### 陷阱 3: 升级后 provider 名称变更

从 2026.4.14 升级到 2026.4.23 时，内部 provider 名称从 `modelstudio` 改为 `bailian`。
升级后**必须检查**配置文件中的 provider 名称是否一致。

---

## 5. 飞书双机器人配置

### 5.1 配置结构

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "defaultAccount": "goldfish",
      "connectionMode": "websocket",
      "domain": "feishu",
      "accounts": {
        "goldfish": {
          "appId": "cli_a94fb700de381bce",
          "appSecret": "YOUR_APP_SECRET",
          "name": "金鱼机器人",
          "enabled": true,
          "groupPolicy": "open",
          "requireMention": false
        },
        "lobster": {
          "appId": "cli_a93c1216dd78dbc3",
          "appSecret": "YOUR_APP_SECRET",
          "name": "龙虾机器人",
          "enabled": true
        }
      }
    }
  }
}
```

### 5.2 机器人用途

| 机器人 | 用途 | 平台 |
|--------|------|------|
| 金鱼机器人 | macOS / 咖啡专用 | 飞书 |
| 龙虾机器人 | Windows 专用 | 飞书 |

### 5.3 飞书配置要点

- `connectionMode: "websocket"` — 使用 WebSocket 模式（推荐）
- `groupPolicy: "open"` — 允许加入所有群
- `requireMention: false` — 不需要 @ 也能回复
- `defaultAccount: "goldfish"` — 默认使用金鱼机器人

---

## 6. Gateway 服务配置

### 6.1 启动 / 停止 / 重启

```bash
openclaw gateway start    # 启动
openclaw gateway stop     # 停止
openclaw gateway restart  # 重启
openclaw gateway status   # 查看状态
```

### 6.2 Gateway 配置

```json
{
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "YOUR_GATEWAY_TOKEN"
    }
  }
}
```

- `bind: "loopback"` — 仅本地访问（127.0.0.1）
- 端口：18789
- Dashboard：http://127.0.0.1:18789/

### 6.3 日志查看

```bash
openclaw logs              # 查看最近日志
openclaw logs --follow     # 实时查看日志
```

日志文件位置：`/tmp/openclaw/openclaw-*.log`

---

## 7. 升级 OpenClaw

### 7.1 升级步骤

```bash
# 1. 停止 Gateway
openclaw gateway stop

# 2. 清理旧版本（重要！防止 ENOTEMPTY 错误）
rm -rf ~/.npm-global/lib/node_modules/.openclaw-* 2>/dev/null

# 3. 安装最新版本
npm install -g openclaw@latest

# 4. 验证版本
openclaw --version

# 5. 检查配置
openclaw doctor

# 6. 重启 Gateway
openclaw gateway restart
```

### 7.2 升级后必做检查

1. ✅ 检查 provider 名称是否一致（`bailian` vs `modelstudio`）
2. ✅ 检查 `auth-profiles.json` 中的 provider 是否匹配
3. ✅ 检查 `agents.defaults.models` 允许列表是否包含主模型
4. ✅ 更新 `openclaw.json` 中的 `meta.lastTouchedVersion`

### 7.3 升级常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `ENOTEMPTY` | 旧临时目录未清理 | `rm -rf ~/.npm-global/lib/node_modules/.openclaw-*` |
| `Unknown model` | provider 名称不匹配 | 统一改为 `bailian` |
| 命令找不到 | PATH 未刷新 | 重新打开终端或 `source ~/.zshrc` |
| Gateway 启动失败 | 配置不兼容新版 | 运行 `openclaw doctor` 检查 |

---

## 8. 常见问题排查

### 8.1 模型无法使用

```bash
# 查看当前模型状态
openclaw models status

# 列出可用模型
openclaw models list

# 切换模型
/model bailian/qwen3.6-plus
```

### 8.2 认证失败

```bash
# 检查认证配置
cat ~/.openclaw/agents/main/agent/auth-profiles.json

# 检查 .env 环境变量
cat ~/.openclaw/.env
```

### 8.3 配置不生效

```bash
# 检查配置语法
openclaw doctor

# 重启 Gateway
openclaw gateway restart

# 查看配置
openclaw config show
```

### 8.4 飞书机器人离线

```bash
# 检查飞书插件状态
openclaw status

# 查看飞书相关日志
openclaw logs --follow | grep feishu
```

### 8.5 npm 安装卡住或失败

```bash
# 清理 npm 缓存
npm cache clean --force

# 使用国内镜像（如果网络慢）
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install -g openclaw@latest
```

---

## 9. 备份与恢复

### 9.1 需要备份的文件

```
~/.openclaw/
├── openclaw.json                      # 主配置（⚠️ 含敏感信息）
├── .env                               # 环境变量（⚠️ 含 API Key）
├── agents/main/agent/
│   └── auth-profiles.json             # 认证信息（⚠️ 含 API Key）
└── workspace/                         # 工作目录
    ├── AGENTS.md
    ├── SOUL.md
    ├── MEMORY.md
    ├── USER.md
    ├── TOOLS.md
    ├── HEARTBEAT.md
    └── memory/                        # 记忆文件
```

### 9.2 快速备份命令

```bash
# 备份整个 .openclaw 目录（排除 node_modules）
tar -czf openclaw-backup-$(date +%Y%m%d).tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  ~/.openclaw/
```

### 9.3 恢复

```bash
# 停止 Gateway
openclaw gateway stop

# 恢复配置
tar -xzf openclaw-backup-YYYYMMDD.tar.gz -C ~/

# 重启
openclaw gateway start
```

---

## 附录：当前完整配置模板

> ⚠️ 注意：敏感信息已用占位符替换，实际使用时请填入真实值

<details>
<summary>点击查看 openclaw.json 完整模板</summary>

```json
{
  "meta": {
    "lastTouchedVersion": "2026.4.23",
    "lastTouchedAt": "2026-04-25T13:22:54.000Z"
  },
  "auth": {
    "profiles": {
      "bailian:default": {
        "provider": "bailian",
        "mode": "api_key"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.6-plus",
            "name": "qwen3.6-plus",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.6-plus"
      },
      "models": {
        "bailian/qwen3.6-plus": {},
        "bailian/qwen3.5-plus": {}
      },
      "workspace": "/Users/YOUR_USERNAME/.openclaw/workspace",
      "compaction": {
        "mode": "safeguard"
      }
    }
  },
  "tools": {
    "profile": "coding",
    "web": {
      "search": {
        "provider": "duckduckgo"
      }
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "defaultAccount": "goldfish",
      "connectionMode": "websocket",
      "domain": "feishu",
      "accounts": {
        "goldfish": {
          "appId": "cli_YOUR_APP_ID",
          "appSecret": "YOUR_APP_SECRET",
          "name": "金鱼机器人",
          "enabled": true,
          "groupPolicy": "open",
          "requireMention": false
        }
      }
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "YOUR_GATEWAY_TOKEN"
    }
  }
}
```

</details>

---

_文档由金鱼维护，最后更新 2026-04-25_
