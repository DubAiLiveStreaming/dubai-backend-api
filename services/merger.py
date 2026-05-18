import subprocess
import imageio_ffmpeg
from pathlib import Path

def merge_audio_video(video_path: str, audio_path: str, job_id: str, temp_dir: Path) -> str:
    output_path = str(temp_dir / f"{job_id}_dubbed.mp4")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Get video duration
    import json
    probe = subprocess.run([
        ffmpeg_exe.replace("ffmpeg", "ffprobe"),
        "-v", "quiet", "-print_format", "json",
        "-show_format", video_path
    ], capture_output=True, text=True)
    
    try:
        video_duration = float(json.loads(probe.stdout)["format"]["duration"])
    except:
        video_duration = None

    # Merge — trim audio to video length
    cmd = [
        ffmpeg_exe,
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v",
        "-map", "1:a",
        "-vcodec", "copy",
        "-acodec", "aac",
        "-shortest",  # audio = video length
        "-y", output_path
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return output_path