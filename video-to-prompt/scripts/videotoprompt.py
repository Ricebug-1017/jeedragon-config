#!/usr/bin/env python3
"""
VideoToPrompt - 视频转 AI 提示词一键工具

将视频内容逆向工程为结构化的 AI 视频生成提示词。
支持 Kling（可灵）、Veo（Google）、Seedance（字节跳动）、Wan（阿里万相）。

用法:
    python videotoprompt.py <视频路径> [方案] [帧数]

方案:
    dashscope  - 百炼 qwen-vl-plus（默认）
    gemini     - Google Gemini 2.0 Flash
    ollama     - 本地 Ollama qwen2.5-vl

环境变量:
    DASHSCOPE_API_KEY  - 百炼 API Key（dashscope 方案需要）
    GEMINI_API_KEY     - Google API Key（gemini 方案需要）

示例:
    python videotoprompt.py video.mp4
    python videotoprompt.py video.mp4 dashscope 12
    python videotoprompt.py video.mp4 gemini
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
    
    # 短视频 (<10s) 特殊处理
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
    print(f"✅ {len(frame_paths)} 帧 → {output_dir}/")
    return frame_paths, duration


def analyze_with_dashscope(frame_paths):
    """使用百炼 qwen-vl-plus 分析"""
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        print("❌ 请设置环境变量 DASHSCOPE_API_KEY")
        print("   export DASHSCOPE_API_KEY='your-api-key'")
        sys.exit(1)
    
    print("🔍 使用 qwen-vl-plus 分析画面...")
    
    content = [{
        "type": "text",
        "text": """请分析这些视频截图，它们是同一个视频的不同时间点的帧。

请按时间顺序详细描述每一帧的画面内容：
1. 场景类型和主要元素（人物、物体、文字、图形）
2. 人物的动作、表情和位置关系
3. 色彩风格、光线条件和整体氛围
4. 镜头角度（远景/中景/近景/特写/俯拍/仰拍）
5. 任何文字、UI元素或品牌标识
6. 画面构图和视觉焦点

最后，请总结：
- 这段视频的整体视觉风格
- 内容主题和叙事结构
- 适合用什么风格的提示词来描述"""
    }]
    
    for path in frame_paths:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })
    
    resp = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "qwen-vl-plus",
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 4000
        },
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def analyze_with_gemini(frame_paths):
    """使用 Google Gemini 2.0 Flash 分析"""
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ 请先安装: pip install google-generativeai")
        sys.exit(1)
    
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("❌ 请设置环境变量 GEMINI_API_KEY")
        print("   export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)
    
    print("🔍 使用 Gemini 2.0 Flash 分析画面...")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    parts = [
        "请分析这些视频截图，按时间顺序详细描述每一帧的画面内容。\n"
        "包括：场景类型、主要元素、人物动作、色彩风格、镜头角度、文字UI。\n"
        "最后总结视频的整体视觉风格和内容主题。"
    ]
    
    for path in frame_paths:
        with open(path, "rb") as f:
            parts.append({
                "mime_type": "image/jpeg",
                "data": f.read()
            })
    
    response = model.generate_content(parts)
    return response.text


def analyze_with_ollama(frame_paths):
    """使用本地 Ollama qwen2.5-vl 分析"""
    print("🔍 使用 Ollama qwen2.5-vl 分析画面...")
    
    user_text = ("请分析这些视频截图，按时间顺序详细描述每一帧的画面内容。\n"
                 "包括：场景类型、主要元素、人物动作、色彩风格、镜头角度、文字UI。\n"
                 "最后总结视频的整体视觉风格和内容主题。")
    
    content = [{"type": "text", "text": user_text}]
    
    for path in frame_paths:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })
    
    resp = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5-vl",
            "messages": [{"role": "user", "content": content}],
            "stream": False
        },
        timeout=300
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def generate_prompts(analysis, duration):
    """
    基于 Vision 分析结果，生成多模型 prompt
    
    这里使用简单的模板方式。更高级的做法是让另一个 LLM
    将分析结果转换为各模型的最佳格式。
    """
    # 取分析的前800字作为摘要
    summary = analysis[:800] if len(analysis) > 800 else analysis
    
    prompts = {
        "kling": (
            f"写实风格视频，{summary}\n"
            f"视频时长约{duration:.0f}秒。4K画质，电影级调色，稳定运镜。"
        ),
        "veo": (
            f"A cinematic video. {summary}\n"
            f"Approximately {duration:.0f} seconds long. "
            f"Cinematic quality, realistic style, smooth camera movement."
        ),
        "seedance": (
            f"写实风格，{summary}\n"
            f"视频时长约{duration:.0f}秒。4K高清，电影级调色，流畅运镜。"
        ),
        "wan": (
            f"{summary}\n"
            f"视频时长约{duration:.0f}秒。高清画质，写实风格，流畅运镜。"
        )
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
    print("  🎬 VideoToPrompt - 视频转AI提示词")
    print("=" * 50)
    
    if not os.path.exists(video_path):
        print(f"❌ 文件不存在: {video_path}")
        sys.exit(1)
    
    # Step 1: 抽帧
    frame_paths, duration = extract_frames(video_path, num_frames)
    
    # Step 2: Vision 分析
    analysis = None
    if scheme == "dashscope":
        analysis = analyze_with_dashscope(frame_paths)
    elif scheme == "gemini":
        analysis = analyze_with_gemini(frame_paths)
    elif scheme == "ollama":
        analysis = analyze_with_ollama(frame_paths)
    else:
        print(f"❌ 未知方案: {scheme}（可选: dashscope, gemini, ollama）")
        sys.exit(1)
    
    print(f"\n📝 画面分析:\n{'─' * 40}")
    print(analysis)
    print(f"{'─' * 40}")
    
    # Step 3: 生成 prompt
    prompts = generate_prompts(analysis, duration)
    
    print(f"\n{'=' * 50}")
    print(f"  🎯 生成的 Prompt")
    print(f"{'=' * 50}")
    
    for model, prompt in prompts.items():
        print(f"\n🎬 {model.upper()} Prompt:")
        print(f"{'─' * 40}")
        print(prompt)
    
    # 保存到文件
    output_file = f"{os.path.splitext(video_path)[0]}_prompts.json"
    result = {
        "video": video_path,
        "duration": round(duration, 2),
        "frames": len(frame_paths),
        "analysis_scheme": scheme,
        "analysis": analysis,
        "prompts": prompts
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存: {output_file}")
    print("✅ 完成！")


if __name__ == "__main__":
    main()
