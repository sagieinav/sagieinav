"""One-off retouch of the study-room pixel art: remove the posters behind Sagi and the right mug.

Posters: replaced with brick from the clean wall above them, shifted up by whole pattern periods
(99px = 3 brick courses, found by autocorrelation on high-passed luminance) so mortar lines align.
Head and lamp pixels in front of the poster are kept with colour keys.
Mug: the pot and desk behind it are rebuilt from the visible pot strip and the desk beside it.

Run from the repo root (needs pillow, numpy, opencv-python-headless):
    python3 scripts/clean_scene.py assets/src/scene.webp assets/src/scene-clean.png
"""
import sys

import cv2
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open(src).convert("RGB"))
img = rgb.astype(np.float32) / 255
H, W, _ = img.shape
lum = img @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
hue, sat = hsv[..., 0] * 2, hsv[..., 1] / 255  # hue in degrees
PERIOD, CLEAN_TOP = 99, 158  # rows above CLEAN_TOP are plain brick

paper = (lum > 0.66) & (sat < 0.42)
replace = np.zeros((H, W), bool)
replace[158:458, 726:948] = True      # left poster
replace[158:458, 1052:1328] = True    # centre poster

skin = (lum > 0.45) & (sat > 0.30) & ~paper & (hue < 40)
head = np.zeros_like(replace); head[374:458, 1048:1118] = True      # hair starts at y 376
skin_zone = np.zeros_like(replace); skin_zone[405:458, 1048:1093] = True  # forehead/ear, left of x 1093
# lamp shade: keep everything below its top edge (a polygon traced from the image)
shade = np.zeros((H, W), np.uint8)
cv2.fillPoly(shade, [np.array([(1236, 460), (1236, 447), (1270, 428), (1300, 409), (1347, 401), (1347, 460)], np.int32)], 1)
lamp_zone = shade.astype(bool)
bronze = ((hue > 25) & (hue < 60) & (lum > 0.28)) | (lum < 0.14)
# Around the head, keep everything that isn't poster: the hair has light grey-blue strands, so a
# "dark = hair" key leaves holes; paper and the brown frame are the only things to remove there.
frame = (hue > 5) & (hue < 45) & (sat > 0.25) & (lum > 0.15) & (lum < 0.65)
paperish = paper | ((lum > 0.5) & (sat < 0.45) & (hue > 20) & (hue < 60))   # paper's anti-aliased edge
beside_face = np.zeros_like(replace); beside_face[432:458, 1093:1118] = True   # frame lines right of the face
head_keep = head & ~paperish & ~frame & ~(beside_face & (lum >= 0.15))
replace &= ~(head_keep | (skin_zone & skin) | (lamp_zone & ~paper))

# copy brick from above, whole periods up
ys, xs = np.nonzero(replace)
sy = ys.copy()
while (sy >= CLEAN_TOP).any():
    sy = np.where(sy >= CLEAN_TOP, sy - PERIOD, sy)
copied = img.copy()
copied[ys, xs] = img[sy, xs]

out_img = copied

# right mug (x 1322-1392, y 656-736): rebuild pot body, its right outline, then desk
pot_col = out_img[:, 1314:1320].mean(axis=1)            # pot colour per row, from its visible left strip
outline = out_img[650, 1386]                             # dark pot outline colour
for y in range(656, 700):
    out_img[y, 1320:1386] = pot_col[y]
    out_img[y, 1386:1391] = outline
out_img[697:701, 1310:1391] = outline                    # pot base line
left = np.median(out_img[700:740, 1290:1306], axis=1)    # desk colour per row, left of the pot
right = np.median(out_img[700:740, 1396:1412], axis=1)   # ... and right of the mug
t = np.linspace(0, 1, 1394 - 1310)[None, :, None]
out_img[700:740, 1310:1394] = left[:, None, :] * (1 - t) + right[:, None, :] * t

Image.fromarray((out_img * 255).astype(np.uint8)).save(out)
print("saved", out)
