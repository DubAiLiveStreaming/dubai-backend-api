import subprocess
import imageio_ffmpeg
from pathlib import Path

def extract_audio(video_path: str) -> str:
    audio_path = str(Path(video_path).with_suffix(".wav"))
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    result = subprocess.run([
        ffmpeg_exe,
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ac", "1",
        "-ar", "16000",
        "-y", audio_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Audio extract failed: {result.stderr}")
    
    return audio_path