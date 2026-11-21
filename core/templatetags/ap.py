"""Small helpers for the admin panel templates."""
from django import template

register = template.Library()


@register.filter
def file_url(value):
    """URL of an uploaded file, or '' when there is none (FieldFile.url raises if empty)."""
    try:
        return value.url if value else ""
    except (ValueError, AttributeError):
        return ""


@register.filter
def is_image(value):
    name = getattr(value, "name", "") or ""
    return name.lower().rsplit(".", 1)[-1] in {"jpg", "jpeg", "png", "webp", "gif", "svg", "avif"}


@register.simple_tag
def scheme_presets():
    """The ready-made colour schemes for the Site Settings picker."""
    from core import theme
    return [{"key": k, "name": n, "primary": a, "accent": b, "dark": c} for k, n, a, b, c in theme.PRESETS]
