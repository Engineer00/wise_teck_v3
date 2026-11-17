"""Colour-layer masks for the reference JPEG (and for screenshots of the live page).

Each curve layer in the design has a distinct colour family, so a per-pixel HSV rule isolates it:
  gold   - warm yellow/orange ribbon (hero sweep, About block, footer wave)
  navy   - deep blue wedge / footer body
  silk   - lavender-blue translucent ribbons (darker + bluer than the canvas)
  white  - near-white crest / highlights

Run directly to write a colour-coded preview of the masks:
    python tools/ref_masks.py <image.png|jpg> <out.png>
"""
import sys
import numpy as np
from PIL import Image


def hsv(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn + 1e-6
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, d / (mx + 1e-6), 0)
    return h, s, mx, a


def masks(img):
    h, s, v, a = hsv(img)
    gold = (h > 28) & (h < 52) & (s > 0.38) & (v > 0.55)
    navy = (h > 205) & (h < 240) & (s > 0.45) & (v < 0.55)
    # silk: lavender-blue, noticeably more saturated / darker than the pale canvas
    silk = (h > 215) & (h < 250) & (s > 0.10) & (s < 0.45) & (v > 0.78) & ~navy
    white = (s < 0.05) & (v > 0.97)
    return {"gold": gold, "navy": navy, "silk": silk, "white": white}


def preview(img):
    m = masks(img)
    out = np.full((*m["gold"].shape, 3), 235, np.uint8)
    out[m["white"]] = (255, 255, 255)
    out[m["silk"]] = (150, 160, 230)
    out[m["navy"]] = (15, 35, 100)
    out[m["gold"]] = (240, 180, 40)
    return Image.fromarray(out)


if __name__ == "__main__":
    preview(Image.open(sys.argv[1])).save(sys.argv[2])
