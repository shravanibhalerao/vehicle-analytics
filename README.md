# Vehicle Analytics

Real-time vehicle counting and analytics from a traffic video stream.

This project detects and tracks vehicles, identifies their approximate colour, counts vehicles when they cross a virtual line, stores crossing events in PostgreSQL, and displays live analytics on a React dashboard.

![Vehicle Analytics Dashboard](./docs/dashboard.png)
## Features

- Vehicle detection using **YOLOv8n** (car, motorcycle, bus, truck)
- Multi-object tracking using **ByteTrack**
- Unique vehicle IDs for tracking
- Line-crossing vehicle counting with **Up / Down** direction
- Vehicle colour classification using **CLIP**
- Majority voting over multiple frames for colour prediction
- PostgreSQL database for storing vehicle events
- FastAPI backend with analytics endpoints
- React dashboard with live HLS video, statistics and charts
- Automatic dashboard refresh every 5 seconds
- Live video streaming using MediaMTX and FFmpeg

## Architecture

```text
Traffic Video
     |
     v
   FFmpeg
     |
     v
  MediaMTX
     |
     +---------------------> React Dashboard
     |                         (Live Video)
     |
     v
Vehicle Detection Pipeline
     |
     +-- YOLOv8n Detection
     |
     +-- ByteTrack Tracking
     |
     +-- CLIP Colour Detection
     |
     +-- Line Crossing Counter
     |
     v
  PostgreSQL
     |
     v
   FastAPI
     |
     v
React Dashboard
(Analytics and Statistics)
```

## Technology Stack

| Component | Technology |
|---|---|
| Vehicle Detection | YOLOv8n |
| Object Tracking | ByteTrack |
| Colour Classification | OpenAI CLIP |
| Backend | FastAPI, Python |
| Database | PostgreSQL |
| Frontend | React, Vite |
| Charts | Recharts |
| Video Streaming | MediaMTX, FFmpeg |
| Video Playback | HLS.js |

## Project Structure

```text
vehicle-analytics/
├── backend/          FastAPI application
├── database/         SQL database scripts
├── docs/             Project screenshots
├── frontend/         React dashboard
├── mediamtx/         MediaMTX configuration
├── pipeline/         Detection, tracking and counting
├── scripts/          Helper scripts
├── videos/           Input traffic video
├── requirements.txt
└── .env              Database configuration
```

## Installation and Setup

### 1. Requirements

- Python 3.10+
- Node.js 18+
- PostgreSQL
- FFmpeg
- MediaMTX

### 2. Python Environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Database Configuration

Create a PostgreSQL database named `vehicle_analytics`.

Run the SQL script inside the `database/` folder.

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vehicle_analytics
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Frontend Installation

```powershell
cd frontend
npm install
```

### 5. Input Video

Place the traffic video inside the `videos/` folder with the filename:

```text
traffic.mp4
```

## Running the Project

Run each component in a separate terminal.

### 1. Start MediaMTX

```powershell
mediamtx\mediamtx.exe
```

### 2. Start FFmpeg Video Stream

```powershell
ffmpeg -re -stream_loop -1 -i videos/traffic.mp4 -an -c:v libx264 -preset veryfast -tune zerolatency -g 60 -pix_fmt yuv420p -rtsp_transport tcp -f rtsp rtsp://localhost:8554/traffic

3. Start Vehicle Detection Pipeline

Activate the Python virtual environment and run:

python pipeline/track_count.py

The pipeline displays vehicle detection boxes, tracking IDs, colour labels and counting information in its OpenCV window.

Press q to stop the pipeline.

4. Start FastAPI Backend

From the project root:

uvicorn backend.main:app --reload --port 8000

API documentation:

http://localhost:8000/docs

5. Start React Dashboard

cd frontend
npm run dev

Open:

http://localhost:5173

API Endpoints

Method

Endpoint

Description

GET

/api/total

Total vehicles counted

GET

/api/stats/types

Vehicle count by type

GET

/api/stats/colors

Vehicle count by colour

GET

/api/events/recent?limit=20

Recent crossing events

GET

/api/analytics/history?hours=24

Hourly vehicle analytics

Database: vehicle_events

Column

Description

id

Unique row ID

vehicle_id

ByteTrack vehicle ID

vehicle_type

Car, motorcycle, bus or truck

vehicle_color

Detected vehicle colour

direction

Up or Down

timestamp

Vehicle crossing time

How the System Works

Detection: YOLOv8n detects vehicles in each video frame.

Tracking: ByteTrack assigns and maintains vehicle IDs across frames.

Colour Classification: CLIP predicts the approximate vehicle colour using cropped vehicle images.

Counting: A virtual horizontal line counts vehicles when their centre crosses it.

Database Storage: Crossing events are stored in PostgreSQL.

Analytics: FastAPI provides data to the React dashboard.

Visualization: The dashboard displays statistics, charts and live video.

Screenshots

Dashboard



Vehicle Detection and Tracking Pipeline



Stream Test



API Documentation



Known Limitations

Vehicle colour classification is approximate and may make mistakes.

Motorcycles may be classified as black because of dark clothing and helmets.

CLIP processing can reduce FPS on CPU-based systems.

Crowded scenes may cause tracking ID loss.

The counting line is configured for the current camera angle.

Conclusion

The Vehicle Analytics system combines computer vision, object tracking, video streaming, database management and web technologies to provide real-time vehicle monitoring and analytics.