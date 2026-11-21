"""Slow down password guessing and form spam: after too many attempts from one address, it has to wait.

Attempts are kept in the database, so every server worker shares the count. Addresses are stored as a salted
one-way hash, never as the IP itself. Limits: settings.THROTTLE, e.g. {"login": (5, 15)} = 5 tries per 15 minutes.
"""

import hashlib
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import Attempt


def client_ip(request):
    """The visitor's address. Behind Nginx it arrives in X-Real-IP / X-Forwarded-For (see DEPLOY.md)."""
    meta = request.META
    forwarded = meta.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    return meta.get("HTTP_X_REAL_IP") or forwarded or meta.get("REMOTE_ADDR", "")


def _key(request):
    return hashlib.sha256(f"{settings.SECRET_KEY}|{client_ip(request)}".encode()).hexdigest()


def _window(kind):
    limit, minutes = settings.THROTTLE[kind]
    return limit, timezone.now() - timedelta(minutes=minutes)


def blocked(kind, request):
    """True when this address used up its attempts for `kind` in the current window."""
    limit, since = _window(kind)
    return Attempt.objects.filter(kind=kind, key=_key(request), at__gte=since).count() >= limit


def hit(kind, request):
    """Count one attempt (a failed login, a sent message). Old attempts are cleared out on the way."""
    Attempt.objects.filter(at__lt=timezone.now() - timedelta(days=1)).delete()
    Attempt.objects.create(kind=kind, key=_key(request))


def clear(kind, request):
    Attempt.objects.filter(kind=kind, key=_key(request)).delete()


def minutes(kind):
    return settings.THROTTLE[kind][1]
