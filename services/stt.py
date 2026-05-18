import whisper
import asyncio

model = whisper.load_model("base")

async def transcribe_audio(audio_path: str) -> dict:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: model.transcribe(audio_path)
    )
    return result