"""Edge-profile tracer: extracts every background curve of the reference JPEG as smooth SVG bands.

Background ribbons are bands that run across the page, so for each pixel column we measure where the
band's top and bottom edges are, filter out JPEG noise (median + gaussian), and join the two edge
profiles into one closed, smooth Bezier shape. Coordinates are page pixels at 1440px width
(reference 534px x 2.6966), so the whole page is one 1440 x 4315 coordinate system.

Outputs
  assets/wt-curves.svg     SVG sprite: <g id="wt-curves"> with every traced layer (page coordinates)
  assets/wt-sections.json  each section's top/height in page pixels (used to slice the sprite)
  tools/out/score.txt      match score (IoU) of each traced layer against the reference mask
  tools/out/check-*.png    traced outlines drawn over the reference

    python tools/trace_profiles.py
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

from ref_masks import masks

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "assets" / "ref" / "reference.jpeg"
OUT = ROOT / "tools" / "out"
W = 1440
STEP = 3
SIGMA = {"silk": 6.0, "gold": 4.0, "navy": 5.0}  # edge smoothing (in samples of STEP px)

# Section bands in reference px (534 wide) -> page px via the scale factor.
SECTIONS = {
    "topbar": (0, 20), "hero": (20, 243), "about": (243, 415), "eco": (415, 627),
    "programs": (627, 875), "services": (875, 1090), "weekend": (1090, 1185),
    "stories": (1185, 1300), "corp": (1300, 1400), "collab": (1400, 1462), "footer": (1462, 1600),
}

# (id, layer, x0, x1, y0, y1, mode)   mode: band = top+bottom edge, fill = top edge filled to y1
SPECS = [
    # hero
    ("hero-silk-tl",   "silk", 0,    150, 85,   210, "band"),
    ("hero-silk-left", "silk", 0,    135, 235,  625, "band"),
    ("hero-silk-tr",   "silk", 1150, 1440, 130, 300, "band"),
    ("hero-silk-mid",  "silk", 690,  1085, 470, 615, "band"),
    ("hero-silk-main", "silk", 0,    1440, 560, 722, "band"),
    ("hero-gold",      "gold", 1130, 1440, 430, 690, "band"),
    ("hero-navy",      "navy", 1215, 1440, 540, 705, "band"),
    # about
    ("about-silk-bl",  "silk", 0,    320, 1028, 1165, "band"),
    ("about-silk-um",  "silk", 880,  1135, 1058, 1112, "band"),
    # ecosystem
    ("eco-silk-l",     "silk", 0,    85,  1565, 1735, "band"),
    ("eco-silk-r",     "silk", 1355, 1440, 1555, 1712, "band"),
    ("eco-silk-streak","silk", 990,  1275, 1622, 1655, "band"),
    # programs -> services
    ("prog-silk-bl",   "silk", 0,    260, 2215, 2355, "band"),
    ("serv-silk-tr",   "silk", 1245, 1440, 2318, 2392, "band"),
    # footer
    ("foot-gold-l",    "gold", 0,    255, 3922, 4002, "band"),
    ("foot-gold-m",    "gold", 315,  525, 3958, 4002, "band"),
    ("foot-gold-r",    "gold", 1155, 1440, 3915, 4002, "band"),
    ("foot-navy",      "navy", 0,    1440, 3915, 4315, "fill"),
]


def longest_run(col):
    best, start, bs, be = 0, None, None, None
    for i, v in enumerate(np.append(col, False)):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > best:
                best, bs, be = i - start, start, i - 1
            start = None
    return (bs, be) if best >= 2 else (None, None)


def smooth(a, sigma=4.0):
    a = np.asarray(a, float)
    if len(a) < 5:
        return a
    k = 5
    pad = np.pad(a, k // 2, mode="edge")
    med = np.array([np.median(pad[i:i + k]) for i in range(len(a))])
    r = int(sigma * 3)
    x = np.arange(-r, r + 1)
    g = np.exp(-x * x / (2 * sigma * sigma)); g /= g.sum()
    return np.convolve(np.pad(med, r, mode="edge"), g, mode="valid")


def catmull_open(p):
    d = []
    for i in range(len(p) - 1):
        p0 = p[i - 1] if i > 0 else p[i]
        p1, p2 = p[i], p[i + 1]
        p3 = p[i + 2] if i + 2 < len(p) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d)


def profile(mask, x0, x1, y0, y1, mode, layer="silk"):
    xs, tops, bots = [], [], []
    for x in range(x0, min(x1, W - 1) + 1, STEP):
        col = mask[y0:y1, x]
        if mode == "fill":
            idx = np.flatnonzero(col)
            if len(idx) == 0:
                continue
            t, b = idx[0], y1 - y0
        else:
            t, b = longest_run(col)
            if t is None:
                continue
        xs.append(x); tops.append(y0 + t); bots.append(y0 + b)
    if len(xs) < 4:
        return None
    # keep the longest contiguous x-run (drop stray columns)
    xs = np.array(xs); gaps = np.flatnonzero(np.diff(xs) > STEP * 4)
    segs = np.split(np.arange(len(xs)), gaps + 1)
    seg = max(segs, key=len)
    sg = SIGMA.get(layer, 4.0)
    xs, tops, bots = xs[seg], smooth(np.array(tops)[seg], sg), smooth(np.array(bots)[seg], sg)
    if mode == "fill":
        bots = np.full_like(bots, y1)
    # snap to page edges so ribbons run in from the edge without a gap
    if xs[0] <= STEP * 2: xs[0] = 0
    if xs[-1] >= W - STEP * 2: xs[-1] = W
    # taper the open (non-edge) ends to a point, like the ribbons in the design
    if xs[0] > 0:
        mid = (tops[0] + bots[0]) / 2; tops[0] = bots[0] = mid
    if xs[-1] < W:
        mid = (tops[-1] + bots[-1]) / 2; tops[-1] = bots[-1] = mid
    return xs, tops, bots


def band_path(xs, tops, bots, every=4):
    """Smooth closed band. The polygon (for scoring) keeps every sample; the SVG path keeps every
    `every`-th sample (plus both ends) - the edges are already smoothed, so nothing visible is lost."""
    top = list(zip(xs, tops)); bot = list(zip(xs[::-1], bots[::-1]))
    keep = sorted(set(range(0, len(top), every)) | {len(top) - 1})
    t2, b2 = [top[i] for i in keep], [bot[i] for i in keep]
    d = f"M{t2[0][0]:.0f} {t2[0][1]:.1f} " + catmull_open(t2)
    d += f" L{b2[0][0]:.0f} {b2[0][1]:.1f} " + catmull_open(b2) + " Z"
    return d, np.array(top + bot, np.int32)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ref = Image.open(REF).convert("RGB")
    s = W / ref.width
    H = round(ref.height * s)
    big = ref.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    m = masks(big)
    clean = {}
    for k in ("silk", "gold", "navy"):
        mk = (m[k].astype(np.uint8) * 255)
        mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        clean[k] = mk > 0

    shapes, scores = [], []
    canvas = cv2.cvtColor(np.asarray(big), cv2.COLOR_RGB2BGR).copy()
    col = {"silk": (220, 90, 60), "gold": (0, 140, 255), "navy": (120, 20, 0)}
    for sid, layer, x0, x1, y0, y1, mode in SPECS:
        r = profile(clean[layer], x0, x1, y0, y1, mode, layer)
        if r is None:
            print("skip", sid); continue
        if layer == "gold":
            # gold sits directly on the navy in the design: extend it under the navy (navy is drawn on top)
            # only where navy covers it (hero: x >= 1240; footer: the whole width)
            under = (r[0] >= 1240) if sid == "hero-gold" else np.ones_like(r[0], bool)
            r = (r[0], r[1], r[2] + 22 * under)
        d, poly = band_path(*r)
        shapes.append((sid, layer, d))
        if layer == "silk":
            # satin sheen: crisp white lines along the band's smoothed top and bottom edges
            xs, tops, bots = r
            keep = sorted(set(range(0, len(xs), 4)) | {len(xs) - 1})
            for edge, cls in ((tops, "wt-line"), (bots, "wt-line wt-line-b")):
                pts = [(xs[i], edge[i]) for i in keep]
                shapes.append((sid + ("-t" if edge is tops else "-b"), cls,
                               f"M{pts[0][0]:.0f} {pts[0][1]:.1f} " + catmull_open(pts)))
        # score: IoU of traced shape vs reference mask inside the spec window
        traced = np.zeros((H, W), np.uint8); cv2.fillPoly(traced, [poly], 1)
        win = np.s_[y0:y1, x0:min(x1, W)]
        a, b = traced[win].astype(bool), clean[layer][win]
        iou = (a & b).sum() / max(1, (a | b).sum())
        scores.append((sid, iou))
        cv2.polylines(canvas, [poly], True, col[layer], 2)

    # sprite: silk gets a translucent satin fill + white sheen; gold/navy solid gradients
    body = []
    for sid, layer, d in shapes:
        if layer.startswith("wt-line"):
            body.append(f'  <path id="{sid}" class="{layer}" d="{d}" fill="none"/>')
            continue
        fill = {"silk": "url(#wtSilk)", "gold": "url(#wtGold)", "navy": "url(#wtNavy)"}[layer]
        body.append(f'  <path id="{sid}" class="wt-{layer}" d="{d}" fill="{fill}"/>')
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">\n'
        '<defs>\n'
        ' <linearGradient id="wtSilk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9d0f6" stop-opacity=".95"/>'
        '<stop offset=".55" stop-color="#b3bdf0" stop-opacity=".85"/><stop offset="1" stop-color="#a3aeea" stop-opacity=".75"/></linearGradient>\n'
        ' <linearGradient id="wtGold" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#f3e1a6"/>'
        '<stop offset=".45" stop-color="#dcb84a"/><stop offset="1" stop-color="#8a6a1f"/></linearGradient>\n'
        ' <linearGradient id="wtNavy" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a3a8f"/><stop offset="1" stop-color="#0b1f55"/></linearGradient>\n'
        ' <g id="wt-curves">\n' + "\n".join(body) + "\n </g>\n</defs>\n</svg>\n"
    )
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "wt-curves.svg").write_text(svg, encoding="utf-8")
    secs = {k: {"top": round(a * s), "height": round(b * s) - round(a * s)} for k, (a, b) in SECTIONS.items()}
    (ROOT / "assets" / "wt-sections.json").write_text(json.dumps(secs, indent=1))
    lines = [f"{sid:16s} IoU {iou*100:5.1f}%" for sid, iou in scores]
    mean = sum(i for _, i in scores) / len(scores)
    lines.append(f"{'MEAN':16s} IoU {mean*100:5.1f}%")
    (OUT / "score.txt").write_text("\n".join(lines))
    print("\n".join(lines))
    for name, (a, b) in (("top", (0, 1250)), ("mid", (1500, 2450)), ("foot", (3850, H))):
        cv2.imwrite(str(OUT / f"check-{name}.png"), canvas[a:b])


if __name__ == "__main__":
    main()
