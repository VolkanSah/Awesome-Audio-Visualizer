# -----------------------------------------------------------------------------
# 6. Export functions - merge_video_audio (Automated)
# File: decoder.py
# -----------------------------------------------------------------------------
import argparse
import subprocess
import os
import json
from datetime import datetime

# Lade FFmpeg-Pfad aus system_report.json
def get_ffmpeg_path():
    config_file = 'system_report.json'
    if not os.path.exists(config_file):
        raise FileNotFoundError("system_report.json not found. Please run detector first.")
    with open(config_file, 'r') as f:
        data = json.load(f)
        ffmpeg_path = data.get("ffmpeg_path")
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            raise FileNotFoundError("FFmpeg path not found or invalid in system_report.json.")
        return ffmpeg_path

# Merge Video + Audio
def merge_video_audio(video_path, audio_path, output_path=None):
    if not os.path.exists(video_path):
        return {"status": "error", "message": f"Video file not found: {video_path}"}
    if not os.path.exists(audio_path):
        return {"status": "error", "message": f"Audio file not found: {audio_path}"}

    ffmpeg_path = get_ffmpeg_path()

    # Default Output-Pfad
    if not output_path:
        base, _ = os.path.splitext(video_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{base}_merged_{timestamp}.mp4"

    command = [
        ffmpeg_path,
        '-y',  # overwrite
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {"status": "success", "output": output_path}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"FFmpeg failed: {e}"}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merge a video and an audio file using FFmpeg.")
    parser.add_argument('video_path', help="Path to the video file.")
    parser.add_argument('audio_path', help="Path to the audio file.")
    parser.add_argument('--output', help="Optional: Path for the merged output file.")

    args = parser.parse_args()
    result = merge_video_audio(args.video_path, args.audio_path, args.output)
    print(result)
