#!/usr/bin/env python3
"""
VideoToPrompt - 关键帧提取
从视频中提取关键帧，用于后续的 Vision 分析。
"""

import os
import sys
import json
from moviepy import VideoFileClip
from PIL import Image


def extract_frames(video_path, num_frames=8, output_dir=None):
    """
    从视频中提取均匀分布的关键帧
    
    Args:
        video_path: 视频文件路径
        num_frames: 提取帧数 (默认8)
        output_dir: 输出目录 (默认: 视频同级目录的 frames/ 子目录)
    
    Returns:
        dict: {frame_paths: [...], duration: float, size: [w,h], fps: float}
    """
    if not os.path.exists(video_path):
        print(json.dumps({"error": f"文件不存在: {video_path}"}))
        sys.exit(1)
    
    clip = VideoFileClip(video_path)
    duration = clip.duration
    size = clip.size
    fps = clip.fps
    
    if output_dir is None:
        base = os.path.splitext(video_path)[0]
        output_dir = f"{base}_frames"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 对于短视频 (<10s)，逐帧提取最多5帧
    if duration < 10:
        num_frames = min(num_frames, 5)
        interval = duration / (num_frames + 1)
    else:
        interval = duration / num_frames
    
    frame_paths = []
    
    for i in range(num_frames):
        if duration < 10:
            t = (i + 1) * interval  # 跳过开头和结尾
        else:
            t = i * interval
        
        frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        path = os.path.join(output_dir, f"frame_{i+1:02d}_{t:.1f}s.jpg")
        img.save(path, 'JPEG', quality=85)
        frame_paths.append(path)
    
    clip.close()
    
    result = {
        "frame_paths": frame_paths,
        "duration": round(duration, 2),
        "size": size,
        "fps": fps,
        "num_frames": len(frame_paths),
        "output_dir": output_dir
    }
    
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python extract_frames.py <video_path> [num_frames] [output_dir]")
        print("  video_path: 视频文件路径")
        print("  num_frames: 提取帧数 (默认8)")
        print("  output_dir: 输出目录 (可选)")
        sys.exit(1)
    
    video_path = sys.argv[1]
    num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    extract_frames(video_path, num_frames, output_dir)
