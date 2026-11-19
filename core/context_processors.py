import time

from django.db.models import Prefetch

from .models import FooterColumn, NavItem, Program, SiteSettings

ASSET_V = time.strftime("%Y%m%d%H%M%S")   # cache-buster: browsers re-fetch CSS/JS after each deploy / restart


def site(request):
    if request.path.startswith("/admin"):
        return {"site_logo": SiteSettings.load().logo_src, "asset_v": ASSET_V}     # admin panel: the logo uploaded in Site Settings, if any
    children = NavItem.objects.filter(is_active=True)
    return {
        "site": SiteSettings.load(),
        "nav": NavItem.objects.filter(parent__isnull=True, is_active=True).prefetch_related(
            Prefetch("children", queryset=children)),
        "footer_columns": FooterColumn.objects.prefetch_related("links"),
        "programs": Program.objects.filter(is_active=True),
        "asset_v": ASSET_V,
    }
