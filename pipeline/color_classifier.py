"""
color_classifier.py
Purpose: Guess the colour of a vehicle from its cropped bounding box.
Method : 1) take the lower-central part of the crop (body panels,
            less roof/windshield glare)
         2) drop the brightest 20% of pixels (reflections)
         3) convert to HSV and put every remaining pixel into a bucket
         4) the bucket with the most pixels wins
Note   : This video has a blue-ish tint, so low/medium saturation is
         treated as "no colour".
Colours: black, white, silver, grey, red, blue (others -> "other")
"""

import cv2
import numpy as np

COLOR_NAMES = ["black", "white", "silver", "grey", "red", "blue", "other"]

# ---------- Tunable thresholds ----------
BLACK_V = 90          # V below this -> black
NEUTRAL_S = 110       # S below this -> no real colour (grey family)
WHITE_V = 170         # neutral and V >= this -> white
SILVER_V = 120        # neutral and V >= this -> silver, else grey
GLARE_PERCENT = 80    # ignore pixels brighter than this percentile
# ----------------------------------------


def classify_color(frame, x1, y1, x2, y2):
    """Return the colour name of the vehicle inside the box (x1,y1,x2,y2)."""
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 - x1 < 8 or y2 - y1 < 8:
        return "other"

    bw, bh = x2 - x1, y2 - y1
    # lower-central region: 25%-75% width, 40%-85% height
    crop = frame[y1 + int(bh * 0.40): y1 + int(bh * 0.85),
                 x1 + bw // 4: x2 - bw // 4]
    if crop.size == 0:
        return "other"

    crop = cv2.resize(crop, (32, 32))
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    H = hsv[:, :, 0].astype(int).ravel()
    S = hsv[:, :, 1].astype(int).ravel()
    V = hsv[:, :, 2].astype(int).ravel()

    # Remove the brightest pixels (glare / reflections)
    keep = V <= np.percentile(V, GLARE_PERCENT)
    H, S, V = H[keep], S[keep], V[keep]

    black = V < BLACK_V
    neutral = (S < NEUTRAL_S) & ~black
    white = neutral & (V >= WHITE_V)
    silver = neutral & (V >= SILVER_V) & (V < WHITE_V)
    grey = neutral & (V < SILVER_V)
    coloured = (S >= NEUTRAL_S) & ~black
    red = coloured & ((H < 10) | (H > 165))
    blue = coloured & (H >= 95) & (H <= 130)

    counts = {
        "black": int(black.sum()),
        "white": int(white.sum()),
        "silver": int(silver.sum()),
        "grey": int(grey.sum()),
        "red": int(red.sum()),
        "blue": int(blue.sum()),
        "other": int(coloured.sum() - red.sum() - blue.sum()),
    }
    return max(counts, key=counts.get)


if __name__ == "__main__":
    tests = {
        "black": (10, 10, 10), "white": (240, 240, 240),
        "red": (0, 0, 200), "blue": (200, 0, 0), "grey": (90, 90, 90),
    }
    for expected, bgr in tests.items():
        img = np.full((100, 100, 3), bgr, dtype=np.uint8)
        print(f"expected={expected:6s} got={classify_color(img, 0, 0, 100, 100)}")