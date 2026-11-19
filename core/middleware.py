from django.db.models import F
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from .models import Redirect


class RedirectFallbackMiddleware:
    """When an address is not found, send the visitor to its new address if one is listed in Admin → Redirects."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404 or request.path.startswith(("/admin/", "/static/", "/media/")):
            return response
        path = request.path
        candidates = [path, path.rstrip("/") if path != "/" else path, path if path.endswith("/") else path + "/"]
        r = Redirect.objects.filter(old_path__in=candidates, is_active=True).first()
        if r is None:
            return response
        Redirect.objects.filter(pk=r.pk).update(hits=F("hits") + 1)
        target = r.new_path
        if request.META.get("QUERY_STRING") and "?" not in target:
            target += "?" + request.META["QUERY_STRING"]
        return (HttpResponsePermanentRedirect if r.permanent else HttpResponseRedirect)(target)
