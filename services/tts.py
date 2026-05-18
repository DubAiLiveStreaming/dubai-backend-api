import asyncio
from pathlib import Path
from gtts import gTTS
import ffmpeg

async def generate_tts(segments: list, job_id: str, temp_dir: Path) -> str:
    loop = asyncio.get_event_loop()
    audio_parts = []

    for i, seg in enumerate(segments):
        part_path = str(temp_dir / f"{job_id}_part{i}.mp3")
        text = seg["text"]

        def make_tts(t=text, p=part_path):
            gTTS(text=t, lang="ta").save(p)

        await loop.run_in_executor(None, make_tts)
        audio_parts.append((seg["start"], seg["end"], part_path))

    merged_path = str(temp_dir / f"{job_id}_tts.mp3")
    inputs = [ffmpeg.input(p) for _, _, p in audio_parts]

    if len(inputs) == 1:
        ffmpeg.output(inputs[0], merged_path).overwrite_output().run(quiet=True)
    else:
        joined = ffmpeg.concat(*inputs, v=0, a=1)
        ffmpeg.output(joined, merged_path).overwrite_output().run(quiet=True)

    return merged_path