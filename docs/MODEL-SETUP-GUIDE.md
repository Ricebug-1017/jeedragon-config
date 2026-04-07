# OpenClaw 模型配置指南

> 完整步骤指南 - 适用于 Windows/trae 配置

---

## 📋 目录

1. [快速开始](#快速开始)
2. [配置文件位置](#配置文件位置)
3. [模型配置详解](#模型配置详解)
4. [常用命令](#常用命令)
5. [故障排查](#故障排查)

---

## 🚀 快速开始

### 方法一：使用配置向导（推荐）

```bash
# 运行交互式配置向导
openclaw onboard

# 或
openclaw config wizard
```

### 方法二：手动配置

编辑配置文件 `~/.openclaw/openclaw.json`

---

## 📁 配置文件位置

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| `~/.openclaw/openclaw.json` | JSON | 主配置文件 |
| `~/.openclaw/.env` | dotenv | 环境变量（API 密钥） |
| `~/.openclaw/agents/main/agent/models.json` | JSON | Agent 级别模型配置 |
| `~/.openclaw/agents/main/agent/auth-profiles.json` | JSON | 认证配置 |

---

## 🤖 模型配置详解

### 1. 主配置文件结构 (`openclaw.json`)

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "modelstudio": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus",
            "reasoning": false,
            "input": ["text", "image"],
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "modelstudio/qwen3.5-plus",
      "models": {
        "modelstudio/qwen3.5-plus": {
          "alias": "Qwen"
        }
      }
    }
  }
}
```

### 2. 模型引用格式

- **完整格式**: `provider/model-id`
- **示例**: `modelstudio/qwen3.5-plus`
- **别名**: 可在配置中设置简短别名

### 3. 支持的模型参数

```json
{
  "agents": {
    "defaults": {
      "models": {
        "modelstudio/qwen3.5-plus": {
          "alias": "Qwen",
          "params": {
            "temperature": 0.7,
            "maxTokens": 8192,
            "cacheControlTtl": "1h"
          }
        }
      }
    }
  }
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `alias` | string | 模型别名 |
| `temperature` | number | 随机度 (0-2) |
| `maxTokens` | number | 最大输出 token 数 |
| `cacheControlTtl` | string | 缓存有效期 |

### 4. 配置回退模型

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "modelstudio/qwen3.5-plus",
        "fallbacks": [
          "modelstudio/qwen3-max-2026-01-23",
          "modelstudio/MiniMax-M2.5"
        ]
      }
    }
  }
}
```

---

## 🔧 常用命令

### 查看模型状态

```bash
# 查看当前模型配置
openclaw models status

# 列出所有可用模型
openclaw models list

# 查看模型详情（含认证状态）
openclaw models status --plain
```

### 切换模型

```bash
# 交互式选择模型
/model

# 列出可选模型
/model list

# 直接指定模型
/model modelstudio/qwen3.5-plus

# 查看当前会话模型状态
/model status
```

### 配置模型

```bash
# 设置主模型
openclaw models set modelstudio/qwen3.5-plus

# 设置图像模型
openclaw models set-image modelstudio/qwen3.5-plus

# 添加回退模型
openclaw models fallbacks add modelstudio/MiniMax-M2.5

# 移除回退模型
openclaw models fallbacks remove modelstudio/MiniMax-M2.5

# 清空回退列表
openclaw models fallbacks clear
```

### 配置别名

```bash
# 列出别名
openclaw models aliases list

# 添加别名
openclaw models aliases add Qwen modelstudio/qwen3.5-plus

# 移除别名
openclaw models aliases remove Qwen
```

### 配置命令（直接修改配置）

```bash
# 查看当前配置
openclaw config show

# 设置主模型
openclaw config set agents.defaults.model.primary "modelstudio/qwen3.5-plus"

# 设置回退模型
openclaw config set agents.defaults.model.fallbacks '["modelstudio/MiniMax-M2.5"]'
```

---

## 🔐 API 密钥配置

### 方法一：环境变量（推荐）

创建 `~/.openclaw/.env` 文件：

```bash
# .env 文件
MODELSTUDIO_API_KEY=sk-your-api-key-here
```

在 `openclaw.json` 中引用：

```json
{
  "models": {
    "providers": {
      "modelstudio": {
        "apiKey": "${MODELSTUDIO_API_KEY}"
      }
    }
  }
}
```

### 方法二：直接配置

```json
{
  "models": {
    "providers": {
      "modelstudio": {
        "apiKey": "sk-your-api-key-here"
      }
    }
  }
}
```

> ⚠️ 安全提示：不要将含 API 密钥的配置文件提交到 Git

---

## 🛠️ 故障排查

### 常见问题

#### 1. 模型无法使用

```bash
# 检查模型是否在允许列表中
openclaw models list

# 如果模型不在列表中，添加到配置：
# 编辑 ~/.openclaw/openclaw.json，在 agents.defaults.models 中添加
```

#### 2. 认证失败

```bash
# 检查认证状态
openclaw models status

# 查看 auth-profiles.json
cat ~/.openclaw/agents/main/agent/auth-profiles.json
```

#### 3. 配置不生效

```bash
# 重启 Gateway
openclaw gateway restart

# 验证配置
openclaw doctor
```

#### 4. "Model not allowed" 错误

当 `agents.defaults.models` 设置了允许列表时，只有列表中的模型可用。

**解决方案**：
- 添加模型到允许列表
- 或移除 `agents.defaults.models` 配置

---

## 📝 Windows/trae 配置步骤

### 步骤 1：安装 OpenClaw

```powershell
# PowerShell
npm install -g openclaw
```

### 步骤 2：初始化配置

```powershell
# 运行配置向导
openclaw onboard
```

### 步骤 3：配置模型

```powershell
# 编辑配置文件
notepad $env:USERPROFILE\.openclaw\openclaw.json

# 或使用命令
openclaw config set agents.defaults.model.primary "modelstudio/qwen3.5-plus"
```

### 步骤 4：配置 API 密钥

```powershell
# 创建 .env 文件
notepad $env:USERPROFILE\.openclaw\.env

# 添加 API 密钥
MODELSTUDIO_API_KEY=sk-your-key-here
```

### 步骤 5：启动 Gateway

```powershell
# 启动服务
openclaw gateway start

# 检查状态
openclaw gateway status
```

### 步骤 6：验证配置

```powershell
# 测试模型
openclaw models status

# 发送测试消息
# （通过配置的渠道，如飞书、Telegram 等）
```

---

## 📚 参考链接

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [模型配置概念](https://open-claw.bot/docs/concepts/models/)
- [配置参考](https://www.getopenclaw.ai/docs/configuration)
- [GitHub 仓库](https://github.com/openclaw/openclaw)

---

_最后更新：2026-04-07_
