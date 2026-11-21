"""Section background motifs for the Wise-Teck v3 site — lavender / violet palette, drawn as inline SVG.

Each motif is decorative only (aria-hidden), sits behind the section content and is kept faint so text
stays readable. Generation is deterministic (fixed random seed) so rebuilds are identical.

    motif("hero" | "eco" | "programs" | "services" | "stories" | "collab" | "footer")  -> HTML string
"""
import math
import random

LAV = "#a9b3ee"      # lavender line colour
VIO = "#7b5cf0"      # violet accent
SOFT = "#c9cff6"


def _svg(vb, body, cls):
    return f'<svg class="motif {cls}" viewBox="{vb}" aria-hidden="true" focusable="false">{body}</svg>'


# ------------------------------------------------------------------ hero: globe network
def globe():
    r, cx, cy = 250, 260, 260
    p = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#mgGlow)"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LAV}" stroke-width="1.2"/>']
    for k in range(1, 6):                                       # meridians
        rx = r * math.cos(math.pi / 2 * k / 6)
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{r}" fill="none" stroke="{LAV}" stroke-width=".8" opacity=".8"/>')
    for k in range(-4, 5):                                      # parallels
        y = cy + r * math.sin(math.pi / 2 * k / 5)
        rx = r * math.cos(math.pi / 2 * k / 5)
        p.append(f'<ellipse cx="{cx}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rx * .16:.1f}" fill="none" stroke="{LAV}" stroke-width=".7" opacity=".7"/>')
    rnd = random.Random(7)
    nodes = []
    for _ in range(16):
        a, b = rnd.uniform(0, 2 * math.pi), rnd.uniform(-1.1, 1.1)
        x = cx + r * .92 * math.cos(b) * math.cos(a)
        y = cy + r * .92 * math.sin(b)
        nodes.append((x, y))
    for i in range(len(nodes)):                                 # arcs between nearby nodes
        (x1, y1), (x2, y2) = nodes[i], nodes[(i + 3) % len(nodes)]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 40
        p.append(f'<path d="M{x1:.0f} {y1:.0f} Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="{VIO}" stroke-width="1" opacity=".55"/>')
    for x, y in nodes:
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{VIO}" opacity=".18"/><circle cx="{x:.0f}" cy="{y:.0f}" r="2.6" fill="{VIO}"/>')
    defs = ('<defs><radialGradient id="mgGlow"><stop offset="0" stop-color="#e6e2fd" stop-opacity=".9"/>'
            '<stop offset="1" stop-color="#e6e2fd" stop-opacity="0"/></radialGradient></defs>')
    return _svg("0 0 520 520", defs + "".join(p), "m-globe")


# ------------------------------------------------------------------ ecosystem: circuit connectors
def circuits(flip=False):
    rows = [(40, [(0, 40), (150, 40), (180, 70), (330, 70)]), (95, [(0, 95), (260, 95)]),
            (150, [(0, 150), (130, 150), (160, 120), (300, 120)])]
    p = []
    for _, pts in rows:
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        p.append(f'<path d="{d}" fill="none" stroke="{LAV}" stroke-width="1.4"/>')
        for x, y in pts[1:]:
            p.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" stroke="{VIO}" stroke-width="1.6"/>')
    tr = ' transform="translate(340 0) scale(-1 1)"' if flip else ""
    return _svg("0 0 340 190", f"<g{tr}>{''.join(p)}</g>", "m-circuit" + (" r" if flip else " l"))


def dots(cls):
    return f'<div class="motif m-dots {cls}" aria-hidden="true"></div>'


# ------------------------------------------------------------------ services: hexagon network
def hexnet(flip=False):
    s, p, rnd = 34, [], random.Random(3)
    w3 = s * math.sqrt(3)
    for row in range(7):
        for col in range(6):
            cx = col * w3 + (w3 / 2 if row % 2 else 0)
            cy = row * s * 1.5
            pts = [(cx + s * math.cos(math.pi / 6 + k * math.pi / 3), cy + s * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
            p.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{LAV}" stroke-width="1"/>')
            if rnd.random() < .35:
                x, y = pts[rnd.randrange(6)]
                p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{VIO}" opacity=".7"/>')
    tr = ' transform="translate(360 0) scale(-1 1)"' if flip else ""
    return _svg("0 0 360 330", f"<g{tr}>{''.join(p)}</g>", "m-hex" + (" r" if flip else " l"))


# ------------------------------------------------------------------ partners: skyline
def skyline(flip=False):
    rnd, x, p = random.Random(11 if flip else 5), 0, []
    while x < 480:
        w = rnd.randint(14, 34)
        h = rnd.randint(30, 110) * (1.15 - x / 700)
        p.append(f'<rect x="{x}" y="{140 - h:.0f}" width="{w}" height="{h:.0f}" rx="2" fill="{SOFT}"/>')
        if rnd.random() < .18:
            p.append(f'<rect x="{x + w / 2 - 1.5:.1f}" y="{140 - h - 26:.0f}" width="3" height="26" fill="{SOFT}"/>')
        x += w + rnd.randint(2, 6)
    tr = ' transform="translate(480 0) scale(-1 1)"' if flip else ""
    return _svg("0 0 480 140", f"<g{tr}>{''.join(p)}</g>", "m-sky" + (" r" if flip else " l"))


# ------------------------------------------------------------------ footer: dotted world map + network
CONTINENTS = [
    [(-168, 65), (-140, 70), (-95, 72), (-75, 62), (-60, 50), (-80, 25), (-97, 18), (-105, 22), (-118, 32), (-125, 48), (-140, 58)],
    [(-55, 82), (-25, 80), (-20, 70), (-45, 60), (-55, 70)],
    [(-80, 10), (-60, 8), (-35, -7), (-40, -22), (-58, -38), (-70, -55), (-75, -40), (-72, -15), (-80, -2)],
    [(-10, 36), (-9, 44), (-5, 48), (5, 52), (10, 58), (20, 70), (30, 70), (40, 62), (40, 45), (28, 40), (15, 38)],
    [(-17, 15), (-12, 30), (10, 37), (32, 31), (43, 12), (51, 12), (40, -15), (35, -25), (20, -35), (12, -18), (8, 4), (-8, 5)],
    [(40, 45), (40, 62), (60, 70), (100, 78), (140, 72), (170, 65), (160, 55), (140, 48), (130, 35), (120, 22), (108, 10),
     (100, 15), (90, 22), (78, 8), (70, 22), (58, 25), (50, 30), (40, 40)],
    [(95, 5), (120, 5), (140, -5), (125, -10), (105, -7)],
    [(113, -22), (130, -12), (145, -15), (153, -28), (145, -38), (130, -32), (115, -34)],
]


def _inside(x, y, poly):
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def worldmap():
    p, step = [], 4.5
    lat = 80
    while lat > -58:
        lon = -170
        while lon < 180:
            if any(_inside(lon, lat, poly) for poly in CONTINENTS):
                x, y = (lon + 180) * 1.6, (80 - lat) * 1.6
                p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.9"/>')
            lon += step
        lat -= step
    return _svg("0 0 576 222", f'<g fill="#a9b8f0">{"".join(p)}</g>', "m-map")


def network():
    rnd = random.Random(19)
    pts = [(rnd.uniform(10, 470), rnd.uniform(10, 210)) for _ in range(22)]
    p = []
    for i, (x1, y1) in enumerate(pts):
        near = sorted(pts, key=lambda q: (q[0] - x1) ** 2 + (q[1] - y1) ** 2)[1:3]
        for x2, y2 in near:
            p.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#8fa6ee" stroke-width=".9" opacity=".7"/>')
    for x, y in pts:
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="#b9a8ff" opacity=".18"/><circle cx="{x:.0f}" cy="{y:.0f}" r="2.2" fill="#d9d0ff"/>')
    return _svg("0 0 480 220", "".join(p), "m-net")


def motif(kind):
    if kind == "hero":
        return globe() + dots("m-dots-hero")
    if kind == "inner-hero":                     # compact inner page header: calmer, dots only
        return dots("m-dots-hero")
    if kind == "eco":
        return circuits() + circuits(True) + dots("m-dots-tl") + dots("m-dots-tr")
    if kind == "programs":
        return '<div class="motif m-cap" aria-hidden="true"><i class="fa-solid fa-graduation-cap"></i><i class="fa-solid fa-book"></i></div>'
    if kind == "services":
        return hexnet() + hexnet(True)
    if kind == "stories":
        return '<div class="motif m-quote l" aria-hidden="true">&ldquo;</div><div class="motif m-quote r" aria-hidden="true">&rdquo;</div>'
    if kind == "collab":
        return skyline() + skyline(True) + '<div class="motif m-hand" aria-hidden="true"><i class="fa-solid fa-handshake"></i></div>'
    if kind == "footer":
        return worldmap() + network()
    return ""
