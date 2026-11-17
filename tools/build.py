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
INNER_HERO_ART = art("wv-hero", 320, "wv-hero-art wv-hero-art--soft") + '<div class="ph-bg" aria-hidden="true"><i class="ph-grid"></i></div>' + motif("inner-hero")
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


# second (smaller) photo for the inner-page feature pair: (stitch page, index) — sample images until real photos arrive
SECOND_PHOTO = {"about": ("13", 1), "hub": ("03", 1), "college": ("04", 2), "courses": ("06", 2), "centre": ("13", 3),
                "loan": ("10", 1), "placement": ("08", 2), "contact": ("13", 5)}


def feature_pair(key, visual):
    """Large photo (about 2/3) + smaller photo (about 1/3), tilted together as one unit."""
    first = re.search(r'src="([^"]+)"', visual)
    pool = [SECOND_PHOTO.get(key)] + [("01", i) for i in range(15)] + [("13", i) for i in range(13)]
    src = ""
    for ref in pool:
        if ref and img(*ref) and (not first or img(*ref) != first.group(1)):
            src = img(*ref)
            break
    if not src:
        return visual
    return (f'<div class="pf-pair">{visual}<div class="hero-photo pf-small"><div class="frame">'
            f'<img src="{src}" alt="" loading="lazy"/></div></div></div>')


def page_hero(key, crumbs, eyebrow, title, lead, ctas, visual, facts=None):
    cr = "".join(f'<a href="{h}">{t}</a><i class="fa-solid fa-chevron-right"></i>' for t, h in crumbs[:-1])
    cr += f"<b>{crumbs[-1][0]}</b>"
    fx = ""
    if facts:
        fx = '<div class="hero-facts">' + "".join(f'<span class="fact"><i class="fa-solid {i}"></i>{t}</span>' for i, t in facts) + "</div>"
    st = hero_stats(key) if visual and "hero-photo" in visual else ""
    if st:
        visual = re.sub(r'<div class="badge-float">.*?</div>', "", visual, flags=re.S)   # no badge on inner banners
        visual = feature_pair(key, visual)
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
