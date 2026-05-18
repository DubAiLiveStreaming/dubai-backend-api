import subprocess
import os
from pathlib import Path

def extract_audio(video_path: str) -> str:
    audio_path = str(Path(video_path).with_suffix(".wav"))
    
    # Try different ffmpeg locations
    ffmpeg_paths = [
        "ffmpeg",
        "/usr/bin/ffmpeg", 
        "/usr/local/bin/ffmpeg",
    ]
    
    try:
        import imageio_ffmpeg
        ffmpeg_paths.insert(0, imageio_ffmpeg.get_ffmpeg_exe())
    except:
        pass
    
    for ffmpeg_exe in ffmpeg_paths:
        try:
            subprocess.run([
                ffmpeg_exe, "-i", video_path,
                "-ac", "1", "-ar", "16000",
                "-y", audio_path
            ], check=True, capture_output=True)
            return audio_path
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    
    raise RuntimeError("ffmpeg not found anywhere")