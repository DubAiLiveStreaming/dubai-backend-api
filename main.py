import uuid, asyncio, os, shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from services.audio import extract_audio
from services.stt import transcribe_audio
from services.translate import translate_segments
from services.tts import generate_tts
from services.merger import merge_audio_video

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DubAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
app.mount("/dubbed", StaticFiles(directory=str(TEMP_DIR)), name="dubbed")

jobs = {}

def update_job(job_id, status, progress, extra=None):
    jobs[job_id].update({"status": status, "progress": progress})
    if extra:
        jobs[job_id].update(extra)

async def process_video(job_id, video_path):
    audio_path = None
    try:
        update_job(job_id, "extracting", 10)
        audio_path = extract_audio(video_path)

        update_job(job_id, "transcribing", 25)
        result = await transcribe_audio(audio_path)
        segments = result["segments"]

        update_job(job_id, "translating", 45)
        translated = translate_segments(segments)

        update_job(job_id, "tts", 60)
        tts_path = await generate_tts(translated, job_id, TEMP_DIR)

        update_job(job_id, "merging", 80)
        output_path = merge_audio_video(video_path, tts_path, job_id, TEMP_DIR)

        update_job(job_id, "done", 100, {
            "output_url": f"/dubbed/{job_id}_dubbed.mp4"
        })
    except Exception as e:
        update_job(job_id, "failed", 0, {"error": str(e)})

@app.post("/api/dub")
async def dub_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    video_path = str(TEMP_DIR / f"{job_id}.mp4")
    with open(video_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    jobs[job_id] = {"status": "queued", "progress": 0}
    background_tasks.add_task(process_video, job_id, video_path)
    return JSONResponse({"job_id": job_id, "status": "queued"})

@app.get("/api/job/{job_id}")
async def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return JSONResponse(job)