# VideoToPrompt - 视频转 AI 提示词生成工具

> 将任意视频内容逆向工程为结构化的 AI 视频生成提示词，支持 Kling（可灵）、Veo（Google）、Seedance（字节跳动）、Wan（阿里万相）等主流视频生成模型。

---

## 📋 目录

1. [项目概述](#项目概述)
2. [工作原理](#工作原理)
3. [环境准备](#环境准备)
4. [核心脚本](#核心脚本)
5. [Vision 分析方案](#vision-分析方案)
6. [Prompt 生成模板](#prompt-生成模板)
7. [完整使用流程](#完整使用流程)
8. [故障排除](#故障排除)

---

## 项目概述

### 这是什么？

VideoToPrompt 是一个将视频内容"翻译"成 AI 可理解的提示词的工具。

**输入**：任意视频文件（MP4、MOV 等）  
**输出**：可直接用于 AI 视频生成模型的 prompt

### 应用场景

- 看到一段精彩的视频，想用 AI 生成类似内容
- 将真实拍摄的视频转为 prompt，用 AI 重新演绎
- 分析优秀视频作品的画面结构，学习分镜技巧
- 批量将视频素材库转为可复用的 prompt 资源

---

## 工作原理

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  视频文件    │ ──▶ │  关键帧抽取  │ ──▶ │ Vision 视觉   │ ──▶ │  Prompt 生成  │
│  (MP4/MOV)  │     │  (moviepy)  │     │  分析画面     │     │  (Kling/Veo │
│             │     │             │     │  (qwen-vl等)  │     │  Seedance)  │
└─────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
```

### 三步流程

1. **抽帧**：使用 moviepy 从视频中均匀提取 N 张关键帧（JPG）
2. **分析**：将帧图片发送给 Vision 模型，获取详细的画面描述
3. **生成**：基于分析结果，按目标模型的格式生成优化后的 prompt

---

## 环境准备

### 基础依赖

#### Windows 环境

```powershell
# 1. 安装 Python 3.9+（建议 3.10+）
# 从 https://www.python.org/downloads/ 下载，安装时勾选 "Add to PATH"

# 2. 验证安装
python --version
pip --version

# 3. 安装核心库
pip install moviepy Pillow requests
```

#### macOS 环境

```bash
# 使用 Homebrew 安装 Python（如未安装）
brew install python@3.11

# 安装核心库
pip3 install moviepy Pillow requests
```

### 依赖库说明

| 库 | 用途 | 安装命令 |
|---|---|---|
| moviepy | 视频读取、帧提取 | `pip install moviepy` |
| Pillow | 图片保存为 JPG | `pip install Pillow` |
| requests | HTTP 请求（调用 API） | `pip install requests` |

---

## 核心脚本

### 脚本 1：extract_frames.py - 关键帧提取

```python
#!/usr/bin/env python3
"""
VideoToPrompt - 关键帧提取
从视频中提取关键帧，用于后续的 Vision 分析。

用法:
    python extract_frames.py <视频路径> [帧数] [输出目录]

示例:
    python extract_frames.py video.mp4 8
    python extract_frames.py video.mp4 12 ./my_frames
"""

import os
import sys
import json
from moviepy import VideoFileClip
from PIL import Image


def extract_frames(video_path, num_frames=8, output_dir=None):
    """
    从视频中提取均匀分布的关键帧
    
    参数:
        video_path: 视频文件路径
        num_frames: 提取帧数 (默认8)
        output_dir: 输出目录 (默认: 视频同级目录的 frames/ 子目录)
    
    返回:
        dict: {frame_paths, duration, size, fps, num_frames, output_dir}
    """
    if not os.path.exists(video_path):
        print(json.dumps({"error": f"文件不存在: {video_path}"}))
        sys.exit(1)
    
    print(f"📹 正在读取视频: {video_path}")
    clip = VideoFileClip(video_path)
    duration = clip.duration
    size = clip.size
    fps = clip.fps
    
    if output_dir is None:
        base = os.path.splitext(video_path)[0]
        output_dir = f"{base}_frames"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 短视频 (<10s) 逐帧提取最多5帧
    if duration < 10:
        num_frames = min(num_frames, 5)
        interval = duration / (num_frames + 1)
    else:
        interval = duration / num_frames
    
    frame_paths = []
    
    for i in range(num_frames):
        if duration < 10:
            t = (i + 1) * interval
        else:
            t = i * interval
        
        frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        path = os.path.join(output_dir, f"frame_{i+1:02d}_{t:.1f}s.jpg")
        img.save(path, 'JPEG', quality=85)
        frame_paths.append(path)
        print(f"  ✓ 帧 {i+1}/{num_frames} - {t:.1f}s")
    
    clip.close()
    
    result = {
        "frame_paths": frame_paths,
        "duration": round(duration, 2),
        "size": size,
        "fps": fps,
        "num_frames": len(frame_paths),
        "output_dir": output_dir
    }
    
    print(f"\n✅ 提取完成! {len(frame_paths)} 帧 → {output_dir}/")
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    video_path = sys.argv[1]
    num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    extract_frames(video_path, num_frames, output_dir)
```

**使用方式**：

```bash
# 基本用法 - 提取8帧
python extract_frames.py video.mp4

# 自定义帧数
python extract_frames.py video.mp4 12

# 指定输出目录
python extract_frames.py video.mp4 8 ./output_frames
```

---

## Vision 分析方案

抽帧之后，需要 AI "看懂"这些图片。以下是几种可选方案：

### 方案 A：百炼 DashScope qwen-vl-plus（推荐，国内稳定）

**优点**：免费额度充足、国内访问稳定、中文理解好  
**缺点**：需要注册阿里云账号

```python
"""
方案 A: 使用百炼 DashScope qwen-vl-plus 分析视频帧

配置步骤:
1. 访问 https://bailian.console.aliyun.com/
2. 开通「模型服务」
3. 创建 API Key（注意：需要标准 Key，不是 Coding Plan Key）
4. 将 Key 填入下方 api_key 变量或环境变量
"""

import requests
import base64

DASHSCOPE_API_KEY = "你的百炼标准API Key"  # 或设置环境变量 DASHSCOPE_API_KEY

def analyze_frames_with_qwen_vl(frame_paths, api_key=None):
    """
    使用 qwen-vl-plus 分析多张视频帧
    """
    api_key = api_key or DASHSCOPE_API_KEY
    
    # 构建消息内容
    content = []
    
    # 添加文本 prompt
    content.append({
        "type": "text",
        "text": """请仔细分析这些视频截图，它们是同一个视频的不同时间点的帧。

请按时间顺序详细描述每一帧的画面内容，包括：
1. 场景类型（室内/室外/办公室/自然风景等）
2. 画面中的主要元素（人物、物体、文字、图形等）
3. 人物的动作和表情（如果有）
4. 色彩风格和光线条件
5. 镜头角度（远景/中景/近景/特写）
6. 任何文字或 UI 元素
7. 画面的整体氛围和情绪

最后，请总结这段视频的整体视觉风格、内容主题和叙事节奏。"""
    })
    
    # 添加图片
    for path in frame_paths:
        with open(path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })
    
    # 调用 API
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-vl-plus",
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 4000
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    
    return result["choices"][0]["message"]["content"]
```

### 方案 B：Google Gemini 2.0 Flash（免费额度大）

**优点**：每天 1500 次免费请求、支持多模态  
**缺点**：需要 Google 账号

```python
"""
方案 B: 使用 Google Gemini 2.0 Flash 分析视频帧

配置步骤:
1. 访问 https://aistudio.google.com/apikey
2. 创建 API Key
3. 设置环境变量 GEMINI_API_KEY
"""

import google.generativeai as genai

def analyze_frames_with_gemini(frame_paths):
    """使用 Gemini 2.0 Flash 分析视频帧"""
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    parts = [
        "请仔细分析这些视频截图，它们是同一个视频的不同时间点的帧。\n\n"
        "请按时间顺序详细描述每一帧的画面内容，包括场景、主要元素、色彩风格、"
        "镜头角度、任何文字或UI元素。\n\n"
        "最后总结这段视频的整体视觉风格和内容主题。"
    ]
    
    for path in frame_paths:
        with open(path, "rb") as f:
            image_data = f.read()
        parts.append({
            "mime_type": "image/jpeg",
            "data": image_data
        })
    
    response = model.generate_content(parts)
    return response.text
```

### 方案 C：Ollama 本地运行（完全免费，无需网络）

**优点**：完全免费、数据不出本地、隐私好  
**缺点**：需要较高配置（建议 16GB+ 内存）

```powershell
# Windows PowerShell 安装步骤

# 1. 下载安装包
# 访问 https://ollama.com/download 下载 Windows 版本

# 2. 安装后启动
ollama serve

# 3. 下载视觉模型（另一个终端）
ollama pull qwen2.5-vl
```

```python
"""
方案 C: 使用 Ollama 本地 qwen2.5-vl 分析视频帧
"""

import requests

def analyze_frames_with_ollama(frame_paths):
    """使用本地 Ollama qwen2.5-vl 分析视频帧"""
    
    import base64
    
    messages = {
        "model": "qwen2.5-vl",
        "messages": []
    }
    
    user_content = "请仔细分析这些视频截图，按时间顺序描述每一帧的画面内容，" \
                   "包括场景、主要元素、色彩风格、镜头角度。" \
                   "最后总结这段视频的整体视觉风格和内容主题。"
    
    content = [{"type": "text", "text": user_content}]
    
    for path in frame_paths:
        with open(path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
        })
    
    messages["messages"].append({"role": "user", "content": content})
    
    resp = requests.post(
        "http://localhost:11434/api/chat",
        json=messages,
        timeout=120
    )
    
    return resp.json()["message"]["content"]
```

---

## Prompt 生成模板

拿到画面描述后，按不同视频生成模型的格式输出 prompt：

### Kling（可灵）格式

```
[镜头] [场景描述] [主体动作] [环境细节] [光影效果] [情绪氛围]

示例:
中景镜头，一个现代化办公室内，穿着深色西装的男性站在白色投影幕前，
幕上显示着流程图和文字。温暖的顶灯照亮房间，左侧有窗户透进自然光。
整体色调偏暖，专业而沉稳的氛围。4K画质，电影级调色。
```

### Veo（Google）格式

```
A [shot_type] of [subject] [action] in [setting]. 
[Lighting details]. [Color grading]. [Mood/atmosphere]. 
Cinematic quality, [style].

示例:
A medium shot of a man in a dark suit standing in front of a white 
projection screen displaying flowcharts and text in a modern office. 
Warm overhead lighting with natural light from a left-side window. 
Warm color palette, professional atmosphere. Cinematic quality, 
realistic style.
```

### Seedance（字节跳动）格式

```
[画面风格] [主体] [动作] [场景] [细节] [技术参数]

示例:
写实风格，一名穿西装的男性在现代办公室内进行演示，背后是显示流程图的
投影幕。温暖的灯光和自然采光混合，4K高清，电影级调色，稳定运镜。
```

### Wan（阿里万相）格式

```
[主体描述]，[动作/状态]，[环境/场景]，[光线/色彩]，[风格/画质]

示例:
身穿深色西装的男性，站在投影幕前做演示，现代化办公室环境，
温暖顶灯搭配侧面自然光，写实风格，高清画质。
```

### 自动生成脚本

```python
"""
基于 Vision 分析结果，自动生成多模型 prompt
"""

def generate_prompts(vision_analysis):
    """
    将 Vision 分析结果转换为多模型 prompt
    
    参数:
        vision_analysis: Vision 模型输出的画面描述文本
    
    返回:
        dict: {kling: str, veo: str, seedance: str, wan: str}
    """
    
    # 这里可以加入 LLM 转换逻辑，让另一个模型将中文描述
    # 转换为各模型的最佳 prompt 格式
    
    # 简单版本：直接使用分析结果
    prompts = {
        "kling": f"写实风格视频，{vision_analysis}",
        "veo": f"A cinematic video. {vision_analysis}",
        "seedance": f"写实风格，{vision_analysis}",
        "wan": f"{vision_analysis}，高清画质，写实风格"
    }
    
    return prompts
```

---

## 完整使用流程

### 一站式脚本：videotoprompt.py

```python
#!/usr/bin/env python3
"""
VideoToPrompt - 视频转 Prompt 一键工具

用法:
    python videotoprompt.py <视频路径> [方案] [帧数]

方案:
    dashscope  - 百炼 qwen-vl-plus（默认）
    gemini     - Google Gemini 2.0 Flash
    ollama     - 本地 Ollama

环境变量:
    DASHSCOPE_API_KEY  - 百炼 API Key
    GEMINI_API_KEY     - Google API Key

示例:
    python videotoprompt.py video.mp4
    python videotoprompt.py video.mp4 gemini 12
    python videotoprompt.py video.mp4 ollama
"""

import os
import sys
import json
import base64
import requests
from moviepy import VideoFileClip
from PIL import Image


def extract_frames(video_path, num_frames=8):
    """提取关键帧"""
    print(f"📹 提取关键帧: {video_path}")
    clip = VideoFileClip(video_path)
    duration = clip.duration
    output_dir = f"{os.path.splitext(video_path)[0]}_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    interval = duration / num_frames
    frame_paths = []
    
    for i in range(num_frames):
        t = i * interval
        frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        path = os.path.join(output_dir, f"frame_{i+1:02d}_{t:.1f}s.jpg")
        img.save(path, 'JPEG', quality=85)
        frame_paths.append(path)
    
    clip.close()
    print(f"✅ {len(frame_paths)} 帧 → {output_dir}/")
    return frame_paths, duration


def analyze_with_dashscope(frame_paths):
    """使用百炼 qwen-vl-plus 分析"""
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        print("❌ 请设置环境变量 DASHSCOPE_API_KEY")
        sys.exit(1)
    
    print("🔍 使用 qwen-vl-plus 分析画面...")
    
    content = [{
        "type": "text",
        "text": """请分析这些视频截图，按时间顺序描述每一帧：
1. 场景类型和主要元素
2. 人物动作和表情
3. 色彩风格和光线
4. 镜头角度
5. 任何文字或UI元素
最后总结视频的整体视觉风格和内容主题。"""
    }]
    
    for path in frame_paths:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    
    resp = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "qwen-vl-plus", "messages": [{"role": "user", "content": content}], "max_tokens": 4000},
        timeout=60
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def generate_prompts(analysis, duration):
    """生成多模型 prompt"""
    summary = analysis[:500] if len(analysis) > 500 else analysis
    
    prompts = {
        "kling": f"写实风格视频，{summary}。4K画质，电影级调色，稳定运镜。",
        "veo": f"A cinematic video. {summary}. Cinematic quality, realistic style.",
        "seedance": f"写实风格，{summary}。4K高清，电影级调色，稳定运镜。",
        "wan": f"{summary}，高清画质，写实风格，流畅运镜。"
    }
    
    return prompts


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    video_path = sys.argv[1]
    scheme = sys.argv[2] if len(sys.argv) > 2 else "dashscope"
    num_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    
    print("=" * 50)
    print("  VideoToPrompt - 视频转AI提示词")
    print("=" * 50)
    
    # Step 1: 抽帧
    frame_paths, duration = extract_frames(video_path, num_frames)
    
    # Step 2: Vision 分析
    if scheme == "dashscope":
        analysis = analyze_with_dashscope(frame_paths)
    elif scheme == "gemini":
        print("⚠️  Gemini 方案请自行补充代码（见文档方案B）")
        sys.exit(1)
    elif scheme == "ollama":
        print("⚠️  Ollama 方案请自行补充代码（见文档方案C）")
        sys.exit(1)
    else:
        print(f"❌ 未知方案: {scheme}")
        sys.exit(1)
    
    print(f"\n📝 画面分析:\n{analysis}\n")
    
    # Step 3: 生成 prompt
    prompts = generate_prompts(analysis, duration)
    
    print("=" * 50)
    print("  生成的 Prompt")
    print("=" * 50)
    
    for model, prompt in prompts.items():
        print(f"\n🎬 {model.upper()} Prompt:")
        print("-" * 40)
        print(prompt)
    
    # 保存到文件
    output_file = f"{os.path.splitext(video_path)[0]}_prompts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "video": video_path,
            "duration": duration,
            "analysis": analysis,
            "prompts": prompts
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存: {output_file}")


if __name__ == "__main__":
    main()
```

---

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| `moviepy not found` | 未安装 | `pip install moviepy` |
| `ffmpeg not found` | moviepy 需要 ffmpeg | `pip install imageio-ffmpeg` |
| `SSL_ERROR_SYSCALL` | 网络问题 | 检查网络/代理设置 |
| `Invalid API key` | Key 错误 | 确认使用正确的 Key 类型 |
| `Connection timeout` | 防火墙/网络 | 检查网络连通性 |
| 帧提取慢 | 视频太大 | 减少帧数或降低分辨率 |

### ffmpeg 安装（moviepy 依赖）

```bash
# Windows - 方式1: pip 安装自带 ffmpeg
pip install imageio-ffmpeg

# Windows - 方式2: 手动安装
# 访问 https://ffmpeg.org/download.html 下载
# 解压后将 ffmpeg.exe 所在目录加入 PATH

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### 网络问题（国内访问 GitHub 困难）

```powershell
# Windows PowerShell - 设置代理（如果你有代理）
$env:HTTPS_PROXY="http://127.0.0.1:7890"
$env:HTTP_PROXY="http://127.0.0.1:7890"

# 或使用国内镜像
pip install moviepy -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Ollama Windows 安装

1. 访问 https://ollama.com/download 下载 Windows 安装包
2. 双击安装，完成后在终端验证：
   ```powershell
   ollama --version
   ollama serve
   ```
3. 在另一个终端下载模型：
   ```powershell
   ollama pull qwen2.5-vl
   ```

---

## 项目文件结构

```
video-to-prompt/
├── README.md                      ← 本文件
├── scripts/
│   ├── extract_frames.py          ← 帧提取脚本
│   └── videotoprompt.py           ← 一键转换脚本（待创建）
├── examples/
│   └── douyin_hermes/             ← 示例（Hermes 抖音视频）
│       ├── douyin_79110.mp4
│       └── douyin_79110_frames/
│           ├── frame_01_0.0s.jpg
│           ├── frame_02_46.9s.jpg
│           └── ...
└── output/
    └── douyin_79110_prompts.json  ← 生成的 prompt
```

---

## 许可证

MIT

---

> 本工具仅用于学习和个人用途。使用 AI 生成内容时请遵守相关平台的使用条款。
