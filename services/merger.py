import ffmpeg
from pathlib import Path

def merge_audio_video(video_path: str, audio_path: str, job_id: str, temp_dir: Path) -> str:
    output_path = str(temp_dir / f"{job_id}_dubbed.mp4")
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)
    (
        ffmpeg
        .output(
            video.video,
            audio.audio,
            output_path,
            vcodec="copy",
            acodec="aac",
            strict="experimental"
        )
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path