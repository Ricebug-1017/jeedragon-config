---
name: video-to-prompt
description: Extract key frames from videos and generate structured prompts for AI video generators (Kling, Veo, Seedance, Wan). Supports local files and YouTube URLs.
author: 金鱼
created: 2026-04-30
---

# VideoToPrompt 技能

将视频内容逆向工程为结构化的 AI 视频生成提示词。

## 功能

- 🎬 从本地视频文件提取关键帧
- 📺 支持 YouTube 链接（自动下载后分析）
- 🖼️ 使用 Vision 模型分析画面内容
- 📝 生成适用于主流视频 AI 的 prompt：
  - **Kling**（可灵）
  - **Veo**（Google）
  - **Seedance**（字节跳动）
  - **Wan**（阿里万相）

## 使用方式

```
帮我分析这个视频并生成 prompt：/path/to/video.mp4
分析视频生成 Kling prompt：douyin_79110.mp4
把这段 YouTube 视频转成 prompt：https://youtube.com/watch?v=xxx
```

## 工作原理

1. **抽帧**：使用 moviepy 从视频中均匀提取 N 张关键帧
2. **视觉分析**：将帧发送给 Vision 模型，获取详细画面描述
3. **Prompt 生成**：基于分析结果，生成优化后的视频生成 prompt

## 脚本

- `scripts/extract_frames.py` — 从视频提取关键帧
- `scripts/videotoprompt.py` — 主脚本，协调抽帧+分析+生成

## 依赖

- Python 3.9+
- moviepy (`pip install moviepy`)
- PIL/Pillow
- 可用的 Vision 模型（通过 image 工具）
