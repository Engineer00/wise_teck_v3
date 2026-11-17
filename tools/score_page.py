"""Score a live-page screenshot (1440 x 4315) against the reference: IoU of the gold and navy curve
layers inside the curve zones (hero sweep, About continuation, footer wave).
    python tools/score_page.py <screenshot.png>
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from ref_masks import masks
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "assets" / "ref" / "reference.jpeg"
ZONES = {"hero sweep (gold)": ("gold", 430, 705, 1100, 1440), "hero sweep (navy)": ("navy", 520, 720, 1180, 1440),
         "footer wave (gold)": ("gold", 3900, 4010, 0, 1440), "footer wave (navy)": ("navy", 3930, 4100, 0, 1440)}
ref = Image.open(REF).convert("RGB").resize((1440, 4315), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
me = Image.open(sys.argv[1]).convert("RGB").crop((0, 0, 1440, 4315)).filter(ImageFilter.GaussianBlur(2.5))
mr, mm = masks(ref), masks(me)
tot = []
for name, (layer, y0, y1, x0, x1) in ZONES.items():
    a, b = mr[layer][y0:y1, x0:x1], mm[layer][y0:y1, x0:x1]
    iou = (a & b).sum() / max(1, (a | b).sum()); tot.append(iou)
    print(f"{name:20s} {iou*100:5.1f}%")
print(f"{'MEAN':20s} {sum(tot)/len(tot)*100:5.1f}%")
