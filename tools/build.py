"""Build the Wise-Teck v3 static site (home + inner pages) from one shared layout.

    python tools/build.py

- Curves: assets/wt-curves.svg (traced from the reference by tools/trace_profiles.py) is inlined
  into every page; each section shows its own slice of it (see slice()).
- Home section heights are locked to the reference (assets/wt-sections.json) so traced curves land
  exactly where they are in the JPEG. Inner pages reuse the hero, divider and footer slices.
- Wording comes from "eco system (5).pdf". Anything the PDF does not cover is shown as a clearly
  marked placeholder — never invented.
- Photos are the ones the Stitch pages already use (generic campus/lab/workspace shots only).
"""
import json
import re
from html import escape
from pathlib import Path

from motifs import motif

ROOT = Path(__file__).resolve().parent.parent
STITCH = ROOT.parent / "stitch_wise_teck_multi_page_website"
SPRITE = (ROOT / "assets" / "wt-curves.svg").read_text(encoding="utf-8")
import time
ASSET_V = time.strftime("%Y%m%d%H%M%S")   # cache-buster: browsers re-fetch CSS/JS after every build
SECS = json.loads((ROOT / "assets" / "wt-sections.json").read_text())


# ---------------------------------------------------------------- images from the Stitch pages
def load_images():
    out = {}
    for d in sorted(STITCH.glob("page_*")):
        f = d / "code.stitch-original.html"
        if not f.exists():
            f = d / "code.html"
        if not f.exists():
            continue
        key = d.name[5:7]
        if d.name.startswith("page_01_homepage_wise"):
            key = "01"
        elif d.name.startswith("page_01"):
            continue
        out[key] = re.findall(r'<img[^>]*?src="([^"]+)"', f.read_text(encoding="utf-8", errors="ignore"))
    return out


IMG = load_images()


def img(page, i):
    lst = IMG.get(page) or []
    return lst[i] if i < len(lst) else ""


# ---------------------------------------------------------------- site map
PAGES = {
    "home": "index.html", "about": "about.html", "hub": "wise-support-hub.html", "college": "wise-college.html",
    "courses": "professional-paid-courses.html",
    "centre": "earning-centre.html", "blocks": "earning-blocks.html", "corporate": "corporate-services.html",
    "incubation": "business-incubation.html", "loan": "student-loan-scheme.html", "placement": "placement.html",
    "stories": "success-stories.html", "contact": "contact.html",
}
P = PAGES

NAV = [
    ("Home", "home", None),
    ("About", "about", [("About Wise-Teck", P["about"]), ("Vision &amp; Objectives", P["about"] + "#objectives"),
                        ("Success Stories", P["stories"])]),
    ("Programs", "programs", [("Wise Support Hub", P["hub"]), ("Wise College Degree Programs", P["college"]),
                              ("Professional Paid Courses", P["courses"])]),
    ("Services", "services", [("Corporate Technology Services", P["corporate"]),
                              ("Business Incubation Centre", P["incubation"]),
                              ("Student Loan Scheme", P["loan"])]),
    ("Earning Centre", "centre", [("Wise-Teck Earning Centre", P["centre"]), ("Our Earning Blocks", P["blocks"])]),
    ("Placement", "placement", None),
    ("Contact", "contact", None),
]
SECTION_OF = {"about": "about", "stories": "about", "hub": "programs", "college": "programs",
              "courses": "programs", "corporate": "services", "incubation": "services", "loan": "services",
              "centre": "centre", "blocks": "centre", "placement": "placement", "contact": "contact", "home": "home"}

PROGRAMS = [
    ("hub", "fa-users", "Wise Support Hub", "Fully Funded Educational &amp; Skills Training Program &middot; Intermediate Level"),
    ("college", "fa-graduation-cap", "Wise College", "Higher Education with Professional Skills &middot; Degree Level Program"),
    ("courses", "fa-layer-group", "Professional Paid Courses", "Paid courses for students, graduates, and working professionals."),
]


# ---------------------------------------------------------------- layout pieces
def art(sym, h, cls):
    """One self-contained wave symbol from assets/wt-curves.svg (tools/draw_waves.py)."""
    return (f'<svg class="{cls}" viewBox="0 0 1440 {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<use href="#{sym}"/></svg>')


HERO_ART = art("wv-hero", 320, "wv-hero-art") + motif("hero")            # home hero: full wave + globe motif
INNER_HERO_ART = '<div class="ph-bg" aria-hidden="true"><i class="ph-grid"></i><svg class="ph-wave" viewBox="0 0 1440 170" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="phG1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eceef5"/><stop offset=".5" stop-color="#d5d9e6"/><stop offset="1" stop-color="#c3c8d9"/></linearGradient><linearGradient id="phG2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#eef0f6"/><stop offset="1" stop-color="#dde0ea"/></linearGradient><filter id="phSh" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="5"/></filter></defs><path d="M0,170 L0,30.0 L6,30.1 L12,30.2 L18,30.6 L24,31.0 L30,31.5 L36,32.2 L42,32.9 L48,33.8 L54,34.8 L60,35.9 L66,37.0 L72,38.2 L78,39.6 L84,40.9 L90,42.3 L96,43.8 L102,45.3 L108,46.9 L114,48.4 L120,50.0 L126,51.6 L132,53.1 L138,54.7 L144,56.2 L150,57.7 L156,59.1 L162,60.4 L168,61.8 L174,63.0 L180,64.1 L186,65.2 L192,66.2 L198,67.1 L204,67.8 L210,68.5 L216,69.0 L222,69.4 L228,69.8 L234,69.9 L240,70.0 L246,69.9 L252,69.8 L258,69.4 L264,69.0 L270,68.5 L276,67.8 L282,67.1 L288,66.2 L294,65.2 L300,64.1 L306,63.0 L312,61.8 L318,60.4 L324,59.1 L330,57.7 L336,56.2 L342,54.7 L348,53.1 L354,51.6 L360,50.0 L366,48.4 L372,46.9 L378,45.3 L384,43.8 L390,42.3 L396,40.9 L402,39.6 L408,38.2 L414,37.0 L420,35.9 L426,34.8 L432,33.8 L438,32.9 L444,32.2 L450,31.5 L456,31.0 L462,30.6 L468,30.2 L474,30.1 L480,30.0 L486,30.1 L492,30.2 L498,30.6 L504,31.0 L510,31.5 L516,32.2 L522,32.9 L528,33.8 L534,34.8 L540,35.9 L546,37.0 L552,38.2 L558,39.6 L564,40.9 L570,42.3 L576,43.8 L582,45.3 L588,46.9 L594,48.4 L600,50.0 L606,51.6 L612,53.1 L618,54.7 L624,56.2 L630,57.7 L636,59.1 L642,60.4 L648,61.8 L654,63.0 L660,64.1 L666,65.2 L672,66.2 L678,67.1 L684,67.8 L690,68.5 L696,69.0 L702,69.4 L708,69.8 L714,69.9 L720,70.0 L726,69.9 L732,69.8 L738,69.4 L744,69.0 L750,68.5 L756,67.8 L762,67.1 L768,66.2 L774,65.2 L780,64.1 L786,63.0 L792,61.8 L798,60.4 L804,59.1 L810,57.7 L816,56.2 L822,54.7 L828,53.1 L834,51.6 L840,50.0 L846,48.4 L852,46.9 L858,45.3 L864,43.8 L870,42.3 L876,40.9 L882,39.6 L888,38.2 L894,37.0 L900,35.9 L906,34.8 L912,33.8 L918,32.9 L924,32.2 L930,31.5 L936,31.0 L942,30.6 L948,30.2 L954,30.1 L960,30.0 L966,30.1 L972,30.2 L978,30.6 L984,31.0 L990,31.5 L996,32.2 L1002,32.9 L1008,33.8 L1014,34.8 L1020,35.9 L1026,37.0 L1032,38.2 L1038,39.6 L1044,40.9 L1050,42.3 L1056,43.8 L1062,45.3 L1068,46.9 L1074,48.4 L1080,50.0 L1086,51.6 L1092,53.1 L1098,54.7 L1104,56.2 L1110,57.7 L1116,59.1 L1122,60.4 L1128,61.8 L1134,63.0 L1140,64.1 L1146,65.2 L1152,66.2 L1158,67.1 L1164,67.8 L1170,68.5 L1176,69.0 L1182,69.4 L1188,69.8 L1194,69.9 L1200,70.0 L1206,69.9 L1212,69.8 L1218,69.4 L1224,69.0 L1230,68.5 L1236,67.8 L1242,67.1 L1248,66.2 L1254,65.2 L1260,64.1 L1266,63.0 L1272,61.8 L1278,60.4 L1284,59.1 L1290,57.7 L1296,56.2 L1302,54.7 L1308,53.1 L1314,51.6 L1320,50.0 L1326,48.4 L1332,46.9 L1338,45.3 L1344,43.8 L1350,42.3 L1356,40.9 L1362,39.6 L1368,38.2 L1374,37.0 L1380,35.9 L1386,34.8 L1392,33.8 L1398,32.9 L1404,32.2 L1410,31.5 L1416,31.0 L1422,30.6 L1428,30.2 L1434,30.1 L1440,30.0 L1440,170 Z" fill="url(#phG1)"/><path d="M0,30.0 L6,30.1 L12,30.2 L18,30.6 L24,31.0 L30,31.5 L36,32.2 L42,32.9 L48,33.8 L54,34.8 L60,35.9 L66,37.0 L72,38.2 L78,39.6 L84,40.9 L90,42.3 L96,43.8 L102,45.3 L108,46.9 L114,48.4 L120,50.0 L126,51.6 L132,53.1 L138,54.7 L144,56.2 L150,57.7 L156,59.1 L162,60.4 L168,61.8 L174,63.0 L180,64.1 L186,65.2 L192,66.2 L198,67.1 L204,67.8 L210,68.5 L216,69.0 L222,69.4 L228,69.8 L234,69.9 L240,70.0 L246,69.9 L252,69.8 L258,69.4 L264,69.0 L270,68.5 L276,67.8 L282,67.1 L288,66.2 L294,65.2 L300,64.1 L306,63.0 L312,61.8 L318,60.4 L324,59.1 L330,57.7 L336,56.2 L342,54.7 L348,53.1 L354,51.6 L360,50.0 L366,48.4 L372,46.9 L378,45.3 L384,43.8 L390,42.3 L396,40.9 L402,39.6 L408,38.2 L414,37.0 L420,35.9 L426,34.8 L432,33.8 L438,32.9 L444,32.2 L450,31.5 L456,31.0 L462,30.6 L468,30.2 L474,30.1 L480,30.0 L486,30.1 L492,30.2 L498,30.6 L504,31.0 L510,31.5 L516,32.2 L522,32.9 L528,33.8 L534,34.8 L540,35.9 L546,37.0 L552,38.2 L558,39.6 L564,40.9 L570,42.3 L576,43.8 L582,45.3 L588,46.9 L594,48.4 L600,50.0 L606,51.6 L612,53.1 L618,54.7 L624,56.2 L630,57.7 L636,59.1 L642,60.4 L648,61.8 L654,63.0 L660,64.1 L666,65.2 L672,66.2 L678,67.1 L684,67.8 L690,68.5 L696,69.0 L702,69.4 L708,69.8 L714,69.9 L720,70.0 L726,69.9 L732,69.8 L738,69.4 L744,69.0 L750,68.5 L756,67.8 L762,67.1 L768,66.2 L774,65.2 L780,64.1 L786,63.0 L792,61.8 L798,60.4 L804,59.1 L810,57.7 L816,56.2 L822,54.7 L828,53.1 L834,51.6 L840,50.0 L846,48.4 L852,46.9 L858,45.3 L864,43.8 L870,42.3 L876,40.9 L882,39.6 L888,38.2 L894,37.0 L900,35.9 L906,34.8 L912,33.8 L918,32.9 L924,32.2 L930,31.5 L936,31.0 L942,30.6 L948,30.2 L954,30.1 L960,30.0 L966,30.1 L972,30.2 L978,30.6 L984,31.0 L990,31.5 L996,32.2 L1002,32.9 L1008,33.8 L1014,34.8 L1020,35.9 L1026,37.0 L1032,38.2 L1038,39.6 L1044,40.9 L1050,42.3 L1056,43.8 L1062,45.3 L1068,46.9 L1074,48.4 L1080,50.0 L1086,51.6 L1092,53.1 L1098,54.7 L1104,56.2 L1110,57.7 L1116,59.1 L1122,60.4 L1128,61.8 L1134,63.0 L1140,64.1 L1146,65.2 L1152,66.2 L1158,67.1 L1164,67.8 L1170,68.5 L1176,69.0 L1182,69.4 L1188,69.8 L1194,69.9 L1200,70.0 L1206,69.9 L1212,69.8 L1218,69.4 L1224,69.0 L1230,68.5 L1236,67.8 L1242,67.1 L1248,66.2 L1254,65.2 L1260,64.1 L1266,63.0 L1272,61.8 L1278,60.4 L1284,59.1 L1290,57.7 L1296,56.2 L1302,54.7 L1308,53.1 L1314,51.6 L1320,50.0 L1326,48.4 L1332,46.9 L1338,45.3 L1344,43.8 L1350,42.3 L1356,40.9 L1362,39.6 L1368,38.2 L1374,37.0 L1380,35.9 L1386,34.8 L1392,33.8 L1398,32.9 L1404,32.2 L1410,31.5 L1416,31.0 L1422,30.6 L1428,30.2 L1434,30.1 L1440,30.0" fill="none" stroke="#fff" stroke-opacity=".95" stroke-width="2" vector-effect="non-scaling-stroke"/><path d="M0,48.0 L6,48.1 L12,48.2 L18,48.6 L24,49.0 L30,49.5 L36,50.2 L42,50.9 L48,51.8 L54,52.8 L60,53.9 L66,55.0 L72,56.2 L78,57.6 L84,58.9 L90,60.3 L96,61.8 L102,63.3 L108,64.9 L114,66.4 L120,68.0 L126,69.6 L132,71.1 L138,72.7 L144,74.2 L150,75.7 L156,77.1 L162,78.4 L168,79.8 L174,81.0 L180,82.1 L186,83.2 L192,84.2 L198,85.1 L204,85.8 L210,86.5 L216,87.0 L222,87.4 L228,87.8 L234,87.9 L240,88.0 L246,87.9 L252,87.8 L258,87.4 L264,87.0 L270,86.5 L276,85.8 L282,85.1 L288,84.2 L294,83.2 L300,82.1 L306,81.0 L312,79.8 L318,78.4 L324,77.1 L330,75.7 L336,74.2 L342,72.7 L348,71.1 L354,69.6 L360,68.0 L366,66.4 L372,64.9 L378,63.3 L384,61.8 L390,60.3 L396,58.9 L402,57.6 L408,56.2 L414,55.0 L420,53.9 L426,52.8 L432,51.8 L438,50.9 L444,50.2 L450,49.5 L456,49.0 L462,48.6 L468,48.2 L474,48.1 L480,48.0 L486,48.1 L492,48.2 L498,48.6 L504,49.0 L510,49.5 L516,50.2 L522,50.9 L528,51.8 L534,52.8 L540,53.9 L546,55.0 L552,56.2 L558,57.6 L564,58.9 L570,60.3 L576,61.8 L582,63.3 L588,64.9 L594,66.4 L600,68.0 L606,69.6 L612,71.1 L618,72.7 L624,74.2 L630,75.7 L636,77.1 L642,78.4 L648,79.8 L654,81.0 L660,82.1 L666,83.2 L672,84.2 L678,85.1 L684,85.8 L690,86.5 L696,87.0 L702,87.4 L708,87.8 L714,87.9 L720,88.0 L726,87.9 L732,87.8 L738,87.4 L744,87.0 L750,86.5 L756,85.8 L762,85.1 L768,84.2 L774,83.2 L780,82.1 L786,81.0 L792,79.8 L798,78.4 L804,77.1 L810,75.7 L816,74.2 L822,72.7 L828,71.1 L834,69.6 L840,68.0 L846,66.4 L852,64.9 L858,63.3 L864,61.8 L870,60.3 L876,58.9 L882,57.6 L888,56.2 L894,55.0 L900,53.9 L906,52.8 L912,51.8 L918,50.9 L924,50.2 L930,49.5 L936,49.0 L942,48.6 L948,48.2 L954,48.1 L960,48.0 L966,48.1 L972,48.2 L978,48.6 L984,49.0 L990,49.5 L996,50.2 L1002,50.9 L1008,51.8 L1014,52.8 L1020,53.9 L1026,55.0 L1032,56.2 L1038,57.6 L1044,58.9 L1050,60.3 L1056,61.8 L1062,63.3 L1068,64.9 L1074,66.4 L1080,68.0 L1086,69.6 L1092,71.1 L1098,72.7 L1104,74.2 L1110,75.7 L1116,77.1 L1122,78.4 L1128,79.8 L1134,81.0 L1140,82.1 L1146,83.2 L1152,84.2 L1158,85.1 L1164,85.8 L1170,86.5 L1176,87.0 L1182,87.4 L1188,87.8 L1194,87.9 L1200,88.0 L1206,87.9 L1212,87.8 L1218,87.4 L1224,87.0 L1230,86.5 L1236,85.8 L1242,85.1 L1248,84.2 L1254,83.2 L1260,82.1 L1266,81.0 L1272,79.8 L1278,78.4 L1284,77.1 L1290,75.7 L1296,74.2 L1302,72.7 L1308,71.1 L1314,69.6 L1320,68.0 L1326,66.4 L1332,64.9 L1338,63.3 L1344,61.8 L1350,60.3 L1356,58.9 L1362,57.6 L1368,56.2 L1374,55.0 L1380,53.9 L1386,52.8 L1392,51.8 L1398,50.9 L1404,50.2 L1410,49.5 L1416,49.0 L1422,48.6 L1428,48.2 L1434,48.1 L1440,48.0" fill="none" stroke="#7a80a6" stroke-opacity=".35" stroke-width="8" filter="url(#phSh)" vector-effect="non-scaling-stroke"/><path d="M0,170 L0,50.0 L6,50.1 L12,50.2 L18,50.6 L24,51.0 L30,51.5 L36,52.2 L42,52.9 L48,53.8 L54,54.8 L60,55.9 L66,57.0 L72,58.2 L78,59.6 L84,60.9 L90,62.3 L96,63.8 L102,65.3 L108,66.9 L114,68.4 L120,70.0 L126,71.6 L132,73.1 L138,74.7 L144,76.2 L150,77.7 L156,79.1 L162,80.4 L168,81.8 L174,83.0 L180,84.1 L186,85.2 L192,86.2 L198,87.1 L204,87.8 L210,88.5 L216,89.0 L222,89.4 L228,89.8 L234,89.9 L240,90.0 L246,89.9 L252,89.8 L258,89.4 L264,89.0 L270,88.5 L276,87.8 L282,87.1 L288,86.2 L294,85.2 L300,84.1 L306,83.0 L312,81.8 L318,80.4 L324,79.1 L330,77.7 L336,76.2 L342,74.7 L348,73.1 L354,71.6 L360,70.0 L366,68.4 L372,66.9 L378,65.3 L384,63.8 L390,62.3 L396,60.9 L402,59.6 L408,58.2 L414,57.0 L420,55.9 L426,54.8 L432,53.8 L438,52.9 L444,52.2 L450,51.5 L456,51.0 L462,50.6 L468,50.2 L474,50.1 L480,50.0 L486,50.1 L492,50.2 L498,50.6 L504,51.0 L510,51.5 L516,52.2 L522,52.9 L528,53.8 L534,54.8 L540,55.9 L546,57.0 L552,58.2 L558,59.6 L564,60.9 L570,62.3 L576,63.8 L582,65.3 L588,66.9 L594,68.4 L600,70.0 L606,71.6 L612,73.1 L618,74.7 L624,76.2 L630,77.7 L636,79.1 L642,80.4 L648,81.8 L654,83.0 L660,84.1 L666,85.2 L672,86.2 L678,87.1 L684,87.8 L690,88.5 L696,89.0 L702,89.4 L708,89.8 L714,89.9 L720,90.0 L726,89.9 L732,89.8 L738,89.4 L744,89.0 L750,88.5 L756,87.8 L762,87.1 L768,86.2 L774,85.2 L780,84.1 L786,83.0 L792,81.8 L798,80.4 L804,79.1 L810,77.7 L816,76.2 L822,74.7 L828,73.1 L834,71.6 L840,70.0 L846,68.4 L852,66.9 L858,65.3 L864,63.8 L870,62.3 L876,60.9 L882,59.6 L888,58.2 L894,57.0 L900,55.9 L906,54.8 L912,53.8 L918,52.9 L924,52.2 L930,51.5 L936,51.0 L942,50.6 L948,50.2 L954,50.1 L960,50.0 L966,50.1 L972,50.2 L978,50.6 L984,51.0 L990,51.5 L996,52.2 L1002,52.9 L1008,53.8 L1014,54.8 L1020,55.9 L1026,57.0 L1032,58.2 L1038,59.6 L1044,60.9 L1050,62.3 L1056,63.8 L1062,65.3 L1068,66.9 L1074,68.4 L1080,70.0 L1086,71.6 L1092,73.1 L1098,74.7 L1104,76.2 L1110,77.7 L1116,79.1 L1122,80.4 L1128,81.8 L1134,83.0 L1140,84.1 L1146,85.2 L1152,86.2 L1158,87.1 L1164,87.8 L1170,88.5 L1176,89.0 L1182,89.4 L1188,89.8 L1194,89.9 L1200,90.0 L1206,89.9 L1212,89.8 L1218,89.4 L1224,89.0 L1230,88.5 L1236,87.8 L1242,87.1 L1248,86.2 L1254,85.2 L1260,84.1 L1266,83.0 L1272,81.8 L1278,80.4 L1284,79.1 L1290,77.7 L1296,76.2 L1302,74.7 L1308,73.1 L1314,71.6 L1320,70.0 L1326,68.4 L1332,66.9 L1338,65.3 L1344,63.8 L1350,62.3 L1356,60.9 L1362,59.6 L1368,58.2 L1374,57.0 L1380,55.9 L1386,54.8 L1392,53.8 L1398,52.9 L1404,52.2 L1410,51.5 L1416,51.0 L1422,50.6 L1428,50.2 L1434,50.1 L1440,50.0 L1440,170 Z" fill="url(#phG2)"/><path d="M0,50.0 L6,50.1 L12,50.2 L18,50.6 L24,51.0 L30,51.5 L36,52.2 L42,52.9 L48,53.8 L54,54.8 L60,55.9 L66,57.0 L72,58.2 L78,59.6 L84,60.9 L90,62.3 L96,63.8 L102,65.3 L108,66.9 L114,68.4 L120,70.0 L126,71.6 L132,73.1 L138,74.7 L144,76.2 L150,77.7 L156,79.1 L162,80.4 L168,81.8 L174,83.0 L180,84.1 L186,85.2 L192,86.2 L198,87.1 L204,87.8 L210,88.5 L216,89.0 L222,89.4 L228,89.8 L234,89.9 L240,90.0 L246,89.9 L252,89.8 L258,89.4 L264,89.0 L270,88.5 L276,87.8 L282,87.1 L288,86.2 L294,85.2 L300,84.1 L306,83.0 L312,81.8 L318,80.4 L324,79.1 L330,77.7 L336,76.2 L342,74.7 L348,73.1 L354,71.6 L360,70.0 L366,68.4 L372,66.9 L378,65.3 L384,63.8 L390,62.3 L396,60.9 L402,59.6 L408,58.2 L414,57.0 L420,55.9 L426,54.8 L432,53.8 L438,52.9 L444,52.2 L450,51.5 L456,51.0 L462,50.6 L468,50.2 L474,50.1 L480,50.0 L486,50.1 L492,50.2 L498,50.6 L504,51.0 L510,51.5 L516,52.2 L522,52.9 L528,53.8 L534,54.8 L540,55.9 L546,57.0 L552,58.2 L558,59.6 L564,60.9 L570,62.3 L576,63.8 L582,65.3 L588,66.9 L594,68.4 L600,70.0 L606,71.6 L612,73.1 L618,74.7 L624,76.2 L630,77.7 L636,79.1 L642,80.4 L648,81.8 L654,83.0 L660,84.1 L666,85.2 L672,86.2 L678,87.1 L684,87.8 L690,88.5 L696,89.0 L702,89.4 L708,89.8 L714,89.9 L720,90.0 L726,89.9 L732,89.8 L738,89.4 L744,89.0 L750,88.5 L756,87.8 L762,87.1 L768,86.2 L774,85.2 L780,84.1 L786,83.0 L792,81.8 L798,80.4 L804,79.1 L810,77.7 L816,76.2 L822,74.7 L828,73.1 L834,71.6 L840,70.0 L846,68.4 L852,66.9 L858,65.3 L864,63.8 L870,62.3 L876,60.9 L882,59.6 L888,58.2 L894,57.0 L900,55.9 L906,54.8 L912,53.8 L918,52.9 L924,52.2 L930,51.5 L936,51.0 L942,50.6 L948,50.2 L954,50.1 L960,50.0 L966,50.1 L972,50.2 L978,50.6 L984,51.0 L990,51.5 L996,52.2 L1002,52.9 L1008,53.8 L1014,54.8 L1020,55.9 L1026,57.0 L1032,58.2 L1038,59.6 L1044,60.9 L1050,62.3 L1056,63.8 L1062,65.3 L1068,66.9 L1074,68.4 L1080,70.0 L1086,71.6 L1092,73.1 L1098,74.7 L1104,76.2 L1110,77.7 L1116,79.1 L1122,80.4 L1128,81.8 L1134,83.0 L1140,84.1 L1146,85.2 L1152,86.2 L1158,87.1 L1164,87.8 L1170,88.5 L1176,89.0 L1182,89.4 L1188,89.8 L1194,89.9 L1200,90.0 L1206,89.9 L1212,89.8 L1218,89.4 L1224,89.0 L1230,88.5 L1236,87.8 L1242,87.1 L1248,86.2 L1254,85.2 L1260,84.1 L1266,83.0 L1272,81.8 L1278,80.4 L1284,79.1 L1290,77.7 L1296,76.2 L1302,74.7 L1308,73.1 L1314,71.6 L1320,70.0 L1326,68.4 L1332,66.9 L1338,65.3 L1344,63.8 L1350,62.3 L1356,60.9 L1362,59.6 L1368,58.2 L1374,57.0 L1380,55.9 L1386,54.8 L1392,53.8 L1398,52.9 L1404,52.2 L1410,51.5 L1416,51.0 L1422,50.6 L1428,50.2 L1434,50.1 L1440,50.0" fill="none" stroke="#fff" stroke-width="3" vector-effect="non-scaling-stroke"/><path d="M0,53.0 L6,53.1 L12,53.2 L18,53.6 L24,54.0 L30,54.5 L36,55.2 L42,55.9 L48,56.8 L54,57.8 L60,58.9 L66,60.0 L72,61.2 L78,62.6 L84,63.9 L90,65.3 L96,66.8 L102,68.3 L108,69.9 L114,71.4 L120,73.0 L126,74.6 L132,76.1 L138,77.7 L144,79.2 L150,80.7 L156,82.1 L162,83.4 L168,84.8 L174,86.0 L180,87.1 L186,88.2 L192,89.2 L198,90.1 L204,90.8 L210,91.5 L216,92.0 L222,92.4 L228,92.8 L234,92.9 L240,93.0 L246,92.9 L252,92.8 L258,92.4 L264,92.0 L270,91.5 L276,90.8 L282,90.1 L288,89.2 L294,88.2 L300,87.1 L306,86.0 L312,84.8 L318,83.4 L324,82.1 L330,80.7 L336,79.2 L342,77.7 L348,76.1 L354,74.6 L360,73.0 L366,71.4 L372,69.9 L378,68.3 L384,66.8 L390,65.3 L396,63.9 L402,62.6 L408,61.2 L414,60.0 L420,58.9 L426,57.8 L432,56.8 L438,55.9 L444,55.2 L450,54.5 L456,54.0 L462,53.6 L468,53.2 L474,53.1 L480,53.0 L486,53.1 L492,53.2 L498,53.6 L504,54.0 L510,54.5 L516,55.2 L522,55.9 L528,56.8 L534,57.8 L540,58.9 L546,60.0 L552,61.2 L558,62.6 L564,63.9 L570,65.3 L576,66.8 L582,68.3 L588,69.9 L594,71.4 L600,73.0 L606,74.6 L612,76.1 L618,77.7 L624,79.2 L630,80.7 L636,82.1 L642,83.4 L648,84.8 L654,86.0 L660,87.1 L666,88.2 L672,89.2 L678,90.1 L684,90.8 L690,91.5 L696,92.0 L702,92.4 L708,92.8 L714,92.9 L720,93.0 L726,92.9 L732,92.8 L738,92.4 L744,92.0 L750,91.5 L756,90.8 L762,90.1 L768,89.2 L774,88.2 L780,87.1 L786,86.0 L792,84.8 L798,83.4 L804,82.1 L810,80.7 L816,79.2 L822,77.7 L828,76.1 L834,74.6 L840,73.0 L846,71.4 L852,69.9 L858,68.3 L864,66.8 L870,65.3 L876,63.9 L882,62.6 L888,61.2 L894,60.0 L900,58.9 L906,57.8 L912,56.8 L918,55.9 L924,55.2 L930,54.5 L936,54.0 L942,53.6 L948,53.2 L954,53.1 L960,53.0 L966,53.1 L972,53.2 L978,53.6 L984,54.0 L990,54.5 L996,55.2 L1002,55.9 L1008,56.8 L1014,57.8 L1020,58.9 L1026,60.0 L1032,61.2 L1038,62.6 L1044,63.9 L1050,65.3 L1056,66.8 L1062,68.3 L1068,69.9 L1074,71.4 L1080,73.0 L1086,74.6 L1092,76.1 L1098,77.7 L1104,79.2 L1110,80.7 L1116,82.1 L1122,83.4 L1128,84.8 L1134,86.0 L1140,87.1 L1146,88.2 L1152,89.2 L1158,90.1 L1164,90.8 L1170,91.5 L1176,92.0 L1182,92.4 L1188,92.8 L1194,92.9 L1200,93.0 L1206,92.9 L1212,92.8 L1218,92.4 L1224,92.0 L1230,91.5 L1236,90.8 L1242,90.1 L1248,89.2 L1254,88.2 L1260,87.1 L1266,86.0 L1272,84.8 L1278,83.4 L1284,82.1 L1290,80.7 L1296,79.2 L1302,77.7 L1308,76.1 L1314,74.6 L1320,73.0 L1326,71.4 L1332,69.9 L1338,68.3 L1344,66.8 L1350,65.3 L1356,63.9 L1362,62.6 L1368,61.2 L1374,60.0 L1380,58.9 L1386,57.8 L1392,56.8 L1398,55.9 L1404,55.2 L1410,54.5 L1416,54.0 L1422,53.6 L1428,53.2 L1434,53.1 L1440,53.0" fill="none" stroke="#c9cde0" stroke-opacity=".7" stroke-width="1" vector-effect="non-scaling-stroke"/><path d="M0,70.0 L6,70.1 L12,70.2 L18,70.6 L24,71.0 L30,71.5 L36,72.2 L42,72.9 L48,73.8 L54,74.8 L60,75.9 L66,77.0 L72,78.2 L78,79.6 L84,80.9 L90,82.3 L96,83.8 L102,85.3 L108,86.9 L114,88.4 L120,90.0 L126,91.6 L132,93.1 L138,94.7 L144,96.2 L150,97.7 L156,99.1 L162,100.4 L168,101.8 L174,103.0 L180,104.1 L186,105.2 L192,106.2 L198,107.1 L204,107.8 L210,108.5 L216,109.0 L222,109.4 L228,109.8 L234,109.9 L240,110.0 L246,109.9 L252,109.8 L258,109.4 L264,109.0 L270,108.5 L276,107.8 L282,107.1 L288,106.2 L294,105.2 L300,104.1 L306,103.0 L312,101.8 L318,100.4 L324,99.1 L330,97.7 L336,96.2 L342,94.7 L348,93.1 L354,91.6 L360,90.0 L366,88.4 L372,86.9 L378,85.3 L384,83.8 L390,82.3 L396,80.9 L402,79.6 L408,78.2 L414,77.0 L420,75.9 L426,74.8 L432,73.8 L438,72.9 L444,72.2 L450,71.5 L456,71.0 L462,70.6 L468,70.2 L474,70.1 L480,70.0 L486,70.1 L492,70.2 L498,70.6 L504,71.0 L510,71.5 L516,72.2 L522,72.9 L528,73.8 L534,74.8 L540,75.9 L546,77.0 L552,78.2 L558,79.6 L564,80.9 L570,82.3 L576,83.8 L582,85.3 L588,86.9 L594,88.4 L600,90.0 L606,91.6 L612,93.1 L618,94.7 L624,96.2 L630,97.7 L636,99.1 L642,100.4 L648,101.8 L654,103.0 L660,104.1 L666,105.2 L672,106.2 L678,107.1 L684,107.8 L690,108.5 L696,109.0 L702,109.4 L708,109.8 L714,109.9 L720,110.0 L726,109.9 L732,109.8 L738,109.4 L744,109.0 L750,108.5 L756,107.8 L762,107.1 L768,106.2 L774,105.2 L780,104.1 L786,103.0 L792,101.8 L798,100.4 L804,99.1 L810,97.7 L816,96.2 L822,94.7 L828,93.1 L834,91.6 L840,90.0 L846,88.4 L852,86.9 L858,85.3 L864,83.8 L870,82.3 L876,80.9 L882,79.6 L888,78.2 L894,77.0 L900,75.9 L906,74.8 L912,73.8 L918,72.9 L924,72.2 L930,71.5 L936,71.0 L942,70.6 L948,70.2 L954,70.1 L960,70.0 L966,70.1 L972,70.2 L978,70.6 L984,71.0 L990,71.5 L996,72.2 L1002,72.9 L1008,73.8 L1014,74.8 L1020,75.9 L1026,77.0 L1032,78.2 L1038,79.6 L1044,80.9 L1050,82.3 L1056,83.8 L1062,85.3 L1068,86.9 L1074,88.4 L1080,90.0 L1086,91.6 L1092,93.1 L1098,94.7 L1104,96.2 L1110,97.7 L1116,99.1 L1122,100.4 L1128,101.8 L1134,103.0 L1140,104.1 L1146,105.2 L1152,106.2 L1158,107.1 L1164,107.8 L1170,108.5 L1176,109.0 L1182,109.4 L1188,109.8 L1194,109.9 L1200,110.0 L1206,109.9 L1212,109.8 L1218,109.4 L1224,109.0 L1230,108.5 L1236,107.8 L1242,107.1 L1248,106.2 L1254,105.2 L1260,104.1 L1266,103.0 L1272,101.8 L1278,100.4 L1284,99.1 L1290,97.7 L1296,96.2 L1302,94.7 L1308,93.1 L1314,91.6 L1320,90.0 L1326,88.4 L1332,86.9 L1338,85.3 L1344,83.8 L1350,82.3 L1356,80.9 L1362,79.6 L1368,78.2 L1374,77.0 L1380,75.9 L1386,74.8 L1392,73.8 L1398,72.9 L1404,72.2 L1410,71.5 L1416,71.0 L1422,70.6 L1428,70.2 L1434,70.1 L1440,70.0" fill="none" stroke="#7a80a6" stroke-opacity=".28" stroke-width="8" filter="url(#phSh)" vector-effect="non-scaling-stroke"/><path d="M0,170 L0,72.0 L6,72.1 L12,72.2 L18,72.6 L24,73.0 L30,73.5 L36,74.2 L42,74.9 L48,75.8 L54,76.8 L60,77.9 L66,79.0 L72,80.2 L78,81.6 L84,82.9 L90,84.3 L96,85.8 L102,87.3 L108,88.9 L114,90.4 L120,92.0 L126,93.6 L132,95.1 L138,96.7 L144,98.2 L150,99.7 L156,101.1 L162,102.4 L168,103.8 L174,105.0 L180,106.1 L186,107.2 L192,108.2 L198,109.1 L204,109.8 L210,110.5 L216,111.0 L222,111.4 L228,111.8 L234,111.9 L240,112.0 L246,111.9 L252,111.8 L258,111.4 L264,111.0 L270,110.5 L276,109.8 L282,109.1 L288,108.2 L294,107.2 L300,106.1 L306,105.0 L312,103.8 L318,102.4 L324,101.1 L330,99.7 L336,98.2 L342,96.7 L348,95.1 L354,93.6 L360,92.0 L366,90.4 L372,88.9 L378,87.3 L384,85.8 L390,84.3 L396,82.9 L402,81.6 L408,80.2 L414,79.0 L420,77.9 L426,76.8 L432,75.8 L438,74.9 L444,74.2 L450,73.5 L456,73.0 L462,72.6 L468,72.2 L474,72.1 L480,72.0 L486,72.1 L492,72.2 L498,72.6 L504,73.0 L510,73.5 L516,74.2 L522,74.9 L528,75.8 L534,76.8 L540,77.9 L546,79.0 L552,80.2 L558,81.6 L564,82.9 L570,84.3 L576,85.8 L582,87.3 L588,88.9 L594,90.4 L600,92.0 L606,93.6 L612,95.1 L618,96.7 L624,98.2 L630,99.7 L636,101.1 L642,102.4 L648,103.8 L654,105.0 L660,106.1 L666,107.2 L672,108.2 L678,109.1 L684,109.8 L690,110.5 L696,111.0 L702,111.4 L708,111.8 L714,111.9 L720,112.0 L726,111.9 L732,111.8 L738,111.4 L744,111.0 L750,110.5 L756,109.8 L762,109.1 L768,108.2 L774,107.2 L780,106.1 L786,105.0 L792,103.8 L798,102.4 L804,101.1 L810,99.7 L816,98.2 L822,96.7 L828,95.1 L834,93.6 L840,92.0 L846,90.4 L852,88.9 L858,87.3 L864,85.8 L870,84.3 L876,82.9 L882,81.6 L888,80.2 L894,79.0 L900,77.9 L906,76.8 L912,75.8 L918,74.9 L924,74.2 L930,73.5 L936,73.0 L942,72.6 L948,72.2 L954,72.1 L960,72.0 L966,72.1 L972,72.2 L978,72.6 L984,73.0 L990,73.5 L996,74.2 L1002,74.9 L1008,75.8 L1014,76.8 L1020,77.9 L1026,79.0 L1032,80.2 L1038,81.6 L1044,82.9 L1050,84.3 L1056,85.8 L1062,87.3 L1068,88.9 L1074,90.4 L1080,92.0 L1086,93.6 L1092,95.1 L1098,96.7 L1104,98.2 L1110,99.7 L1116,101.1 L1122,102.4 L1128,103.8 L1134,105.0 L1140,106.1 L1146,107.2 L1152,108.2 L1158,109.1 L1164,109.8 L1170,110.5 L1176,111.0 L1182,111.4 L1188,111.8 L1194,111.9 L1200,112.0 L1206,111.9 L1212,111.8 L1218,111.4 L1224,111.0 L1230,110.5 L1236,109.8 L1242,109.1 L1248,108.2 L1254,107.2 L1260,106.1 L1266,105.0 L1272,103.8 L1278,102.4 L1284,101.1 L1290,99.7 L1296,98.2 L1302,96.7 L1308,95.1 L1314,93.6 L1320,92.0 L1326,90.4 L1332,88.9 L1338,87.3 L1344,85.8 L1350,84.3 L1356,82.9 L1362,81.6 L1368,80.2 L1374,79.0 L1380,77.9 L1386,76.8 L1392,75.8 L1398,74.9 L1404,74.2 L1410,73.5 L1416,73.0 L1422,72.6 L1428,72.2 L1434,72.1 L1440,72.0 L1440,170 Z" fill="#f7f8fe"/><path d="M0,72.0 L6,72.1 L12,72.2 L18,72.6 L24,73.0 L30,73.5 L36,74.2 L42,74.9 L48,75.8 L54,76.8 L60,77.9 L66,79.0 L72,80.2 L78,81.6 L84,82.9 L90,84.3 L96,85.8 L102,87.3 L108,88.9 L114,90.4 L120,92.0 L126,93.6 L132,95.1 L138,96.7 L144,98.2 L150,99.7 L156,101.1 L162,102.4 L168,103.8 L174,105.0 L180,106.1 L186,107.2 L192,108.2 L198,109.1 L204,109.8 L210,110.5 L216,111.0 L222,111.4 L228,111.8 L234,111.9 L240,112.0 L246,111.9 L252,111.8 L258,111.4 L264,111.0 L270,110.5 L276,109.8 L282,109.1 L288,108.2 L294,107.2 L300,106.1 L306,105.0 L312,103.8 L318,102.4 L324,101.1 L330,99.7 L336,98.2 L342,96.7 L348,95.1 L354,93.6 L360,92.0 L366,90.4 L372,88.9 L378,87.3 L384,85.8 L390,84.3 L396,82.9 L402,81.6 L408,80.2 L414,79.0 L420,77.9 L426,76.8 L432,75.8 L438,74.9 L444,74.2 L450,73.5 L456,73.0 L462,72.6 L468,72.2 L474,72.1 L480,72.0 L486,72.1 L492,72.2 L498,72.6 L504,73.0 L510,73.5 L516,74.2 L522,74.9 L528,75.8 L534,76.8 L540,77.9 L546,79.0 L552,80.2 L558,81.6 L564,82.9 L570,84.3 L576,85.8 L582,87.3 L588,88.9 L594,90.4 L600,92.0 L606,93.6 L612,95.1 L618,96.7 L624,98.2 L630,99.7 L636,101.1 L642,102.4 L648,103.8 L654,105.0 L660,106.1 L666,107.2 L672,108.2 L678,109.1 L684,109.8 L690,110.5 L696,111.0 L702,111.4 L708,111.8 L714,111.9 L720,112.0 L726,111.9 L732,111.8 L738,111.4 L744,111.0 L750,110.5 L756,109.8 L762,109.1 L768,108.2 L774,107.2 L780,106.1 L786,105.0 L792,103.8 L798,102.4 L804,101.1 L810,99.7 L816,98.2 L822,96.7 L828,95.1 L834,93.6 L840,92.0 L846,90.4 L852,88.9 L858,87.3 L864,85.8 L870,84.3 L876,82.9 L882,81.6 L888,80.2 L894,79.0 L900,77.9 L906,76.8 L912,75.8 L918,74.9 L924,74.2 L930,73.5 L936,73.0 L942,72.6 L948,72.2 L954,72.1 L960,72.0 L966,72.1 L972,72.2 L978,72.6 L984,73.0 L990,73.5 L996,74.2 L1002,74.9 L1008,75.8 L1014,76.8 L1020,77.9 L1026,79.0 L1032,80.2 L1038,81.6 L1044,82.9 L1050,84.3 L1056,85.8 L1062,87.3 L1068,88.9 L1074,90.4 L1080,92.0 L1086,93.6 L1092,95.1 L1098,96.7 L1104,98.2 L1110,99.7 L1116,101.1 L1122,102.4 L1128,103.8 L1134,105.0 L1140,106.1 L1146,107.2 L1152,108.2 L1158,109.1 L1164,109.8 L1170,110.5 L1176,111.0 L1182,111.4 L1188,111.8 L1194,111.9 L1200,112.0 L1206,111.9 L1212,111.8 L1218,111.4 L1224,111.0 L1230,110.5 L1236,109.8 L1242,109.1 L1248,108.2 L1254,107.2 L1260,106.1 L1266,105.0 L1272,103.8 L1278,102.4 L1284,101.1 L1290,99.7 L1296,98.2 L1302,96.7 L1308,95.1 L1314,93.6 L1320,92.0 L1326,90.4 L1332,88.9 L1338,87.3 L1344,85.8 L1350,84.3 L1356,82.9 L1362,81.6 L1368,80.2 L1374,79.0 L1380,77.9 L1386,76.8 L1392,75.8 L1398,74.9 L1404,74.2 L1410,73.5 L1416,73.0 L1422,72.6 L1428,72.2 L1434,72.1 L1440,72.0" fill="none" stroke="#fff" stroke-width="2.5" vector-effect="non-scaling-stroke"/></svg></div>' + motif("inner-hero")
FOOT_ART = art("wv-foot", 170, "wv-foot-art") + motif("footer")
_div_n = [0]


def wave_div(kind=None):
    """In-flow wave band between two sections; alternates crest direction (a / b) down the page."""
    if kind is None:
        kind = "a" if _div_n[0] % 2 == 0 else "b"
        _div_n[0] += 1
    return f'<div class="wave-div" aria-hidden="true">{art("wv-div-" + kind, 130, "wv-div-art")}</div>'


def divider(*_):
    return wave_div()


def sec_slice(name):          # kept for compatibility; hero/footer art is placed directly now
    return HERO_ART if name == "hero" else ""


def head(title, desc):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title}</title>
<meta name="description" content="{escape(desc)}"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="assets/css/wise-teck.css?v={ASSET_V}"/>
<link rel="icon" href="assets/img/favicon.png"/>
</head>'''


SYMBOLS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <linearGradient id="wPurple" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8b4dff"/><stop offset="1" stop-color="#4c1d95"/></linearGradient>
    <linearGradient id="wGold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbe5a2"/><stop offset=".5" stop-color="#f2bd4b"/><stop offset="1" stop-color="#d9961c"/></linearGradient>
    <symbol id="wmark" viewBox="0 0 60 48"><path d="M2 6 L13 6 L22 34 L30 12 L38 34 L46 6 L58 6 L44 44 L34 44 L30 30 L26 44 L16 44 Z"/></symbol>
  </defs>
</svg>'''

TOPBAR = '''<div class="topbar" style="min-height:54px">
  <div class="container" style="min-height:54px">
    <div class="group"><span><i class="fa-solid fa-location-dot"></i>A Project of WISE Education Society</span></div>
    <div class="group">
      <a href="tel:+923008410868"><i class="fa-solid fa-phone"></i>+92 300 8410868</a>
      <a href="mailto:info@wise-teck.org"><i class="fa-solid fa-envelope"></i>info@wise-teck.org</a>
      <span class="hide-sm"><i class="fa-solid fa-location-dot"></i>48-Main Gulberg, Lahore</span>
    </div>
  </div>
</div>'''


def nav(active):
    sect = SECTION_OF.get(active, "")
    items = []
    for label, key, kids in NAV:
        on = sect == key
        if kids is None:
            href = P[key] if key in P else "#"
            items.append(f'<a{" class=\"active\"" if on else ""} href="{href}">{label}</a>')
        else:
            sub = "".join(f'<a href="{h}">{t}</a>' for t, h in kids)
            items.append(f'<div class="dd{" active" if on else ""}"><button type="button">{label} <i class="fa-solid fa-chevron-down"></i></button>'
                         f'<div class="dd-panel">{sub}</div></div>')
    return f'''  <div class="nav-wrap">
    <nav class="nav" aria-label="Main">
      <a class="logo" href="{P["home"]}"><span class="brand__spin" aria-hidden="true"><img class="brand__face" src="assets/img/logo-round.svg" alt="" width="44" height="44"/><img class="brand__face brand__face--back" src="assets/img/logo-round.svg" alt="" width="44" height="44"/></span><span><b>WISE-TECK</b><small>A Project of WISE</small></span></a>
      <div class="menu" id="menu">{"".join(items)}</div>
      <a class="btn btn-gold" href="{P["contact"]}">Apply Now <i class="fa-solid fa-arrow-right"></i></a>
      <button class="burger" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button>
    </nav>
  </div>'''


def footer(ref=False):
    return f'''<footer class="footer wt-sec" id="contact-info">
  {FOOT_ART}
  <div class="container">
    <div class="ft-grid">
      <div class="ft-col">
        <a class="logo ft-logo" href="{P["home"]}"><span class="brand__spin" aria-hidden="true"><img class="brand__face" src="assets/img/logo-round.svg" alt="" width="44" height="44"/><img class="brand__face brand__face--back" src="assets/img/logo-round.svg" alt="" width="44" height="44"/></span><span><b>WISE-TECK</b><small>A Project of WISE</small></span></a>
        <p class="ft-tag">Skills, Projects, Mentorship and Earning Opportunities.</p>
        <div class="social"><a href="#" aria-label="Facebook"><i class="fa-brands fa-facebook-f"></i></a><a href="#" aria-label="Instagram"><i class="fa-brands fa-instagram"></i></a><a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin-in"></i></a><a href="#" aria-label="YouTube"><i class="fa-brands fa-youtube"></i></a></div>
      </div>
      <div class="ft-col"><h4>Quick Links</h4><a href="{P["home"]}">Home</a><a href="{P["about"]}">About</a><a href="{P["home"]}#programs">Programs</a><a href="{P["home"]}#services">Services</a><a href="{P["contact"]}">Contact</a></div>
      <div class="ft-col"><h4>Our Programs</h4><a href="{P["hub"]}">Wise Support Hub</a><a href="{P["college"]}">Wise College Degree Programs</a><a href="{P["courses"]}">Professional Paid Courses</a></div>
      <div class="ft-col"><h4>Our Services</h4><a href="{P["centre"]}">Earning Centre</a><a href="{P["placement"]}">Placement Department</a><a href="{P["loan"]}">Student Loan Scheme</a><a href="{P["corporate"]}">Corporate Services</a></div>
      <div class="ft-col"><div class="ft-contact">
        <div><i class="fa-solid fa-phone"></i>+92 300 8410868</div>
        <div><i class="fa-regular fa-envelope"></i>info@wise-teck.org</div>
        <div><i class="fa-solid fa-location-dot"></i>48-Main Gulberg, Lahore</div>
      </div></div>
    </div>
  </div>
</footer>'''


def page(key, title, desc, hero, body, home=False):
    ref = ' data-ref="assets/ref/reference.jpeg"' if home else ""
    three = (f'<script src="assets/js/vendor/three.min.js?v={ASSET_V}" defer></script>\n<script src="assets/js/hero-three.js?v={ASSET_V}" defer></script>\n'
             if 'id="heroThreeStage"' in hero else "")
    return f'''{head(title, desc)}
<body class="v3{"" if home else " inner"}"{ref}>
{SYMBOLS}
{SPRITE}
{TOPBAR}
{hero}
<main>
{body}
</main>
{footer(ref=home)}
{three}<script src="assets/js/wt-waves.js?v={ASSET_V}" defer></script>
<script src="assets/js/wt.js?v={ASSET_V}"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- reusable blocks
def btn(label, href, kind="gold", icon="fa-arrow-right"):
    return f'<a class="btn btn-{kind}" href="{href}">{label} <i class="fa-solid {icon}"></i></a>'


def sec_head(kicker, title, sub=None, lined=False):
    k = f'<span class="kicker">{kicker}</span>' if kicker else ""
    h = f'<h2 class="lined">{title}</h2>' if lined else f"<h2>{title}</h2>"
    s = f"<p>{sub}</p>" if sub else ""
    return f'<div class="sec-head reveal">{k}{h}{s}</div>'


def blk(inner, cls="", div=None, sid=""):
    i = f' id="{sid}"' if sid else ""
    after = wave_div() if div else ""
    return f'<section class="blk {cls}"{i}><div class="container">{inner}</div></section>{after}'


def cards(items, cols=3, numbered=False):
    out = []
    for n, it in enumerate(items, 1):
        icon, title, text = it[0], it[1], it[2]
        link = it[3] if len(it) > 3 else None
        num = f'<span class="num">{n:02d}</span>' if numbered else ""
        more = f'<a class="more" href="{link[1]}">{link[0]} <i class="fa-solid fa-arrow-right"></i></a>' if link else ""
        out.append(f'<article class="card reveal d{(n - 1) % 4}">{num}<div class="ic"><i class="fa-solid {icon}"></i></div>'
                   f'<h3>{title}</h3><p>{text}</p>{more}</article>')
    c = {4: " c4", 2: " c2"}.get(cols, "")
    return f'<div class="cards{c}">{"".join(out)}</div>'


def steps(items):
    out = []
    for n, it in enumerate(items, 1):
        p = f"<p>{it[2]}</p>" if len(it) > 2 and it[2] else ""
        out.append(f'<div class="step reveal d{(n - 1) % 4}"><div class="dot"><i class="fa-solid {it[0]}"></i></div>'
                   f'<small>Step {n}</small><h3>{it[1]}</h3>{p}</div>')
    return f'<div class="steps" style="--n:{len(items)}">{"".join(out)}</div>'


def pstrip(active=None):
    out = []
    for key, icon, title, text in PROGRAMS:
        on = " on" if key == active else ""
        out.append(f'<a class="pc reveal{on}" href="{P[key]}"><span class="ic"><i class="fa-solid {icon}"></i></span>'
                   f'<h3>{title}</h3><p>{text}</p><span class="more">Read More <i class="fa-solid fa-arrow-right"></i></span></a>')
    return f'<div class="pstrip">{"".join(out)}</div>'


def checklist(title, items, two=False):
    lis = "".join(f'<li><i class="fa-solid fa-check"></i>{t}</li>' for t in items)
    return f'<div class="glass panel reveal"><h3>{title}</h3><ul class="checks{" two" if two else ""}">{lis}</ul></div>'


def placeholder(title, text):
    return (f'<div class="placeholder reveal"><i class="fa-solid fa-pen-to-square"></i><div><b>[Placeholder] {title}</b>{text}</div></div>')


def quote(text, who, sub, icon="fa-quote-left"):
    return (f'<div class="glass quote-card reveal"><div class="q">&ldquo;</div><blockquote>{text}</blockquote>'
            f'<div class="sig"><span><i class="fa-solid {icon}"></i></span><div><b>{who}</b><small>{sub}</small></div></div></div>')


def media(src, alt):
    return f'<div class="media reveal"><img src="{src}" alt="{escape(alt)}" loading="lazy"/></div>'


def split(left, right, rev=False):
    """Two-column block. Each side is always ONE grid cell (a text side made of several elements
    is wrapped, so its kicker / heading / paragraphs / button stay together in its column)."""
    def cell(x):
        x = x.strip()
        return x if (x.startswith("<div") and x.endswith("</div>") and x.count("<div") == x.count("</div>") and
                     _single_root(x)) else f'<div class="reveal">{x}</div>'
    return f'<div class="split{" rev" if rev else ""}">{cell(left)}{cell(right)}</div>'


def _single_root(x):
    """True if x is exactly one element (its first tag closes at the very end)."""
    depth = 0
    for m in re.finditer(r"<(/?)div[^>]*>", x):
        depth += -1 if m.group(1) else 1
        if depth == 0 and m.end() != len(x):
            return False
    return depth == 0


def cta(tag, title, text, primary, secondary=None):
    sec = btn(secondary[0], secondary[1], "outline-light") if secondary else ""
    return blk(f'''<div class="band reveal">
      <svg viewBox="0 0 1200 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,70 C260,20 520,110 800,60 C980,30 1100,70 1200,50" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="2"/><path d="M0,95 C300,55 560,125 840,85 C1010,62 1120,95 1200,80" fill="none" stroke="#f2bd4b" stroke-opacity=".5" stroke-width="2"/></svg>
      <div style="position:relative;z-index:1"><div class="tag">{tag}</div><h2>{title}</h2><p>{text}</p></div>
      <div class="acts">{btn(primary[0], primary[1])}{sec}</div></div>''', "tight", sid="cta") + '<div style="height:60px"></div>'



# glass stat cards under the inner-page feature photo (facts taken from the ecosystem PDF only)
HERO_STATS = {
    "about":     [("fa-diagram-project", "3", "Programs"), ("fa-bullseye", "8", "Core Objectives"), ("fa-cubes", "6", "Earning Blocks")],
    "hub":       [("fa-book-open", "Free", "Education"), ("fa-utensils", "Free", "Daily Lunch"), ("fa-bus", "Free", "Transport")],
    "college":   [("fa-graduation-cap", "ADP &amp; BS", "Degree Programs"), ("fa-microchip", "4", "Specialisations"), ("fa-user-graduate", "MPhil/PhD", "Faculty")],
    "courses":   [("fa-calendar-week", "Weekend", "Classes"), ("fa-user-graduate", "Students", "&amp; Graduates"), ("fa-briefcase", "Working", "Professionals")],
    "centre":    [("fa-diagram-project", "3", "Programs Feed In"), ("fa-cubes", "6", "Earning Blocks"), ("fa-hands-holding-circle", "6", "Support Services")],
    "loan":      [("fa-user-check", "Eligible", "Students"), ("fa-store", "Start", "Your Own Business"), ("fa-route", "Step 4", "of the Earning Journey")],
    "placement": [("fa-briefcase", "Jobs", "&amp; Careers"), ("fa-user-tie", "Internships", "for Students"), ("fa-coins", "Earning", "Opportunities")],
    "contact":   [("fa-phone", "+92 300 8410868", "Call Us"), ("fa-envelope", "info@wise-teck.org", "Email"), ("fa-location-dot", "48-Main Gulberg", "Lahore")],
}


def hero_stats(key):
    items = HERO_STATS.get(key)
    if not items:
        return ""
    long = any(len(v) > 10 for _, v, _ in items)
    return f'<div class="pf-stats{" pf-stats--text" if long else ""}">' + "".join(
        f'<div class="pf-stat"><span class="pf-ic"><i class="fa-solid {i}"></i></span><span><b>{v}</b><small>{l}</small></span></div>'
        for i, v, l in items) + "</div>"


def page_hero(key, crumbs, eyebrow, title, lead, ctas, visual, facts=None):
    cr = "".join(f'<a href="{h}">{t}</a><i class="fa-solid fa-chevron-right"></i>' for t, h in crumbs[:-1])
    cr += f"<b>{crumbs[-1][0]}</b>"
    fx = ""
    if facts:
        fx = '<div class="hero-facts">' + "".join(f'<span class="fact"><i class="fa-solid {i}"></i>{t}</span>' for i, t in facts) + "</div>"
    st = hero_stats(key) if visual and "hero-photo" in visual else ""
    feature = f'<div class="page-feature{" has-stats" if st else ""}">{visual}{st}</div>' if visual else ""
    return f'''<header class="hero page-hero page-hero--center wt-sec">
  {INNER_HERO_ART}
{nav(key)}
  <div class="container hero-body">
    <div class="reveal">
      <nav class="crumbs" aria-label="Breadcrumb">{cr}</nav>
      <div class="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p class="lead">{lead}</p>
      {fx}
      <div class="ctas">{ctas}</div>
    </div>
  </div>
</header>
{feature}'''


def photo(src, alt, badge=None):
    b = ""
    if badge:
        b = f'<div class="badge-float"><span><i class="fa-solid {badge[0]}"></i></span>{badge[1]}</div>'
    return (f'<div class="hero-photo reveal d2"><div class="frame"><img src="{src}" alt="{escape(alt)}"/></div>{b}</div>')


def orb(center_icon, nodes):
    """v1 hero spinner, as is: revolving ring + spokes, Three.js 3D coin with the original logo, 4 floating tags.
    (center_icon is kept for call compatibility; the coin always shows the original Wise-Teck logo.)"""
    six = len(nodes) >= 6
    if six:   # six evenly spaced around the ring (hexagon): top, top-right, bottom-right, bottom, bottom-left, top-left
        tags = "".join(f'<li class="orbit-tag orbit-tag--hex{" orbit-tag--top" if i == 0 else ""}" style="--a:{-90 + 60 * i}deg">'
                       f'<span class="orbit-tag__ic"><i class="fa-solid {ic}"></i></span><span class="orbit-tag__t">{t.replace("<br/>", " ")}</span></li>'
                       for i, (ic, t) in enumerate(nodes[:6]))
        spokes = "".join(f'<i class="hring__spoke" style="--a:{-90 + 60 * i}deg"></i>' for i in range(6))
    else:
        tags = "".join(f'<li class="orbit-tag orbit-tag--{i + 1}"><span class="orbit-tag__ic"><i class="fa-solid {ic}"></i></span>'
                       f'<span class="orbit-tag__t">{t.replace("<br/>", " ")}</span></li>' for i, (ic, t) in enumerate(nodes[:4]))
        spokes = ('<i class="hring__spoke" style="--a:-90deg"></i><i class="hring__spoke" style="--a:0deg"></i>'
                  '<i class="hring__spoke" style="--a:90deg"></i><i class="hring__spoke" style="--a:180deg"></i>')
    return f'''<div class="hero__visual{" hero__visual--six" if six else ""} reveal d2">
      <div class="hring" aria-hidden="true">
        <svg class="hring__sys" viewBox="0 0 200 200" focusable="false"><circle class="hring__soft" cx="100" cy="100" r="96"/><circle class="hring__path" cx="100" cy="100" r="96"/>
          <circle class="hring__p" cx="100" cy="4" r="3"/><circle class="hring__p hring__p--2" cx="100" cy="196" r="2.4"/><circle class="hring__p hring__p--3" cx="4" cy="100" r="2.4"/><circle class="hring__p hring__p--2" cx="196" cy="100" r="2"/></svg>
        {spokes}
      </div>
      <div class="hero__three-stage" id="heroThreeStage"><p class="hero__three-fallback" hidden>Loading 3D…</p><canvas id="heroThreeCanvas" aria-hidden="true"></canvas></div>
      <ul class="orbit-tags">{tags}</ul>
    </div>'''


HOME_CRUMB = ("Home", P["home"])
PATHWAY = [("fa-school", "WISE Educational &amp; Training Programs"), ("fa-graduation-cap", "Wise-Teck Skills Training"),
           ("fa-building", "Wise-Teck Earning Centre"), ("fa-chart-line", "Self-Earning")]
BLOCK_STEPS = [("fa-graduation-cap", "Skills Development"), ("fa-hand-pointer", "Earning Block Selection"),
               ("fa-laptop-code", "Practical Projects"), ("fa-briefcase", "Client Work"), ("fa-chart-line", "Self-Earning")]


def pathway_block(note=None, div=None):
    n = f'<p class="glass note reveal">{note}</p>' if note else ""
    return blk(sec_head("Our Earning Pathway", 'From Education to <span class="accent">Self-Earning</span>',
                        "WISE Educational &amp; Training Programs &rarr; Wise-Teck Skills Training &rarr; Wise-Teck Earning Centre &rarr; Self-Earning")
               + steps(PATHWAY) + n, div=div)


def programs_block(active=None, title="Programs Working Under Wise-Teck"):
    return blk(sec_head(None, title, "Students from all three programs come to Wise-Teck to learn professional skills, then move to the Wise-Teck Earning Centre.", lined=True)
               + pstrip(active), div=("prog", "b"))
