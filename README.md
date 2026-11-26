# Vehicle Analytics

Real-time vehicle counting and analytics from a traffic video stream.
The system detects vehicles, tracks them, finds their colour, counts each one
once when it crosses a virtual line, stores every crossing in PostgreSQL and
shows live analytics on a React dashboard next to the live video.

![Dashboard](docs/dashboard.png)

## Features

- Vehicle detection with **YOLOv8n** (car, motorcycle, bus, truck)
- Multi-object tracking with **ByteTrack** (each vehicle gets a stable ID)
- Line-crossing counter with direction (**up / down**), no double counting
- Vehicle colour from a secondary classifier (**CLIP** zero-shot on the cropped
  bounding box), with a majority vote over several frames per vehicle
- Every crossing saved to **PostgreSQL**
- **FastAPI** backend with analytics endpoints
- **React** dashboard (Vite + Recharts) with live HLS video, stats, charts and
  recent events, auto-refreshing every 5 seconds
- Video served as an RTSP stream with **MediaMTX** (also exposed as HLS for the browser)

## Architecture

```
traffic.mp4 --ffmpeg--> MediaMTX (RTSP :8554 / HLS :8888)
                              |                    |
                              v                    v
              pipeline (YOLOv8n + ByteTrack     React dashboard
                        + CLIP colour)          (live video)
                              |                    ^
                              v                    |
                         PostgreSQL  -------->  FastAPI (:8000)
                       (vehicle_events)
```

## Tech stack

| Part        | Tools                                    |
|-------------|------------------------------------------|
| Detection   | Ultralytics YOLOv8n                      |
| Tracking    | ByteTrack (built into Ultralytics)       |
| Colour      | OpenAI CLIP (`openai/clip-vit-base-patch32`) via Hugging Face Transformers |
| Streaming   | MediaMTX, FFmpeg                         |
| Database    | PostgreSQL, psycopg2                     |
| Backend     | FastAPI, Uvicorn                         |
| Frontend    | React (Vite), Recharts, hls.js           |

## Project structure

```
vehicle-analytics/
├── backend/        FastAPI app (main.py)
├── database/       SQL for the vehicle_events table
├── docs/           Screenshots
├── frontend/       React dashboard (Vite)
├── mediamtx/       MediaMTX config (binary not committed)
├── pipeline/       Detection, tracking, colour, counting
├── scripts/        Helper scripts
├── videos/         Input video (not committed)
├── requirements.txt
└── .env            Database settings (not committed)
```

## Setup

### 1. Requirements

- Python 3.10+
- Node.js 18+
- PostgreSQL
- FFmpeg (on PATH)
- MediaMTX (download the Windows binary and put `mediamtx.exe` in `mediamtx/`)

### 2. Python environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The