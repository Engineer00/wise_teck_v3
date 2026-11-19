"""Compare each Django-rendered page with the v3 static page, tag by tag.  Run: py tools/compare_with_v3.py [-v 60]"""
import difflib, hashlib, html, os, re, sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.test import Client
from django.test.utils import setup_test_environment

V3 = Path(__file__).resolve().parents[2] / "wise-teck-v3"
MAP = {"index.html": "/", "about.html": "/about/", "wise-support-hub.html": "/wise-support-hub/", "wise-college.html": "/wise-college/",
       "professional-paid-courses.html": "/professional-paid-courses/", "earning-centre.html": "/earning-centre/",
       "earning-blocks.html": "/earning-blocks/", "corporate-services.html": "/corporate-services/",
       "business-incubation.html": "/business-incubation/", "student-loan-scheme.html": "/student-loan-scheme/",
       "placement.html": "/placement/", "success-stories.html": "/success-stories/", "contact.html": "/contact/"}
SKIP_ATTR = {"data-ref-top", "data-ref"}


def norm_url(v):
    if v.startswith("http"):
        return "img:" + hashlib.sha1(v.encode()).hexdigest()[:16]
    m = re.match(r"/media/seed/v3/([0-9a-f]{16})\.", v)
    if m:
        return "img:" + m.group(1)
    page, _, frag = v.partition("#")
    if page in MAP:
        return MAP[page] + ("#" + frag if frag else "")
    if page.startswith(("assets/", "/static/")):
        return "asset:" + page.split("?")[0].rsplit("/", 1)[-1]
    return v


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out = []; self.skip = 0; self.in_head = False; self.skip_head = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form": self.skip += 1; self.out.append("<form>"); return
        if self.skip: return
        if tag == "head": self.in_head = True
        if self.in_head and tag in ("link", "meta", "script") and not (tag == "meta" and a.get("name") == "description"):
            self.skip_head = tag == "script"; return
        if tag == "link" and "site-extras" in (a.get("href") or ""): return
        items = []
        for k, v in sorted(a.items()):
            if k in SKIP_ATTR: continue
            v = v or ""
            if k == "class": v = " ".join(sorted(v.split()))
            elif k in ("href", "src"): v = norm_url(v)
            elif k == "style": v = re.sub(r"\s+", "", v)
            items.append(f'{k}="{v}"')
        self.out.append(f"<{tag} {' '.join(items)}>".replace(" >", ">"))
    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if self.in_head and tag in ("link", "meta") and not (tag == "meta" and a.get("name") == "description"): return
        self.handle_starttag(tag, attrs); self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag == "head": self.in_head = False
        if self.in_head and tag in ("link", "meta", "script"):
            self.skip_head = False; return
        if tag == "form": self.skip -= 1; return
        if not self.skip: self.out.append(f"</{tag}>")
    def handle_data(self, d):
        if self.skip or self.skip_head: return
        t = re.sub(r"\s+", " ", d).strip()
        if t: self.out.append(t)


def tokens(s):
    p = P(); p.feed(s); return p.out


setup_test_environment()
c = Client()
total = 0
for f, url in MAP.items():
    a = tokens((V3 / f).read_text(encoding="utf-8"))
    r = c.get(url)
    b = tokens(r.content.decode())
    diff = [l for l in difflib.unified_diff(a, b, "v3", "django", n=1, lineterm="") if not l.startswith(("---", "+++"))]
    changes = [l for l in diff if l[:1] in "+-"]
    total += len(changes)
    print(f"{url:30s} status={r.status_code} v3={len(a)} dj={len(b)} diffs={len(changes)}")
    if changes and "-v" in sys.argv:
        print("\n".join(diff[:int(sys.argv[sys.argv.index('-v') + 1]) if len(sys.argv) > sys.argv.index('-v') + 1 else 60]))
print("TOTAL DIFF LINES", total)
