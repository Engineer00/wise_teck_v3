"""Colour schemes: three brand colours -> every colour on the site.

The palette in the stylesheet's :root blocks is the default scheme (Wise-Teck violet). A scheme is three
brand colours:

    primary  buttons, links, highlights, light backgrounds   (default violet  #6d28d9)
    accent   call-to-action gold                             (default gold    #d4af37)
    dark     top bar, footer, headings                       (default navy    #0d2158)

Every palette colour belongs to one of those families (by its hue and lightness). For a new scheme each colour
takes the new family hue and saturation while keeping its own lightness, so light backgrounds stay light,
text stays dark and every contrast on the site stays as readable as in the default scheme. The family's anchor
shade becomes exactly the chosen colour. Status colours (red errors, green success), white and the logo
artwork are never changed.

The result reaches the page in three ways:
    css_overrides()   a :root block in <head> that overrides the stylesheet's palette tokens
    js_map()          {default hex: new hex} for the scripts that draw (waves, 3D coin), read from <html>
    recolor_markup()  the same map applied to server-drawn SVG (background motifs, gradients)
"""
import json
import math
import re
from functools import lru_cache

from django.conf import settings

DEFAULT = {"primary": "#6d28d9", "accent": "#d4af37", "dark": "#0d2158"}

# Ready-made schemes: (key, name, primary, accent, dark). Each passes the WCAG AA checks in check_contrast().
PRESETS = [
    ("", "Wise-Teck Violet (default)", "#6d28d9", "#d4af37", "#0d2158"),
    ("ocean", "Ocean Blue", "#1d4ed8", "#f59e0b", "#0b1f3a"),
    ("emerald", "Emerald", "#047857", "#d4af37", "#0f2a24"),
    ("teal", "Teal & Coral", "#0f766e", "#fb923c", "#102a2c"),
    ("crimson", "Crimson", "#b91c1c", "#d4af37", "#2a1015"),
    ("indigo", "Royal Indigo", "#4338ca", "#eab308", "#141a4a"),
]
CUSTOM = "custom"
CHOICES = [(k, name) for k, name, *_ in PRESETS] + [(CUSTOM, "Custom colours")]
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
NEVER = ("--p-err-", "--p-ok-", "--p-red-", "--p-wordmark-", "--p-white", "--p-black")


# ----------------------------------------------------------------------------------------- colour maths
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in rgb)


def to_oklch(h):
    r, g, b = (_lin(v / 255) for v in hex_to_rgb(h))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def _oklch_to_rgb01(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (_gam(4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_),
            _gam(-1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_),
            _gam(-0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_))


def from_oklch(L, C, H):
    """OKLCH -> hex, lowering the saturation until the colour fits on screen (sRGB)."""
    L = max(0.0, min(1.0, L))
    for _ in range(40):
        rgb = _oklch_to_rgb01(L, C, H)
        if all(-0.001 <= v <= 1.001 for v in rgb):
            break
        C *= 0.92
    return rgb_to_hex(tuple(max(0.0, min(1.0, v)) * 255 for v in rgb))


def luminance(h):
    r, g, b = (_lin(v / 255) for v in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ------------------------------------------------------------------------------------- recolouring
def family(h):
    """Which brand colour a default palette colour follows: 'primary', 'accent', 'dark' or None (unchanged)."""
    L, C, H = to_oklch(h)
    if C < 0.008:                       # white, black, greys
        return None
    if 50 <= H <= 110:                  # golds, ambers
        return "accent"
    if 180 <= H <= 330:                 # blues, violets, lavenders
        return "dark" if L < 0.42 else "primary"
    return None                         # reds, greens: status colours


def recolor(h, scheme):
    fam = family(h)
    if fam is None:
        return h.lower()
    L, C, H = to_oklch(h)
    La, Ca, Ha = to_oklch(DEFAULT[fam])
    Ln, Cn, Hn = to_oklch(scheme[fam])
    pull = math.exp(-((L - La) / 0.16) ** 2)          # 1 at the anchor shade, ~0 for very light / very dark shades
    return from_oklch(L + (Ln - La) * pull, C * (Cn / Ca if Ca else 1), H + (Hn - Ha))


def resolve(settings_obj, preview=None):
    """The active scheme {'key', 'primary', 'accent', 'dark'}; None means the default (nothing to override)."""
    key = preview if preview is not None else (settings_obj.color_scheme or "")
    if key == CUSTOM:
        colours = {"primary": settings_obj.color_primary, "accent": settings_obj.color_accent, "dark": settings_obj.color_dark}
        if not all(HEX.match(v or "") for v in colours.values()):
            return None
    else:
        preset = next((p for p in PRESETS if p[0] == key), None)
        if preset is None:
            return None
        colours = {"primary": preset[2], "accent": preset[3], "dark": preset[4]}
    colours = {k: v.lower() for k, v in colours.items()}
    return None if colours == DEFAULT else {"key": key, **colours}


@lru_cache(maxsize=1)
def palette():
    """The default palette from the stylesheet: {token: hex} for --p-* colours (channel tokens converted)."""
    css = (settings.BASE_DIR / "static" / "css" / "wise-teck.css").read_text(encoding="utf8")
    roots = "".join(re.findall(r":root\s*\{([^}]*)\}", css))
    tokens = {name: value.lower() for name, value in re.findall(r"(--p-[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", roots)}
    for name, r, g, b in re.findall(r"(--p-[\w-]+-rgb):\s*(\d+)\s+(\d+)\s+(\d+)\s*;", roots):
        tokens[name] = rgb_to_hex((int(r), int(g), int(b)))
    return tokens


@lru_cache(maxsize=1)
def _drawing_colours():
    """Every colour written into the drawing scripts (waves, 3D coin) and the server-drawn motifs."""
    found = set()
    for rel in ("static/js/wt-waves.js", "static/js/hero-three.js", "core/motifs.py", "templates/base.html"):
        text = (settings.BASE_DIR / rel).read_text(encoding="utf8")
        found |= {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", text)}
        found |= {"#" + h.lower() for h in re.findall(r"0x([0-9a-fA-F]{6})\b", text)}
    return sorted(found)


def _key(scheme):
    return (scheme["primary"], scheme["accent"], scheme["dark"])


@lru_cache(maxsize=16)
def _build(key):
    scheme = dict(zip(("primary", "accent", "dark"), key))
    css = []
    for name, value in palette().items():
        if name.startswith(NEVER):
            continue
        new = recolor(value, scheme)
        if new == value:
            continue
        css.append(f"{name}:{' '.join(str(v) for v in hex_to_rgb(new))}" if name.endswith("-rgb") else f"{name}:{new}")
    mapping = {h: recolor(h, scheme) for h in _drawing_colours()}
    mapping = {k: v for k, v in mapping.items() if k != v}
    return ":root{" + ";".join(css) + "}", json.dumps(mapping, separators=(",", ":")), mapping


def css_overrides(scheme):
    return _build(_key(scheme))[0] if scheme else ""


def js_map(scheme):
    return _build(_key(scheme))[1] if scheme else ""


def recolor_markup(markup, scheme):
    if not scheme:
        return markup
    mapping = _build(_key(scheme))[2]
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapping.get(m.group(0).lower(), m.group(0)), markup)


def check_contrast(primary, accent, dark):
    """WCAG AA (4.5:1) for the pairs the design uses. Returns a list of problems in plain words."""
    scheme = {"primary": primary.lower(), "accent": accent.lower(), "dark": dark.lower()}
    problems = []
    if contrast(primary, "#ffffff") < 4.5:
        problems.append("White button text is hard to read on the primary colour — choose a darker primary colour.")
    if contrast(dark, "#ffffff") < 4.5:
        problems.append("White text in the top bar and footer is hard to read on the dark colour — choose a darker colour.")
    if contrast(accent, recolor("#10123f", scheme)) < 4.5:
        problems.append("Dark text on the accent (gold) buttons is hard to read — choose a lighter, brighter accent colour.")
    return problems
