"""
detect_test.py
Purpose: Test vehicle detection using YOLOv8n.
         Reads a video (MP4 file or RTSP stream), detects cars, buses,
         trucks and motorcycles, and shows boxes with class + confidence.
Run:     python pipeline/detect_test.py
Quit:    press the 'q' key in the video window.
"""

import time
import cv2
from ultralytics import YOLO

# ---------- Settings (you can change these) ----------
SOURCE = "videos/traffic.mp4"   # later: "rtsp://localhost:8554/traffic"
MODEL_NAME = "yolov8n.pt"       # smallest model, downloads automatically
CONFIDENCE = 0.35               # ignore detections below 35% sure
# COCO class numbers: 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
# -----------------------------------------------------

model = YOLO(MODEL_NAME)
cap = cv2.VideoCapture(SOURCE)

if not cap.isOpened():
    raise SystemExit(f"Could not open video source: {SOURCE}")

prev_time = time.time()

while True:
    ok, frame = cap.read()
    if not ok:
        print("Video ended or stream stopped.")
        break

    # Run detection on this frame, only for vehicle classes
    results = model.predict(
        frame,
        conf=CONFIDENCE,
        classes=list(VEHICLE_CLASSES.keys()),
        imgsz=640,
        verbose=False,
    )

    # Draw a box + label for every detected vehicle
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = f"{VEHICLE_CLASSES[cls_id]} {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, max(y1 - 8, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show FPS (frames per second) on screen
    now = time.time()
    fps = 1.0 / (now - prev_time)
    prev_time = now
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

    cv2.imshow("Vehicle Detection Test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()