import time

from django.db.models import Prefetch

from . import theme
from .models import FooterColumn, NavItem, Program, SiteSettings

ASSET_V = time.strftime("%Y%m%d%H%M%S")  # cache-buster: browsers re-fetch CSS/JS after each deploy / restart


def site(request):
    if request.path.startswith("/admin"):
        site_settings = SiteSettings.load()
        return {
            "site": site_settings,
            "site_logo": site_settings.logo_src,
            "asset_v": ASSET_V,  # admin panel
            "theme": None,
            "theme_css": "",
            "theme_map": "",
            "theme_preview": "",
        }
    children = NavItem.objects.filter(is_active=True)
    site_settings = SiteSettings.load()
    scheme, preview_name = _scheme(request, site_settings)
    request.uses_analytics = bool(site_settings.ga_id)  # AnalyticsCSPMiddleware allows Google's scripts on these pages
    return {
        "site": site_settings,
        "theme": scheme,
        "theme_css": theme.css_overrides(scheme),
        "theme_map": theme.js_map(scheme),
        "theme_preview": preview_name,
        "nav": NavItem.objects.filter(parent__isnull=True, is_active=True).prefetch_related(
            Prefetch("children", queryset=children)
        ),
        "footer_columns": FooterColumn.objects.prefetch_related("links"),
        "programs": Program.objects.filter(is_active=True),
        "asset_v": ASSET_V,
    }


class _Preview:
    """Unsaved custom colours from the admin's Preview button."""

    def __init__(self, query):
        self.color_scheme = theme.CUSTOM
        self.color_primary, self.color_accent, self.color_dark = (
            query.get(k, "") for k in ("primary", "accent", "dark")
        )


def _scheme(request, site_settings):
    """(active scheme or None, name of a previewed scheme or "")."""
    key = request.GET.get("scheme")
    if key is None or not (request.user.is_authenticated and request.user.is_staff):
        return theme.resolve(site_settings), ""
    source = _Preview(request.GET) if key == theme.CUSTOM else site_settings
    name = dict(theme.CHOICES).get(key, "")
    return theme.resolve(source, preview=key), name
