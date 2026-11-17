"""Symmetric wave art for the Wise-Teck v3 site — one self-contained SVG symbol per placement.

Industry-standard structure: sections size to their content; waves live in dedicated pieces:
  #wv-hero     hero bottom art      (1440 x 320)  silk strands + mirrored gold/navy corner sweeps
  #wv-div-a    section divider      (1440 x 130)  silk ribbon set, crest up in the middle
  #wv-div-b    section divider      (1440 x 130)  same set mirrored vertically (alternates with -a)
  #wv-foot     footer top art       (1440 x 170)  silk + symmetric navy wave + gold thick-thin-thick

Every curve is symmetric about the page centre and has gentle extra bends:
    s(x) = A1*cos(t) + A2*cos(2t),   t = 2*pi*(x - W/2) / W

No white anywhere: satin fills and strand lines are lavender / violet tones.
    python tools/draw_waves.py
"""
from pathlib import Path

import numpy as np

from trace_profiles import catmull_open

ROOT = Path(__file__).resolve().parent.parent
W = 1440
X = np.linspace(0, W, 121)                        # 12px spacing; curves are exact cosine sums
T = 2 * np.pi * (X - W / 2) / W


def s(a1, a2=0.0):
    return a1 * np.cos(T) + a2 * np.cos(2 * T)


def edge_weight(start=0.5):
    """0 across the middle, rising smoothly to 1 at both page edges (corner sweeps)."""
    u = np.clip((np.abs(2 * X / W - 1) - start) / (1 - start), 0, 1)
    return u * u * u * (u * (6 * u - 15) + 10)


def d_open(ys):
    pts = list(zip(X, ys))
    return f"M{pts[0][0]:.0f} {pts[0][1]:.1f} " + catmull_open(pts)


def d_band(top, bot):
    t = list(zip(X, top)); b = list(zip(X[::-1], bot[::-1]))
    return (f"M{t[0][0]:.0f} {t[0][1]:.1f} " + catmull_open(t) + f" L{b[0][0]:.0f} {b[0][1]:.1f} "
            + catmull_open(b) + " Z")


def silk_paths(base, a1, a2, n, gap, strong=False, w=None):
    """n parallel strands on one symmetric wave + two satin fills, all lavender."""
    w = s(a1, a2) if w is None else w
    st = [base + w + k * gap for k in range(n)]
    out = [f'<path class="wt-silk" d="{d_band(st[0], st[-1])}" fill="url(#wvSilkA)" opacity="{.6 if strong else .5}"/>',
           f'<path class="wt-silk" d="{d_band(st[0], st[len(st) // 2])}" fill="url(#wvSilkB)" opacity="{.65 if strong else .55}"/>']
    for k, y in enumerate(st):
        out.append(f'<path class="{"wt-lav" if k in (0, n - 1) else "wt-lav wt-lav-m"}" d="{d_open(y)}" fill="none"/>')
    return out


def group(gid, items):
    return f' <g id="{gid}">\n  ' + "\n  ".join(items) + "\n </g>"


# ---------------------------------------------------------------- hero bottom (1440 x 240)
# As in the reference JPEG: lavender silk ribbons flow in from the lower left, swell softly behind the
# pedestal, then sweep up into a gold + navy ribbon that rises steeply into the RIGHT edge; a pale
# crest runs underneath. Every curve is a smooth Catmull-Rom spline through a few anchor points.
HH = 320


def cr_sample(anchors, xs):
    """Evaluate a Catmull-Rom spline through (x, y) anchors at xs (anchors sorted by x)."""
    P = np.asarray(anchors, float)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = np.empty_like(xs, dtype=float)
    for j, x in enumerate(xs):
        i = int(np.clip(np.searchsorted(P[1:-1, 0], x) - 1, 0, len(P) - 4)) + 1
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t = (x - p1[0]) / max(1e-6, p2[0] - p1[0])
        out[j] = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t * t
                        + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t ** 3)
    return out


def _smooth01(t):
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (6 * t - 15) + 10)


# Silk with FLOW (reference + owner): many fine strands following ONE shared path, evenly spaced,
# like threads in satin. They enter low on the left, swell softly under the stage, then rise and
# draw together into the gold sweep on the right (and slip under it). Satin fill between them.
hero = []
FLOW = cr_sample([(0, 150), (480, 186), (920, 160), (1200, 118), (1440, 66)], X)   # few anchors = one smooth sweep
NS = 12
gap = 7.5 - 3.5 * _smooth01(X / W)                          # wider on the left, drawing together to the right
strands = [FLOW + k * gap for k in range(NS)]
# soft wash under the flow, fading out before the section edge (no hard line)
hero.append(f'<path d="{d_band(strands[0] - 6, strands[-1] + 46)}" fill="url(#wvWash)"/>')   # ends INSIDE the hero, fully faded
# satin body: full width of the flow, then a brighter core band
hero.append(f'<path class="wt-silk" d="{d_band(strands[0], strands[-1])}" fill="url(#wvRibA)" opacity=".5"/>')
hero.append(f'<path class="wt-silk" d="{d_band(strands[3], strands[8])}" fill="url(#wvRibB)" opacity=".55"/>')
# the strands themselves: finest and faintest at the outer edges, fuller in the middle
for k, y in enumerate(strands):
    m = np.sin(np.pi * (k + 0.5) / NS)
    hero.append(f'<path class="wt-flow" d="{d_open(y)}" fill="none" stroke-width="{0.7 + 0.8 * m:.2f}" stroke-opacity="{0.35 + 0.5 * m:.2f}"/>')

# gold + navy sweep (reference): one long ribbon that starts as a fine tip low in the hero and
# climbs in a single smooth, ever-steeper curve into the right edge. The navy fills the corner
# beneath it as a crescent with a CURVED bottom edge (no flat cuts anywhere). Drawn on its own
# x-range so no zero-width slivers run across the page.
XR = np.linspace(860, W, 80)
u = (XR - 860) / (W - 860)                                  # 0 at the tip -> 1 at the right edge
g_top = (HH - 46) - (HH - 46 - 30) * u ** 2.1               # tip sits well inside the hero; steep into the edge
g_th = 26 * _smooth01(u / 0.38)                             # fine tip, full ribbon after ~40 %
n_top = g_top + g_th
n_bot = (HH - 40) - 30 * u ** 2.2                           # smooth convex bottom, kept inside the hero
n_bot = n_top + np.maximum(n_bot - n_top, 0) * _smooth01((u - 0.1) / 0.4)   # navy grows out of the gold tip - no sliver


def band_xy(xs, top, bot):
    t = list(zip(xs, top)); b = list(zip(xs[::-1], bot[::-1]))
    return (f"M{t[0][0]:.0f} {t[0][1]:.1f} " + catmull_open(t) + f" L{b[0][0]:.0f} {b[0][1]:.1f} "
            + catmull_open(b) + " Z")


hero += [f'<path class="wt-gold" d="{band_xy(XR, g_top, np.minimum(n_top + 12 * _smooth01(u / 0.38), n_bot))}" fill="url(#wvGold)"/>',
         f'<path d="{band_xy(XR, g_top, g_top + g_th * 0.42)}" fill="url(#wvGoldHi)"/>',
         f'<path class="wt-navy" d="{band_xy(XR, n_top, n_bot)}" fill="url(#wvNavyR)"/>',
         f'<path d="{band_xy(XR, n_top, np.minimum(n_top + 7 * _smooth01(u / 0.38), n_bot))}" fill="url(#wvNavyHi)"/>']

# ---------------------------------------------------------------- section divider (1440 x 130)
# Reference style: soft silk swooshes sweep in from the page edges and fade out before the centre
# (About bottom-left, Ecosystem left + right edges, Programs bottom-left, Services top-right in the JPEG).
# Mirrored on both edges for symmetry; the middle of the page stays clear.
DH = 130
HX = np.linspace(0, W * 0.5, 41)                           # left half; right half is the mirror


def _ss(t):
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (6 * t - 15) + 10)


def swoosh(base, rise, thick, n=3, reach=0.46):
    """One edge swoosh pair: a ribbon that curves up (rise>0) or down into the edge, thinning to a point."""
    u = HX / (W * reach)                                   # 0 at the edge -> 1 where it vanishes
    taper = 1 - _ss(u)                                     # full at the edge, 0 at the tip
    centre = base - rise * (1 - np.clip(u, 0, 1)) ** 2     # bends into the edge
    out = []
    for side in (1, -1):                                   # left, then mirrored right
        xs = HX if side == 1 else W - HX
        def path_band(top, bot):
            t = list(zip(xs, top)); b = list(zip(xs[::-1], bot[::-1]))
            return f"M{t[0][0]:.0f} {t[0][1]:.1f} " + catmull_open(t) + f" L{b[0][0]:.0f} {b[0][1]:.1f} " + catmull_open(b) + " Z"
        def path_line(y):
            p = list(zip(xs, y)); return f"M{p[0][0]:.0f} {p[0][1]:.1f} " + catmull_open(p)
        top = centre - thick * taper / 2
        bot = centre + thick * taper / 2
        grad = "wvFadeL" if side == 1 else "wvFadeR"
        out.append(f'<path class="wt-silk" d="{path_band(top, bot)}" fill="url(#{grad})"/>')
        out.append(f'<path class="wt-silk" d="{path_band(top, centre)}" fill="url(#{grad}2)"/>')
        for k in range(n):
            f = k / (n - 1)
            out.append(f'<path class="wt-lav{"" if k in (0, n - 1) else " wt-lav-m"}" d="{path_line(top + (bot - top) * f)}" fill="none" style="stroke:url(#{grad}L)"/>')
    return out


div_a = swoosh(DH * 0.62, 44, 46)                          # swooshes curve UP into both edges
div_b = swoosh(DH * 0.40, -44, 46)                         # swooshes curve DOWN into both edges

# ---------------------------------------------------------------- footer top (1440 x 170)
# Static fallback = the same design as the live footer wave in assets/js/wt-waves.js:
# three even, symmetric crests; two lavender layers; slim gold ribbon; flat navy #24397f (= footer body).
FH = 170
y_f = 104 + 8 * np.cos(T) + 18 * 0.93 * np.cos(3 * T)
thick = 9 + 9 * np.abs(2 * X / W - 1) ** 2
foot = [f'<path class="wt-silk" d="{d_band(y_f - thick - 48, y_f - thick - 30)}" fill="#b9c2f2" opacity=".45"/>',
        f'<path class="wt-silk" d="{d_band(y_f - thick - 24, y_f - thick - 4)}" fill="#a6b0ec" opacity=".65"/>',
        f'<path class="wt-gold" d="{d_band(y_f - thick, y_f + 14)}" fill="url(#wvGold)"/>',
        f'<path d="{d_band(y_f - thick, y_f - thick * 0.5)}" fill="url(#wvGoldHi)"/>',
        f'<path class="wt-navy" d="{d_band(y_f, np.full_like(y_f, FH + 1))}" fill="#24397f"/>',
        f'<path d="{d_band(y_f, y_f + 7)}" fill="#9db4ee" opacity=".32"/>']

defs = """ <linearGradient id="wvSilkA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dde2fb"/><stop offset="1" stop-color="#b3bdf0"/></linearGradient>
 <linearGradient id="wvSilkB" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c7cff5" stop-opacity=".85"/><stop offset=".5" stop-color="#dcd6fb" stop-opacity=".55"/><stop offset="1" stop-color="#c7cff5" stop-opacity=".85"/></linearGradient>
 <linearGradient id="wvFadeL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b3bdf0" stop-opacity=".85"/><stop offset=".6" stop-color="#c9cff6" stop-opacity=".45"/><stop offset="1" stop-color="#dfe3fa" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvFadeR" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#b3bdf0" stop-opacity=".85"/><stop offset=".6" stop-color="#c9cff6" stop-opacity=".45"/><stop offset="1" stop-color="#dfe3fa" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvFadeL2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#dcd6fb" stop-opacity=".8"/><stop offset="1" stop-color="#dcd6fb" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvFadeR2" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#dcd6fb" stop-opacity=".8"/><stop offset="1" stop-color="#dcd6fb" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvFadeLL" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="660" y2="0"><stop offset="0" stop-color="#9aa6ea"/><stop offset="1" stop-color="#c9cff6" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvFadeRL" gradientUnits="userSpaceOnUse" x1="1440" y1="0" x2="780" y2="0"><stop offset="0" stop-color="#9aa6ea"/><stop offset="1" stop-color="#c9cff6" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvGold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f2c45c"/><stop offset=".15" stop-color="#d9961c"/><stop offset=".5" stop-color="#f6d27c"/><stop offset=".85" stop-color="#d9961c"/><stop offset="1" stop-color="#f2c45c"/></linearGradient>
 <linearGradient id="wvGoldHi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3c8" stop-opacity=".8"/><stop offset="1" stop-color="#fff3c8" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvNavy" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c3d92"/><stop offset=".5" stop-color="#0d2158"/><stop offset="1" stop-color="#1c3d92"/></linearGradient>
 <linearGradient id="wvWash" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d3d9f8" stop-opacity=".7"/><stop offset=".45" stop-color="#e2e6fb" stop-opacity=".4"/><stop offset=".8" stop-color="#eef0fc" stop-opacity="0"/></linearGradient>
 <linearGradient id="wvRibA" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a9b4ec"/><stop offset=".5" stop-color="#bcc4f1"/><stop offset="1" stop-color="#a3aeea"/></linearGradient>
 <linearGradient id="wvRibB" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cfd5f7"/><stop offset=".5" stop-color="#d9d3fa"/><stop offset="1" stop-color="#c3cbf4"/></linearGradient>
 <linearGradient id="wvRibC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c6bff6"/><stop offset="1" stop-color="#9fa9e9"/></linearGradient>
 <linearGradient id="wvNavyR" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0d2158"/><stop offset="1" stop-color="#1c3d92"/></linearGradient>
 <linearGradient id="wvNavyHi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d9be0" stop-opacity=".4"/><stop offset="1" stop-color="#7d9be0" stop-opacity="0"/></linearGradient>"""

svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">\n<defs>\n'
       + defs + "\n" + "\n".join([group("wv-hero", hero), group("wv-div-a", div_a), group("wv-div-b", div_b), group("wv-foot", foot)])
       + "\n</defs>\n</svg>\n")
(ROOT / "assets" / "wt-curves.svg").write_text(svg, encoding="utf-8")
print(f"wave symbols: hero {len(hero)}  div-a {len(div_a)}  div-b {len(div_b)}  foot {len(foot)}  ->  {len(svg) // 1024} KB")
