"""
track_count.py
Purpose: Full pipeline.
         RTSP/MP4 -> YOLOv8n detection -> ByteTrack IDs -> HSV colour
         (majority vote) -> line crossing -> PostgreSQL -> annotated RTSP
         stream (boxes + IDs + line) that the dashboard plays.
Run:     python pipeline/track_count.py
Quit:    press 'q' in the video window.
Note:    This is a YOLO/OpenCV implementation, NOT NVIDIA DeepStream.
"""
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|fflags;nobuffer"
import subprocess
import time
from collections import Counter, defaultdict

import cv2
from ultralytics import YOLO
from color_classifier import classify_color
from db import save_event

# ---------- Settings ----------
SOURCE = "videos/traffic.mp4"      # or "videos/traffic.mp4"
OUTPUT_RTSP = "rtsp://localhost:8554/annotated"
PUBLISH_ANNOTATED = False                      # False = no output stream
MODEL_NAME = "yolov8n.pt"
CONFIDENCE = 0.35
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
LINE_POSITION = 0.60
MAX_VOTES = 30
OUT_WIDTH = 1280                              # annotated stream width
# ------------------------------

model = YOLO(MODEL_NAME)
cap = cv2.VideoCapture(SOURCE)
if not cap.isOpened():
    raise SystemExit(f"Could not open video source: {SOURCE}")

frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
line_y = int(frame_h * LINE_POSITION)

# Publish the annotated frames to MediaMTX through FFmpeg
ffmpeg_out = None
if PUBLISH_ANNOTATED:
    ffmpeg_out = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{frame_w}x{frame_h}", "-r", "15", "-i", "-",
         "-vf", f"scale={OUT_WIDTH}:-2", "-c:v", "libx264",
         "-preset", "ultrafast", "-tune", "zerolatency", "-pix_fmt", "yuv420p",
         "-f", "rtsp", "-rtsp_transport", "tcp", OUTPUT_RTSP],
        stdin=subprocess.PIPE,
    )

last_y = {}
counted_ids = set()
color_votes = defaultdict(list)
totals = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
direction_counts = {"up": 0, "down": 0}
prev_time = time.time()


def voted_color(track_id):
    return Counter(color_votes[track_id]).most_common(1)[0][0]


while True:
    ok, frame = cap.read()
    if not ok:
        print("Video ended or stream stopped.")
        break

    results = model.track(
        frame, persist=True, tracker="bytetrack.yaml", conf=CONFIDENCE,
        classes=list(VEHICLE_CLASSES.keys()), imgsz=640, verbose=False,
    )

    boxes = results[0].boxes
    if boxes is not None and boxes.id is not None:
        for box, track_id in zip(boxes, boxes.id.int().tolist()):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_name = VEHICLE_CLASSES[int(box.cls[0])]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            color_votes[track_id].append(classify_color(frame, x1, y1, x2, y2))
            color_votes[track_id] = color_votes[track_id][-MAX_VOTES:]
            vehicle_color = voted_color(track_id)

            # ---- Line crossing (each ID counted once) ----
            if track_id in last_y and track_id not in counted_ids:
                prev_y = last_y[track_id]
                crossed_down = prev_y < line_y <= cy
                crossed_up = prev_y > line_y >= cy
                if crossed_down or crossed_up:
                    direction = "down" if crossed_down else "up"
                    counted_ids.add(track_id)
                    totals[cls_name] += 1
                    direction_counts[direction] += 1
                    print(f"COUNTED: id={track_id} type={cls_name} "
                          f"color={vehicle_color} direction={direction}")
                    save_event(track_id, cls_name, vehicle_color, direction)
            last_y[track_id] = cy

            # ---- Drawing ----
            box_color = (0, 0, 255) if track_id in counted_ids else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)
            cv2.putText(frame, f"#{track_id} {cls_name} {vehicle_color}",
                        (x1, max(y1 - 8, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, box_color, 2)

    cv2.line(frame, (0, line_y), (frame_w, line_y), (0, 255, 255), 2)
    cv2.putText(frame, f"Total: {sum(totals.values())}  Up: {direction_counts['up']}  Down: {direction_counts['down']}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, f"Car:{totals['car']} Bus:{totals['bus']} Truck:{totals['truck']} Moto:{totals['motorcycle']}",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    now = time.time()
    cv2.putText(frame, f"FPS: {1.0 / (now - prev_time):.1f}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    prev_time = now

    # Send the finished frame to the annotated stream
    if ffmpeg_out is not None:
        try:
            ffmpeg_out.stdin.write(frame.tobytes())
        except (BrokenPipeError, OSError):
            ffmpeg_out = None

    cv2.imshow("Tracking + Line Crossing", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
if ffmpeg_out is not None:
    try:
        ffmpeg_out.stdin.close()
    except Exception:
        pass