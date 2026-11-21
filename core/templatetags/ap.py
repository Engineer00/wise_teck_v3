"""Small helpers for the admin panel templates."""

from django import template

from core import images

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


@register.simple_tag
def image_size(field):
    """Recommended upload size for a photo field that always shows in the same place (core/images.py)."""
    model = getattr(getattr(field.form, "_meta", None), "model", None)
    if model is None:
        return None
    return images.size_hint(images.FIELD_SLOTS.get(f"{model._meta.model_name}.{field.name}", ""))
