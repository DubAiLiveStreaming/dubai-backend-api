import subprocess
import imageio_ffmpeg
from pathlib import Path

def extract_audio(video_path: str) -> str:
    audio_path = str(Path(video_path).with_suffix(".wav"))
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_exe, "-i", video_path,
        "-ac", "1", "-ar", "16000",
        "-y", audio_path
    ], check=True)
    return audio_path