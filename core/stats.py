"""Built-in visitor statistics for the admin dashboard: page views, visitors, top pages, sources and devices.

Privacy by design: no cookies and no IP addresses are stored. A visitor is counted once per day through a one-way
hash of (secret, day, IP, browser) that changes every day, the method privacy-first analytics tools use.
Bots, link-preview fetchers, prefetches, staff, previews and the admin are not counted.
"""

import hashlib
import logging
import re
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count, F, Sum
from django.utils import timezone

from .models import DailyVisit, DailyVisitor, Page
from .throttle import client_ip

log = logging.getLogger(__name__)

BOTS = re.compile(
    r"bot|crawl|spider|slurp|preview|facebookexternalhit|whatsapp|headless|lighthouse|python|curl|wget", re.IGNORECASE
)
SKIP = ("/admin", "/preview/", "/static/", "/media/", "/robots.txt", "/sitemap.xml", "/favicon")
SOURCES = [
    ("google.", "Google"),
    ("bing.", "Bing"),
    ("yahoo.", "Yahoo"),
    ("duckduckgo.", "DuckDuckGo"),
    ("facebook.", "Facebook"),
    ("fb.", "Facebook"),
    ("instagram.", "Instagram"),
    ("linkedin.", "LinkedIn"),
    ("lnkd.in", "LinkedIn"),
    ("t.co", "X"),
    ("x.com", "X"),
    ("twitter.", "X"),
    ("youtube.", "YouTube"),
    ("whatsapp.", "WhatsApp"),
    ("chatgpt.", "ChatGPT"),
    ("perplexity.", "Perplexity"),
]
KEEP_VISITOR_DAYS = 90


def device(user_agent):
    if re.search(r"iPad|Tablet|Android(?!.*Mobile)", user_agent):
        return "tablet"
    return "phone" if re.search(r"Mobi|iPhone|Android", user_agent) else "desktop"


def source(request):
    """Where a visit came from: utm_source, else the referring site's name; '' for direct or same-site visits."""
    utm = request.GET.get("utm_source", "").strip()
    if utm:
        return utm[:120].capitalize()
    host = urlsplit(request.META.get("HTTP_REFERER", "")).hostname or ""
    host = host.removeprefix("www.").removeprefix("m.").removeprefix("l.")
    own = request.get_host().split(":")[0].removeprefix("www.")
    if not host or host == own:
        return ""
    return next((name for key, name in SOURCES if key in host), host)[:120]


def countable(request, response):
    """True for a real person viewing a public page."""
    meta = request.META
    purpose = meta.get("HTTP_SEC_PURPOSE", "") + meta.get("HTTP_PURPOSE", "")
    return (
        request.method == "GET"
        and response.status_code == 200
        and response.get("Content-Type", "").startswith("text/html")
        and not request.path.startswith(SKIP)
        and "static" not in request.GET
        and not BOTS.search(meta.get("HTTP_USER_AGENT") or "bot")
        and "prefetch" not in purpose
        and not (settings.SESSION_COOKIE_NAME in request.COOKIES and request.user.is_staff)
    )


def record(request):
    day = timezone.localdate()
    agent = request.META.get("HTTP_USER_AGENT", "")
    row, created = DailyVisit.objects.get_or_create(
        day=day, path=request.path[:255], source=source(request), device=device(agent), defaults={"views": 1}
    )
    if not created:
        DailyVisit.objects.filter(pk=row.pk).update(views=F("views") + 1)
    key = hashlib.sha256(f"{settings.SECRET_KEY}|{day}|{client_ip(request)}|{agent}".encode()).hexdigest()[:32]
    try:
        DailyVisitor.objects.get_or_create(day=day, key=key)
    except IntegrityError:  # the same visitor opening two pages at the same moment
        pass


class VisitStatsMiddleware:
    """Counts page views for the dashboard. Never slows down or breaks a page: errors are logged and ignored."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if countable(request, response):
                record(request)
        except Exception:
            log.exception("Could not record a page view")
        return response


# ------------------------------------------------------------------------------------------ dashboard
def summary(days=30):
    """Totals with the change against the previous period, a daily series and chart, and the top lists."""
    today = timezone.localdate()
    start, prev_start = today - timedelta(days=days - 1), today - timedelta(days=2 * days - 1)
    DailyVisitor.objects.filter(day__lt=today - timedelta(days=KEEP_VISITOR_DAYS)).delete()

    visits = DailyVisit.objects.filter(day__gte=start)
    views_by_day = dict(visits.values_list("day").annotate(n=Sum("views")))
    people_by_day = dict(DailyVisitor.objects.filter(day__gte=start).values_list("day").annotate(n=Count("id")))
    series = []
    for i in range(days):
        day = start + timedelta(days=i)
        series.append({"day": day, "views": views_by_day.get(day, 0), "visitors": people_by_day.get(day, 0)})

    views, visitors = sum(views_by_day.values()), sum(people_by_day.values())
    prev_views = DailyVisit.objects.filter(day__gte=prev_start, day__lt=start).aggregate(n=Sum("views"))["n"] or 0
    prev_visitors = DailyVisitor.objects.filter(day__gte=prev_start, day__lt=start).count()

    titles = {
        ("/" if p.slug == "home" else f"/{p.slug}/"): p.title.split(" | ")[0]
        for p in Page.objects.live().only("slug", "title")
    }
    top_pages = [
        {"path": path, "title": titles.get(path, path), "views": n}
        for path, n in visits.values_list("path").annotate(n=Sum("views")).order_by("-n")[:8]
    ]
    top_sources = [
        {"name": name or "Direct / typed", "views": n}
        for name, n in visits.values_list("source").annotate(n=Sum("views")).order_by("-n")[:6]
    ]
    by_device = dict(visits.values_list("device").annotate(n=Sum("views")))
    devices = [
        {
            "name": name.capitalize(),
            "views": by_device.get(name, 0),
            "share": round(100 * by_device.get(name, 0) / views) if views else 0,
        }
        for name in ("phone", "tablet", "desktop")
    ]
    return {
        "days": days,
        "views": views,
        "visitors": visitors,
        "views_change": _change(views, prev_views),
        "visitors_change": _change(visitors, prev_visitors),
        "chart": _chart(series),
        "first_day": start,
        "top_pages": top_pages,
        "top_sources": top_sources,
        "devices": devices,
    }


def _change(now, before):
    return round(100 * (now - before) / before) if before else None


def _chart(series, width=600, height=140):
    """SVG points for the daily views line and area. No chart library: pages stay light and the CSP strict."""
    top = max([d["views"] for d in series] + [1])
    step = width / max(len(series) - 1, 1)
    points = [
        (round(i * step, 1), round(height - 8 - (height - 16) * d["views"] / top, 1)) for i, d in enumerate(series)
    ]
    line = " ".join(f"{x},{y}" for x, y in points)
    return {"width": width, "height": height, "line": line, "area": f"0,{height} {line} {width},{height}", "max": top}
