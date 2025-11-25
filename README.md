# Video Caption Application

A full-stack web application that allows users to upload MP4 videos, automatically generate captions using AI (OpenAI Whisper), and render those captions onto the video with customizable styles.

## Features

- 🎬 **Video Upload**: Drag & drop or browse to upload MP4 files
- ✨ **AI Caption Generation**: Automatic transcription using OpenAI Whisper
- 🎨 **Multiple Caption Styles**: Bottom, Top, and Karaoke styles
- 📹 **Video Rendering**: Burn captions directly into video
- 💫 **Modern UI**: Premium dark theme with glassmorphism effects
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- OpenAI Whisper (AI transcription)
- MoviePy (Video processing)
- FFmpeg (Video encoding)

**Frontend:**
- HTML5
- Modern CSS (Glassmorphism, Gradients, Animations)
- Vanilla JavaScript

## Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg
- pkg-config

### Installation

1. **Install system dependencies** (macOS):
   ```bash
   brew install ffmpeg pkg-config
   ```

2. **Set up backend**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the backend server**:
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --port 8002
   ```

4. **Open the frontend**:
   - Open `frontend/index.html` in your browser
   - Or use a local server:
     ```bash
     cd frontend
     python3 -m http.server 5500
     ```
   - Then visit: `http://localhost:5500`

## Usage

1. **Upload Video**: Click or drag & drop an MP4 file
2. **Generate Captions**: Click "Auto-Generate Captions" to transcribe audio
3. **Choose Style**: Select from Bottom, Top, or Karaoke caption styles
4. **Render**: Click "Render Video" to burn captions into the video
5. **Download**: Preview and download your captioned video

## API Endpoints

- `POST /upload-video` - Upload video file
- `POST /auto-generate-captions` - Generate captions from video audio
- `POST /render` - Render video with captions
- `GET /download/{filename}` - Download rendered video

## Project Structure

```
video_caption/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app & endpoints
│   │   ├── whisper_service.py   # AI transcription
│   │   ├── renderer.py          # Video rendering
│   │   ├── srt_converter.py     # SRT format converter
│   │   ├── static/              # Uploaded & rendered videos
│   │   └── fonts/               # Custom fonts for captions
│   ├── requirements.txt
│   └── .venv/
└── frontend/
    ├── index.html               # Main UI
    ├── style.css                # Premium styling
    └── script.js                # Frontend logic
```

## Configuration

**Backend Port**: Default is `8002` (change in `backend/app/main.py`)  
**Frontend API URL**: Update `API_BASE` in `frontend/script.js` if deploying

## Notes

- First caption generation downloads the Whisper model (~140MB for base model)
- Rendering can take several minutes depending on video length
- Supports Devanagari and other Unicode scripts in captions

## License

MIT
