# backend/app/main.py
import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.whisper_service import transcribe_local
from app.renderer import render_with_style
from app.srt_converter import segments_to_srt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="Video Captioner (Python)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve frontend static files (if you want to serve frontend from backend)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}-{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"video_path": f"/static/uploads/{filename}", "video_filename": filename}

@app.post("/auto-generate-captions")
async def auto_generate_captions(
    video_filename: str = Form(...),
    language: str = Form(None)  # Optional: 'en', 'hi', 'es', etc. or None for auto-detect
):
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    if not os.path.exists(video_path):
        return {"error": "video file not found"}

    # Transcribe using Whisper with optional language
    segments = transcribe_local(video_path, language=language)
    srt_text = segments_to_srt(segments)

    # Save SRT next to file
    srt_filename = video_filename + ".srt"
    srt_path = os.path.join(UPLOAD_DIR, srt_filename)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_text)

    return {
        "captions": segments,
        "srt_path": f"/static/uploads/{srt_filename}"
    }

@app.post("/render")
async def render(video_filename: str = Form(...), style: str = Form("bottom")):
    """
    style: 'bottom' | 'top' | 'karaoke'
    """
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    srt_path = video_path + ".srt"
    if not os.path.exists(video_path):
        return {"error": "video not found"}
    if not os.path.exists(srt_path):
        return {"error": "srt not found; run auto-generate-captions first"}

    out_name = f"{uuid.uuid4()}-rendered-{style}-{video_filename}"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    render_with_style(video_path, srt_path, out_path, style=style,
                      fonts_dir=os.path.join(BASE_DIR, "fonts"))
    # Return URL to static output
    return {"output_path": f"/static/outputs/{out_name}", "output_filename": out_name}

@app.get("/download/{output_filename:path}")
async def download_output(output_filename: str):
    """
    Download rendered video file.
    Uses :path to handle filenames with special characters.
    """
    print(f"📥 Download request for: {output_filename}")
    out_path = os.path.join(OUTPUT_DIR, output_filename)
    
    if not os.path.exists(out_path):
        print(f" File not found: {out_path}")
        return {"error": "file not found"}
    
    print(f"✅ Serving file: {out_path}")
    # Let FileResponse handle the Content-Disposition header automatically
    # This avoids UnicodeEncodeError for filenames with special characters
    return FileResponse(
        out_path, 
        media_type="video/mp4", 
        filename=output_filename
    )
