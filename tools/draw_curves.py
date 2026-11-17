"""Remake the page background as smooth, hand-authored curve art (final art for the site).

Every curve is a SMOOTH FUNCTION, not a trace:
  - each ribbon's centre line and thickness are least-squares fitted with a low-order polynomial to
    the position measured in the reference (so placement matches the design, wobble is impossible);
  - free ends taper with a smootherstep envelope, so ribbons end in elegant points;
  - the footer gold is one continuous ribbon riding the navy's wave: thick - thin - thick.

Layer styling (like the design):
  silk  -> 3 stacked translucent satin ribbons + white sheen lines
  gold  -> gradient ribbon + light top highlight, tucked under the navy, white seam between them
  navy  -> deep gradient + thin inner rim highlight

Output: assets/wt-curves.svg (page coordinates at 1440 x 4315).   python tools/draw_curves.py
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

from ref_masks import masks
from trace_profiles import SPECS, REF, W, profile, catmull_open

ROOT = Path(__file__).resolve().parent.parent
DEG = {"silk": 4, "gold": 3, "navy": 3}        # polynomial order of each fitted curve (low = smooth)
SAMPLE = 36                                     # output point spacing (px); curves are exact functions


def smootherstep(t):
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (6 * t - 15) + 10)


def fit(xs, ys, deg, xq):
    u = (np.asarray(xs) - xs[0]) / max(1, xs[-1] - xs[0])
    c = np.polyfit(u, ys, deg)
    return np.polyval(c, (xq - xs[0]) / max(1, xs[-1] - xs[0]))


def d_open(xs, ys):
    pts = list(zip(xs, ys))
    return f"M{pts[0][0]:.0f} {pts[0][1]:.1f} " + catmull_open(pts)


def d_band(xs, top, bot):
    t = list(zip(xs, top)); b = list(zip(xs[::-1], bot[::-1]))
    return (f"M{t[0][0]:.0f} {t[0][1]:.1f} " + catmull_open(t) + f" L{b[0][0]:.0f} {b[0][1]:.1f} "
            + catmull_open(b) + " Z")


def ribbon(xs, tops, bots, layer):
    """Smooth ribbon from measured edges: fitted centre line + fitted thickness + tapered free ends."""
    x0, x1 = xs[0], xs[-1]
    xq = np.linspace(x0, x1, max(4, int((x1 - x0) / SAMPLE) + 1))
    mid = fit(xs, (tops + bots) / 2, DEG[layer], xq)
    half = np.clip(fit(xs, (bots - tops) / 2, min(DEG[layer], 3), xq), 0.5, None)
    L = x1 - x0
    env = np.ones_like(xq)
    if x0 > 0:                      # free left end -> taper to a point
        env *= smootherstep((xq - x0) / (0.28 * L))
    if x1 < W:                      # free right end -> taper
        env *= smootherstep((x1 - xq) / (0.28 * L))
    half = half * (0.06 + 0.94 * env)
    return xq, mid - half, mid + half


def main():
    ref = Image.open(REF).convert("RGB")
    s = W / ref.width
    H = round(ref.height * s)
    big = ref.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    m = masks(big)
    clean = {}
    for k in ("silk", "gold", "navy"):
        mk = m[k].astype(np.uint8) * 255
        mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        clean[k] = mk > 0

    silk, gold, navy, lines = [], [], [], []
    foot_top = None
    for sid, layer, x0, x1, y0, y1, mode in SPECS:
        if sid.startswith("foot-gold"):
            continue                                  # footer gold is drawn as one continuous ribbon below
        r = profile(clean[layer], x0, x1, y0, y1, mode, layer)
        if r is None:
            continue
        xs, tops, bots = (np.asarray(v, float) for v in r)

        if sid == "foot-navy":
            # the footer wave: one smooth function across the full width (order 6 = gentle S-waves)
            xq = np.linspace(0, W, int(W / SAMPLE) + 1)
            top = fit(xs, tops, 6, xq)
            foot_top = (xq, top)
            navy.append(("foot-navy", d_band(xq, top, np.full_like(top, y1))))
            navy.append(("foot-navy-hi", d_band(xq, top, top + 9)))
            continue

        xq, top, bot = ribbon(xs, tops, bots, layer)
        if layer == "silk":
            q1 = top + (bot - top) * 0.62
            q2 = top + (bot - top) * 0.45
            silk.append((d_band(xq, top, bot), "wtSilkA", 0.55))
            silk.append((d_band(xq, top, q1), "wtSilkB", 0.55))
            silk.append((d_band(xq, q2, bot), "wtSilkC", 0.45))
            lines += [("wt-line", d_open(xq, top)), ("wt-line wt-line-m", d_open(xq, q2)), ("wt-line wt-line-b", d_open(xq, bot))]
        elif layer == "gold":                         # hero gold: tuck under the navy where navy exists
            under = smootherstep((xq - 1215) / 40)
            gold.append(("g", d_band(xq, top, bot + 22 * under)))
            gold.append(("hi", d_band(xq, top, top + (bot - top) * 0.35)))
        else:                                         # hero navy wedge
            navy.append(("hero-navy", d_band(xq, top, bot)))
            navy.append(("hero-navy-hi", d_band(xq, top, top + 9)))
            lines.append(("wt-seam", d_open(xq, top)))

    if foot_top is not None:
        xq, top = foot_top
        u = np.abs(2 * xq / W - 1)                    # 0 in the middle, 1 at both edges
        thick = 3 + 34 * u ** 2.4                     # thick - thin - thick, like the design
        gold.append(("g", d_band(xq, top - thick, top + 22)))
        gold.append(("hi", d_band(xq, top - thick, top - thick * 0.6)))
        lines.append(("wt-seam", d_open(xq, top)))

    defs = """ <linearGradient id="wtSilkA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dfe4fb"/><stop offset="1" stop-color="#b6c0f1"/></linearGradient>
 <linearGradient id="wtSilkB" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity=".9"/><stop offset=".5" stop-color="#e6e9fc" stop-opacity=".5"/><stop offset="1" stop-color="#ffffff" stop-opacity=".85"/></linearGradient>
 <linearGradient id="wtSilkC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c3cbf4" stop-opacity=".2"/><stop offset="1" stop-color="#9fabea"/></linearGradient>
 <linearGradient id="wtGold" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#f6d27c"/><stop offset=".4" stop-color="#eeb43c"/><stop offset=".75" stop-color="#d9961c"/><stop offset="1" stop-color="#f2c45c"/></linearGradient>
 <linearGradient id="wtGoldHi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6d6" stop-opacity=".85"/><stop offset="1" stop-color="#fff6d6" stop-opacity="0"/></linearGradient>
 <linearGradient id="wtNavy" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1c3d92"/><stop offset=".6" stop-color="#0f2766"/><stop offset="1" stop-color="#0a1c4f"/></linearGradient>
 <linearGradient id="wtNavyHi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6f8fd8" stop-opacity=".35"/><stop offset="1" stop-color="#6f8fd8" stop-opacity="0"/></linearGradient>"""
    g = [f'  <path class="wt-silk" d="{d}" fill="url(#{gr})" opacity="{op}"/>' for d, gr, op in silk]
    g += [f'  <path class="wt-gold" d="{d}" fill="url(#{"wtGoldHi" if k == "hi" else "wtGold"})"/>' for k, d in gold]
    g += [f'  <path class="wt-navy" d="{d}" fill="url(#{"wtNavyHi" if k.endswith("-hi") else "wtNavy"})"/>' for k, d in navy]
    g += [f'  <path class="{c}" d="{d}" fill="none"/>' for c, d in lines]
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">\n<defs>\n'
           + defs + '\n <g id="wt-curves">\n' + "\n".join(g) + "\n </g>\n</defs>\n</svg>\n")
    (ROOT / "assets" / "wt-curves.svg").write_text(svg, encoding="utf-8")
    print(f"smooth curves: silk {len(silk)}  gold {len(gold)}  navy {len(navy)}  lines {len(lines)}  ->  {len(svg)//1024} KB")


if __name__ == "__main__":
    main()
