"""Shrink and compress uploaded photos so pages stay fast (page speed is part of SEO).

Every new upload to an image field is: turned the right way up (phone photos), resized to at most
MAX_SIDE pixels on its longest side, stripped of camera metadata (location etc.) and re-compressed.
SVG, GIF and small files are left as they are. Existing files are never touched.
"""
import io
import logging

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

log = logging.getLogger(__name__)
MAX_SIDE = 2000
QUALITY = 82
SKIP_UNDER = 150 * 1024          # bytes: small files that are already small enough in size and pixels


def optimise(upload):
    """Return a smaller ContentFile for an uploaded image, or None to keep the original."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return None
    name = upload.name or "image"
    if name.lower().endswith((".svg", ".svgz", ".gif", ".ico")):
        return None
    try:
        upload.seek(0)
        im = Image.open(upload)
        fmt = (im.format or "").upper()
        if fmt not in {"JPEG", "PNG", "WEBP", "MPO"}:
            return None
        size = getattr(upload, "size", 0) or 0
        if size and size < SKIP_UNDER and max(im.size) <= MAX_SIDE:
            upload.seek(0)
            return None
        im = ImageOps.exif_transpose(im)
        if max(im.size) > MAX_SIDE:
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        buf = io.BytesIO()
        if fmt in {"JPEG", "MPO"}:
            im.convert("RGB").save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        elif fmt == "WEBP":
            im.save(buf, "WEBP", quality=QUALITY, method=6)
        else:
            im.save(buf, "PNG", optimize=True)
        data = buf.getvalue()
        if size and len(data) >= size:          # never make a file bigger
            upload.seek(0)
            return None
        return ContentFile(data, name=name.rsplit("/", 1)[-1])
    except Exception:
        log.exception("Could not optimise %s; keeping the original", name)
        try:
            upload.seek(0)
        except Exception:
            pass
        return None


@receiver(pre_save)
def optimise_new_uploads(sender, instance, **kwargs):
    if sender._meta.app_label != "core":
        return
    for field in sender._meta.concrete_fields:
        if not isinstance(field, models.ImageField):
            continue
        f = getattr(instance, field.attname)
        if not f or getattr(f, "_committed", True):
            continue                              # nothing new uploaded
        smaller = optimise(f.file if hasattr(f, "file") else f)
        if smaller is not None:
            setattr(instance, field.attname, smaller)
