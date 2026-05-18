import ffmpeg
from pathlib import Path

def extract_audio(video_path: str) -> str:
    audio_path = str(Path(video_path).with_suffix(".wav"))
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, ac=1, ar="16000")
        .overwrite_output()
        .run(quiet=True)
    )
    return audio_path