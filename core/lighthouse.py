"""Google Lighthouse results on the admin dashboard.

Lighthouse (Google's quality checker) runs every day on GitHub's servers: .github/workflows/lighthouse.yml runs
tools/lighthouse/run.mjs on every page in the sitemap, on a phone and a desktop, and posts a summary to
/api/lighthouse/ with the shared secret LIGHTHOUSE_TOKEN. Nothing runs on the web server itself.

    clean(data)   checks and trims what the workflow sends (never trust a request body)
    summary()     what the dashboard shows: average scores with the change since the previous run, every page's
                  scores, Core Web Vitals of the home page and the most common issues in plain words
"""

import hmac
from datetime import UTC, datetime

from django.conf import settings
from django.utils import timezone

from .models import LighthouseRun

CATEGORIES = [
    ("performance", "Performance", "How fast pages load and react"),
    ("accessibility", "Accessibility", "Usable by everyone, including screen readers and keyboards"),
    ("best_practices", "Best practices", "Security and modern web standards"),
    ("seo", "SEO", "Basics search engines need: titles, descriptions, links, crawlable pages"),
]
MODES = ("mobile", "desktop")
METRICS = ("fcp", "lcp", "tbt", "si", "cls")
# Google's limits for "good" and "poor" (Core Web Vitals; TBT stands in for INP in a lab test)
VITALS = [
    ("lcp", "Largest Contentful Paint", "Main content visible", 2500, 4000),
    ("tbt", "Total Blocking Time", "Page reacts to taps", 200, 600),
    ("cls", "Cumulative Layout Shift", "Nothing jumps while loading", 0.1, 0.25),
]
MAX_RESULTS, MAX_ISSUES, KEEP = 80, 10, 120


def token_ok(header):
    """True when the request carries `Authorization: Bearer <LIGHTHOUSE_TOKEN>` (compared in constant time)."""
    expected = getattr(settings, "LIGHTHOUSE_TOKEN", "")
    given = header[7:] if header.startswith("Bearer ") else ""
    return bool(expected) and hmac.compare_digest(given.encode(), expected.encode())


def _score(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return max(0, min(100, round(v)))


def _number(v, limit):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
        return None
    return round(min(v, limit), 3)


def _text(v, length):
    return str(v)[:length] if isinstance(v, (str, int, float)) and not isinstance(v, bool) else ""


def clean(data):
    """The workflow's summary, checked and trimmed. Raises ValueError with a short reason when it is unusable."""
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ValueError("expected an object with a results list")
    try:
        ran_at = datetime.fromisoformat(str(data.get("ran_at", "")).replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("ran_at must be an ISO date and time") from None
    if timezone.is_naive(ran_at):
        ran_at = ran_at.replace(tzinfo=UTC)
    report_url = _text(data.get("report_url"), 300)
    if not report_url.startswith("https://github.com/"):
        report_url = ""
    results = []
    for r in data["results"][:MAX_RESULTS]:
        if not isinstance(r, dict) or r.get("mode") not in MODES:
            continue
        path = _text(r.get("url"), 200)
        if not path.startswith("/"):
            continue
        scores, metrics = r.get("scores") or {}, r.get("metrics") or {}
        if not isinstance(scores, dict) or not isinstance(metrics, dict):
            continue
        issues = []
        for i in (r.get("issues") or [])[:MAX_ISSUES]:
            if isinstance(i, dict) and _text(i.get("title"), 200):
                issues.append(
                    {
                        "id": _text(i.get("id"), 80),
                        "title": _text(i.get("title"), 200),
                        "value": _text(i.get("value"), 80),
                    }
                )
        results.append(
            {
                "url": path,
                "mode": r["mode"],
                "scores": {k: _score(scores.get(k)) for k, _, _ in CATEGORIES},
                "metrics": {k: _number(metrics.get(k), 600000) for k in METRICS},
                "issues": issues,
            }
        )
    if not results:
        raise ValueError("no usable results")
    return {"ran_at": ran_at, "version": _text(data.get("version"), 20), "report_url": report_url, "results": results}


def save(data):
    run = LighthouseRun.objects.create(**clean(data))
    old = LighthouseRun.objects.values_list("pk", flat=True)[KEEP:]
    LighthouseRun.objects.filter(pk__in=list(old)).delete()
    return run


def _averages(run, mode):
    rows = [r for r in run.results if r["mode"] == mode]
    out = {}
    for key, _, _ in CATEGORIES:
        values = [r["scores"][key] for r in rows if r["scores"].get(key) is not None]
        out[key] = round(sum(values) / len(values)) if values else None
    return out


def rating(value, good, poor):
    if value is None:
        return ""
    return "good" if value <= good else "fair" if value <= poor else "poor"


def score_rating(value):
    """Lighthouse's own colours: 90-100 good, 50-89 needs work, 0-49 poor."""
    if value is None:
        return ""
    return "good" if value >= 90 else "fair" if value >= 50 else "poor"


def _vital_text(key, value):
    if value is None:
        return "–"
    if key == "cls":
        return f"{value:.2f}"
    return f"{value / 1000:.1f} s" if key == "lcp" else f"{round(value)} ms"


def summary():
    runs = list(LighthouseRun.objects.all()[:2])
    info = {
        "configured": bool(getattr(settings, "LIGHTHOUSE_TOKEN", "")),
        "workflow_url": settings.LIGHTHOUSE_WORKFLOW_URL,
        "run": None,
    }
    if not runs:
        return info
    run, prev = runs[0], (runs[1] if len(runs) > 1 else None)
    modes = []
    for mode in MODES:
        now, before = _averages(run, mode), (_averages(prev, mode) if prev else {})
        cards = []
        for key, label, help_text in CATEGORIES:
            v, b = now[key], before.get(key)
            cards.append(
                {
                    "label": label,
                    "help": help_text,
                    "value": v,
                    "rating": score_rating(v),
                    "change": (v - b) if v is not None and b is not None else None,
                }
            )
        modes.append({"name": "Phone" if mode == "mobile" else "Desktop", "cards": cards})

    by_page = {}
    for r in run.results:
        by_page.setdefault(r["url"], {})[r["mode"]] = r["scores"]
    pages = []
    for url, modes_ in by_page.items():
        cells = []
        for key, _, _ in CATEGORIES:
            pair = [(modes_.get(m) or {}).get(key) for m in MODES]
            cells.append([{"value": v, "rating": score_rating(v)} for v in pair])
        pages.append({"url": url, "cells": cells})
    home = next((r for r in run.results if r["url"] == "/" and r["mode"] == "mobile"), None)
    vitals = []
    if home:
        for key, label, plain, good, poor in VITALS:
            v = home["metrics"].get(key)
            vitals.append(
                {"label": label, "plain": plain, "text": _vital_text(key, v), "rating": rating(v, good, poor)}
            )

    counts = {}
    for r in run.results:
        for i in r["issues"]:
            item = counts.setdefault(i["title"], {"title": i["title"], "pages": set(), "modes": set()})
            item["pages"].add(r["url"])
            item["modes"].add("phone" if r["mode"] == "mobile" else "desktop")
    issues = sorted(counts.values(), key=lambda i: (-len(i["pages"]), i["title"]))[:8]
    for i in issues:
        i["pages"], i["modes"] = len(i["pages"]), " + ".join(sorted(i["modes"], reverse=True))

    info.update(
        run=run,
        modes=modes,
        pages=sorted(pages, key=lambda p: (p["url"] != "/", p["url"])),
        vitals=vitals,
        issues=issues,
        stale=(timezone.now() - run.ran_at).days >= 3,
    )
    return info
