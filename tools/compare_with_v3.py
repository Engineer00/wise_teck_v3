"""Compare each Django-rendered page with the v3 static page, tag by tag.

    py -3.13 tools/compare_with_v3.py [-v 60] [--head]   (needs ../wise-teck-v3, the static v3 design)

Optional check: the Django site is now the design source of truth (it adds the spacing system, equal
sections and heroes, and the phone top-bar rule). By default it compares with the v3 working files;
--head compares with v3's last commit instead.

Also imported by core/tests/test_site.py. What is ignored on purpose: asset paths (assets/… vs /static/…),
.html vs /slug/ links, local vs remote copies of the same photo, the SEO tags in <head>, and the inside of the
contact <form> (it really submits in Django).
"""
import difflib
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

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


class _Tokens(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.in_head, self.skip_head = [], 0, False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.skip += 1
            self.out.append("<form>")
            return
        if self.skip:
            return
        if tag == "head":
            self.in_head = True
        if self.in_head and tag in ("link", "meta", "script") and not (tag == "meta" and a.get("name") == "description"):
            self.skip_head = tag == "script"
            return
        items = []
        for k, v in sorted(a.items()):
            if k in SKIP_ATTR:
                continue
            v = v or ""
            if k == "class":
                v = " ".join(sorted(v.split()))
            elif k in ("href", "src"):
                v = norm_url(v)
            elif k == "style":
                v = re.sub(r"\s+", "", v)
            items.append(f'{k}="{v}"')
        self.out.append(f"<{tag} {' '.join(items)}>".replace(" >", ">"))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if self.in_head and tag in ("link", "meta") and not (tag == "meta" and a.get("name") == "description"):
            return
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if self.in_head and tag in ("link", "meta", "script"):
            self.skip_head = False
            return
        if tag == "form":
            self.skip -= 1
            return
        if not self.skip:
            self.out.append(f"</{tag}>")

    def handle_data(self, d):
        if self.skip or self.skip_head:
            return
        t = re.sub(r"\s+", " ", d).strip()
        if t:
            self.out.append(t)


def read_v3(name):
    """The committed version of a v3 page (git HEAD), so unfinished edits in the v3 folder don't change the reference."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(V3), "show", f"HEAD:{name}"], capture_output=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.decode("utf-8")
    except (OSError, subprocess.SubprocessError):
        pass
    return (V3 / name).read_text(encoding="utf-8")


def tokens(html_text):
    p = _Tokens()
    p.feed(html_text)
    return p.out


def compare(client, verbose=0):
    """Returns the total number of differing tokens across all pages (0 = identical)."""
    total = 0
    for f, url in MAP.items():
        a = tokens(read_v3(f) if "--head" in sys.argv else (V3 / f).read_text(encoding="utf-8"))
        r = client.get(url)
        b = tokens(r.content.decode())
        diff = [l for l in difflib.unified_diff(a, b, "v3", "django", n=1, lineterm="") if not l.startswith(("---", "+++"))]
        changes = [l for l in diff if l[:1] in "+-"]
        total += len(changes)
        print(f"{url:30s} status={r.status_code} v3={len(a)} dj={len(b)} diffs={len(changes)}")
        if changes and verbose:
            print("\n".join(diff[:verbose]))
    return total


if __name__ == "__main__":
    import os
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.test import Client
    from django.test.utils import setup_test_environment
    setup_test_environment()
    v = int(sys.argv[sys.argv.index("-v") + 1]) if "-v" in sys.argv else 0
    print("TOTAL DIFF LINES", compare(Client(), v))
