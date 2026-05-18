import subprocess
import imageio_ffmpeg
import json
from pathlib import Path

def merge_audio_video(video_path: str, audio_path: str, job_id: str, temp_dir: Path) -> str:
    output_path = str(temp_dir / f"{job_id}_dubbed.mp4")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Extract background music from original video (lower volume)
    bg_path = str(temp_dir / f"{job_id}_bg.wav")
    subprocess.run([
        ffmpeg_exe,
        "-i", video_path,
        "-af", "volume=0.15",  # background music 15% volume
        "-ar", "44100", "-ac", "2",
        "-y", bg_path
    ], capture_output=True)

    # Mix background + dubbed voice
    mixed_path = str(temp_dir / f"{job_id}_mixed.wav")
    subprocess.run([
        ffmpeg_exe,
        "-i", bg_path,
        "-i", audio_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest:weights=1 3[aout]",
        "-map", "[aout]",
        "-ar", "44100",
        "-y", mixed_path
    ], capture_output=True)

    # Merge mixed audio + video
    subprocess.run([
        ffmpeg_exe,
        "-i", video_path,
        "-i", mixed_path,
        "-map", "0:v",
        "-map", "1:a",
        "-vcodec", "copy",
        "-acodec", "aac",
        "-shortest",
        "-y", output_path
    ], capture_output=True, check=True)

    return output_path