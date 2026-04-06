# OpenClaw 模型配置指南

适用于 Windows/macOS/Linux 全平台

---

## 📁 配置文件位置

```
~/.openclaw/openclaw.json
```

Windows 路径示例：
```
C:\Users\<你的用户名>\.openclaw\openclaw.json
```

---

## 🔑 完整配置模板

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.23-2",
    "lastTouchedAt": "2026-03-26T03:23:42.923Z"
  },
  "auth": {
    "profiles": {
      "modelstudio:default": {
        "provider": "modelstudio",
        "mode": "api_key",
        "apiKey": "你的_API_KEY_这里"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "modelstudio": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "api": "openai-compat",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus",
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
          },
          {
            "id": "qwen3-max-2026-01-23",
            "name": "qwen3-max-2026-01-23",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-coder-next",
            "name": "qwen3-coder-next",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-coder-plus",
            "name": "qwen3-coder-plus",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "MiniMax-M2.5",
            "name": "MiniMax-M2.5",
            "reasoning": true,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "glm-5",
            "name": "glm-5",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 202752,
            "maxTokens": 16384
          },
          {
            "id": "glm-4.7",
            "name": "glm-4.7",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 202752,
            "maxTokens": 16384
          },
          {
            "id": "kimi-k2.5",
            "name": "kimi-k2.5",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 32768
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
        },
        "modelstudio/qwen3-max-2026-01-23": {},
        "modelstudio/qwen3-coder-next": {},
        "modelstudio/qwen3-coder-plus": {},
        "modelstudio/MiniMax-M2.5": {},
        "modelstudio/glm-5": {},
        "modelstudio/glm-4.7": {},
        "modelstudio/kimi-k2.5": {}
      },
      "workspace": "C:\\Users\\<你的用户名>\\.openclaw\\workspace",
      "compaction": {
        "mode": "safeguard"
      }
    }
  },
  "tools": {
    "profile": "coding",
    "web": {
      "search": {
        "provider": "searxng"
      }
    }
  },
  "plugins": {
    "entries": {
      "searxng": {
        "enabled": true,
        "config": {
          "baseUrl": "https://searx.be"
        }
      },
      "modelstudio": {
        "enabled": true
      },
      "feishu": {
        "enabled": true
      }
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  },
  "session": {
    "dmScope": "per-channel-peer"
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "自动生成或手动设置"
    },
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    }
  }
}
```

---

## ✅ 关键配置项说明

### 1. API Key 配置（必须）

在 `auth.profiles.modelstudio:default` 中添加你的 API Key：

```json
"auth": {
  "profiles": {
    "modelstudio:default": {
      "provider": "modelstudio",
      "mode": "api_key",
      "apiKey": "sk-xxxxxxxxxxxxxxxx"
    }
  }
}
```

**获取 API Key**: 前往阿里云百炼平台申请

---

### 2. 模型服务地址（必须）

```json
"models": {
  "providers": {
    "modelstudio": {
      "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
      "api": "openai-compat"
    }
  }
}
```

⚠️ **常见错误**: baseUrl 写错会导致连接失败

---

### 3. 默认模型（必须）

```json
"agents": {
  "defaults": {
    "model": "modelstudio/qwen3.5-plus"
  }
}
```

推荐模型：
- `modelstudio/qwen3.5-plus` - 通用对话（推荐）
- `modelstudio/qwen3-coder-plus` - 代码专用
- `modelstudio/MiniMax-M2.5` - 推理能力强

---

### 4. 插件启用（必须）

```json
"plugins": {
  "entries": {
    "modelstudio": {
      "enabled": true
    }
  }
}
```

⚠️ 如果 `enabled: false`，模型将无法使用

---

### 5. Workspace 路径（Windows 特别注意）

Windows 路径需要使用双反斜杠或正斜杠：

```json
"workspace": "C:\\Users\\YourName\\.openclaw\\workspace"
```

或

```json
"workspace": "C:/Users/YourName/.openclaw/workspace"
```

---

## 🔧 验证配置

配置完成后，运行以下命令验证：

```bash
openclaw status
```

检查输出中是否包含：
- ✅ modelstudio 插件已启用
- ✅ 默认模型已设置
- ✅ Gateway 正常运行

---

## ❌ 常见错误排查

### 错误 1: 模型无法连接
```
原因：baseUrl 错误或 API Key 无效
解决：检查 baseUrl 是否为 https://coding.dashscope.aliyuncs.com/v1
```

### 错误 2: 插件未启用
```
原因：plugins.entries.modelstudio.enabled 为 false
解决：改为 true 并重启 OpenClaw
```

### 错误 3: 默认模型不存在
```
原因：agents.defaults.model 指向不存在的模型
解决：改为 modelstudio/qwen3.5-plus
```

### 错误 4: Windows 路径错误
```
原因：使用了单反斜杠 \ 导致转义问题
解决：使用双反斜杠 \\ 或正斜杠 /
```

---

## 📝 快速配置步骤（Windows）

1. 打开 `%USERPROFILE%\.openclaw\openclaw.json`
2. 复制上方完整配置模板
3. 替换以下占位符：
   - `你的_API_KEY_这里` → 你的实际 API Key
   - `<你的用户名>` → 你的 Windows 用户名
4. 保存文件
5. 重启 OpenClaw Gateway：
   ```bash
   openclaw gateway restart
   ```
6. 验证：
   ```bash
   openclaw status
   ```

---

## 📚 参考链接

- OpenClaw 官方文档：https://docs.openclaw.ai
- 阿里云百炼平台：https://bailian.console.aliyun.com/
- GitHub 仓库：https://github.com/openclaw/openclaw

---

_最后更新：2026-04-06_
_配置版本：OpenClaw 2026.3.23-2_
