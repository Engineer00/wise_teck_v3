"""SEO health: the checks search engines care about, run over every live page, blog post and success story.

The admin dashboard shows the score and every problem with a link to the field that fixes it. Titles are
checked exactly as the site prints them (core/seo.py), so what passes here is what Google sees.
"""

from collections import defaultdict
from dataclasses import dataclass

from django.urls import reverse

from .models import BlogPost, Page, SiteSettings, SuccessStory
from .seo import TITLE_MAX, _title, detail_title

TITLE = (30, TITLE_MAX)  # characters Google shows in results
DESCRIPTION = (70, 160)  # Google shows up to ~160; shorter than ~70 wastes the space


@dataclass
class Issue:
    level: str  # "error": fix soon · "warn": worth improving · "tip": optional extra
    text: str
    url: str  # the admin screen that fixes it


def _edit(resource, pk):
    return reverse("adminpanel_change", args=[resource, pk])


class _Report:
    def __init__(self):
        self.checks = 0
        self.issues = []

    def check(self, ok, level, text, url):
        if level != "tip":
            self.checks += 1
        if not ok:
            self.issues.append(Issue(level, text, url))

    def length(self, value, limits, what, name, url):
        lo, hi = limits
        n = len(value)
        self.check(lo <= n <= hi, "warn", f"{name}: {what} is {n} characters (best {lo}–{hi}).", url)

    @property
    def score(self):
        errors = sum(i.level == "error" for i in self.issues)
        warns = sum(i.level == "warn" for i in self.issues)
        return max(0, round(100 * (self.checks - errors - 0.5 * warns) / self.checks)) if self.checks else 100


def audit():
    """Run every check. Returns an object with .score (0-100), .checks and .issues (most serious first)."""
    site = SiteSettings.load()
    r = _Report()
    seen_titles, seen_descriptions = defaultdict(list), defaultdict(list)

    for page in Page.objects.live().filter(is_active=True, noindex=False).prefetch_related("sections"):
        url, name = _edit("pages", page.pk), f"Page “{page.title}”"
        title = _title(site, page.title)
        r.length(title, TITLE, "the title", name, url)
        seen_titles[title.lower()].append((name, url))
        if page.meta_description:
            r.length(page.meta_description, DESCRIPTION, "the description", name, url)
            seen_descriptions[page.meta_description.strip().lower()].append((name, url))
        else:
            r.check(
                False, "error", f"{name} has no description of its own (search results show the site default).", url
            )
        sections = [s for s in page.sections.all() if s.is_active]
        r.check(any(s.is_hero for s in sections), "error", f"{name} has no top section, so no main heading (H1).", url)
        for s in sections:
            if s.img:
                r.check(
                    bool(s.image_alt.strip()),
                    "warn",
                    f"{name}: the photo in “{s.title or s.get_layout_display()}” has no description (alt text).",
                    _edit("sections", s.pk),
                )

    for kind, resource, qs in (
        ("Blog post", "blogs", BlogPost.objects.live()),
        ("Success story", "success-stories", SuccessStory.objects.live()),
    ):
        for obj in qs:
            url, name = _edit(resource, obj.pk), f"{kind} “{obj.title}”"
            title = detail_title(site, obj.title)
            r.length(title, TITLE, "the title", name, url)
            seen_titles[title.lower()].append((name, url))
            if obj.short_description:
                r.length(obj.short_description, DESCRIPTION, "the short description", name, url)
                seen_descriptions[obj.short_description.strip().lower()].append((name, url))
            else:
                r.check(False, "error", f"{name} has no short description (it is the search-result text).", url)
            r.check(bool(obj.img), "warn", f"{name} has no photo (sharing previews fall back to the logo).", url)

    for seen, what in ((seen_titles, "title"), (seen_descriptions, "description")):
        for owners in seen.values():
            for name, url in owners[1:]:
                r.check(False, "error", f"{name} has the same {what} as {owners[0][0]}; each page needs its own.", url)

    settings_url = reverse("adminpanel_list", args=["site-settings"])
    r.check(
        bool(site.site_url.strip()),
        "warn",
        "Site Settings: “Main web address” is empty, so canonical links use whatever address a visitor typed.",
        settings_url,
    )
    r.check(
        bool(site.share_image),
        "tip",
        "Sharing previews use the built-in Wise-Teck card; you can upload your own in Site Settings (1200 × 630 px).",
        settings_url,
    )
    if site.meta_description:
        r.length(site.meta_description, DESCRIPTION, "the default description", "Site Settings", settings_url)
    else:
        r.check(False, "error", "Site Settings: no default description.", settings_url)
    r.check(
        bool(site.google_verification),
        "tip",
        "Connect Google Search Console (Site Settings → Google Search Console code) to see your searches.",
        settings_url,
    )
    r.check(bool(site.ga_id), "tip", "Add a Google Analytics ID for detailed visitor reports (optional).", settings_url)

    order = {"error": 0, "warn": 1, "tip": 2}
    r.issues.sort(key=lambda i: order[i.level])
    return r
