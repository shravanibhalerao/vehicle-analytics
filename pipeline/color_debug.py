"""
color_debug.py
Purpose: Save a few vehicle crops and print their real HSV values,
         so we can tune the colour classifier using real data.
Run:     python pipeline/color_debug.py
Output:  images in debug_crops/ + a printed table.
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
from color_classifier import classify_color

SOURCE = "videos/traffic.mp4"
OUT_DIR = "debug_crops"
os.makedirs(OUT_DIR, exist_ok=True)

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(SOURCE)
frame_no, saved = 0, 0

while saved < 25:
    ok, frame = cap.read()
    if not ok:
        break
    frame_no += 1
    if frame_no % 20 != 0:          # look at every 20th frame only
        continue

    res = model.predict(frame, conf=0.4, classes=[2, 3, 5, 7], verbose=False)
    for box in res[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if (x2 - x1) < 40 or (y2 - y1) < 40:
            continue
        bw, bh = x2 - x1, y2 - y1
        centre = frame[y1 + bh // 4: y2 - bh // 4, x1 + bw // 4: x2 - bw // 4]
        if centre.size == 0:
            continue
        hsv = cv2.cvtColor(centre, cv2.COLOR_BGR2HSV).reshape(-1, 3)
        h, s, v = np.median(hsv, axis=0).astype(int)
        name = classify_color(frame, x1, y1, x2, y2)
        saved += 1
        print(f"crop {saved:2d}: classifier={name:7s} median H={h:3d} S={s:3d} V={v:3d}")
        cv2.imwrite(f"{OUT_DIR}/{saved:02d}_{name}.jpg", frame[y1:y2, x1:x2])
        if saved >= 25:
            break

cap.release()
print("Done. Open the debug_crops folder and look at the images.")