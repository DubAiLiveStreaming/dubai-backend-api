import asyncio
from pathlib import Path
from gtts import gTTS
import subprocess
import imageio_ffmpeg

async def generate_tts(segments: list, job_id: str, temp_dir: Path) -> str:
    loop = asyncio.get_event_loop()
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    part_files = []

    for i, seg in enumerate(segments):
        part_path = str(temp_dir / f"{job_id}_part{i}.mp3")
        padded_path = str(temp_dir / f"{job_id}_padded{i}.wav")
        text = seg["text"]
        start = float(seg["start"])
        end = float(seg["end"])
        duration = end - start

        def make_tts(t=text, p=part_path):
            gTTS(text=t, lang="ta").save(p)

        await loop.run_in_executor(None, make_tts)

        # Fit TTS audio into segment duration
        subprocess.run([
            ffmpeg_exe, "-i", part_path,
            "-af", f"atempo=1.0",
            "-t", str(duration),
            "-ar", "44100", "-ac", "2",
            "-y", padded_path
        ], capture_output=True)

        part_files.append((start, duration, padded_path))

    # Build final audio with silence padding at correct timestamps
    merged_path = str(temp_dir / f"{job_id}_tts.wav")
    total_duration = part_files[-1][0] + part_files[-1][1] + 1

    # Create silence base
    silence_path = str(temp_dir / f"{job_id}_silence.wav")
    subprocess.run([
        ffmpeg_exe, "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=stereo",
        "-t", str(total_duration),
        "-y", silence_path
    ], capture_output=True)

    # Build filter_complex to mix each segment at correct timestamp
    inputs = ["-i", silence_path]
    for _, _, p in part_files:
        inputs += ["-i", p]

    filter_parts = []
    prev = "[0:a]"
    for i, (start, _, _) in enumerate(part_files):
        out = f"[a{i}]" if i < len(part_files) - 1 else "[aout]"
        filter_parts.append(
            f"{prev}[{i+1}:a]adelay={int(start*1000)}|{int(start*1000)}[tmp{i}];"
            f"[tmp{i}]amix=inputs=1[a{i}]" if i < len(part_files) - 1
            else f"{prev}[{i+1}:a]adelay={int(start*1000)}|{int(start*1000)}[aout]"
        )
        prev = f"[a{i}]