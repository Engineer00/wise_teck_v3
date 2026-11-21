"""Shrink and compress uploaded photos so pages stay fast (page speed is part of SEO).

Every new upload to an image field is: turned the right way up (phone photos), resized to at most
MAX_SIDE pixels on its longest side, stripped of camera metadata (location etc.) and re-compressed.
SVG, GIF and small files are left as they are. Existing files are never touched.
"""

import io
import logging
import os
from pathlib import Path
from urllib.parse import unquote

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

log = logging.getLogger(__name__)
MAX_SIDE = 2000
QUALITY = 82
SKIP_UNDER = 150 * 1024  # bytes: small files that are already small enough in size and pixels


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
        if size and len(data) >= size:  # never make a file bigger
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
            continue  # nothing new uploaded
        smaller = optimise(f.file if hasattr(f, "file") else f)
        if smaller is not None:
            setattr(instance, field.attname, smaller)


# ------------------------------------------------------------------------------------- responsive copies
# Every uploaded photo is also served as WebP copies at a few widths (srcset), so a phone downloads a
# 480px image instead of a 2000px one. Copies live in MEDIA_ROOT/_v/, are made on first use (or ahead of
# time by `manage.py make_image_variants`) and are rebuilt when the original changes.
VARIANT_WIDTHS = (480, 800, 1200, 1600)
VARIANT_DIR = "_v"
RESPONSIVE = (".jpg", ".jpeg", ".png", ".webp")


def _source(url):
    """The local file behind a /media/ URL, or None (pasted links to other sites, SVG, GIF, missing files)."""
    if not url or not url.startswith(settings.MEDIA_URL) or not url.lower().endswith(RESPONSIVE):
        return None, ""
    name = unquote(url[len(settings.MEDIA_URL) :])
    root = Path(settings.MEDIA_ROOT).resolve()
    path = (root / name).resolve()
    if root not in path.parents or not path.is_file():  # never read or write outside MEDIA_ROOT
        return None, ""
    return path, name


def _variant(src, name, width):
    """Make (once) a WebP copy of src at the given width; returns its media-relative name, or '' on failure."""
    from PIL import Image

    rel = f"{VARIANT_DIR}/{name.rsplit('.', 1)[0]}-{width}.webp"
    out = Path(settings.MEDIA_ROOT) / rel
    try:
        if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
            return rel
        out.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            tmp = f"{out}.{os.getpid()}.tmp"
            im.save(tmp, "WEBP", quality=QUALITY, method=6)
        os.replace(tmp, out)  # atomic: a half-written file is never served
        return rel
    except Exception:
        log.exception("Could not make a %spx copy of %s", width, name)
        return ""


def srcset(url):
    """'srcset' value for an uploaded photo: WebP copies at VARIANT_WIDTHS up to the photo's own width."""
    from PIL import Image

    src, name = _source(url)
    if src is None:
        return ""
    try:
        with Image.open(src) as im:
            own = im.width
    except Exception:
        return ""
    widths = [w for w in VARIANT_WIDTHS if w < own] + [own]
    parts = [f"{settings.MEDIA_URL}{rel} {w}w" for w in widths if (rel := _variant(src, name, w))]
    return ", ".join(parts)


# ------------------------------------------------------------------------------------ recommended sizes
# Best upload size per image slot: twice the largest size the slot is drawn at (sharp on phones and laptops
# with high-density screens), in the slot's shape. Bigger photos are fine: they are resized automatically.
# The admin shows these next to every photo field; README.md has the same table.
SLOTS = {
    "hero": (1920, 800, "Wide banner: inner-page hero photo, and the photo at the top of a blog post or story."),
    "hero2": (1200, 500, "Second hero photo, shown next to the first one when the hero has stats."),
    "about": (1200, 800, "Home · About photo (framed, landscape)."),
    "split": (1400, 1050, "Photo beside text (4:3 landscape)."),
    "weekend": (1400, 960, "Home · Weekend courses photo (landscape)."),
    "partner": (1440, 600, "Home · Corporate collaborations photo (wide)."),
    "card": (800, 500, "Card photo (16:10): programs, earning blocks, team, blog cards."),
    "tile": (800, 450, "Home · photo tile (16:9)."),
    "logo2": (400, 200, "Collaborator logo: transparent PNG or SVG."),
    "blog": (1920, 1080, "Blog photo: a 16:10 card on lists and a wide banner on the post (keep the subject centred)."),
    "story": (1000, 1000, "Square photo of the person: round on lists, centre of a wide banner on the story page."),
    "team": (800, 500, "Team card photo (16:10, head and shoulders centred)."),
    "icon": (112, 112, "Small icon: SVG is best; PNG with a transparent background also works."),
    "logo": (
        512,
        512,
        "Round logo: a square PNG with a transparent background; shown 40–48px in the header and "
        "footer and larger on the home page and the 3D coin.",
    ),
    "favicon": (512, 512, "Browser tab icon: square PNG."),
    "share": (1200, 630, "Sharing preview on WhatsApp, Facebook, LinkedIn and X."),
}
# Fields that always show the same slot. Section and card photos depend on the section type (core/layouts.py).
FIELD_SLOTS = {
    "sitesettings.logo": "logo",
    "sitesettings.favicon": "favicon",
    "sitesettings.share_image": "share",
    "page.share_image": "share",
    "blogpost.featured_image": "blog",
    "successstory.image": "story",
    "teammember.image": "team",
    "service.icon_file": "icon",
}


def size_hint(slot):
    """{'size': '1920 × 800 px', 'tip': 'where it shows …'} for a slot, or None."""
    if slot not in SLOTS:
        return None
    w, h, where = SLOTS[slot]
    return {"size": f"{w} × {h} px", "tip": f"{where} Best size {w} × {h} px; bigger photos are resized automatically."}


# How wide each slot is drawn (the srcset 'sizes' attribute), from the layout at 390 / 768 / 1024 / 1440px.
DRAWN = {
    "hero": "(max-width:1024px) 100vw, 1160px",
    "hero2": "(max-width:640px) 50vw, 580px",
    "about": "(max-width:640px) 100vw, 600px",
    "split": "(max-width:1024px) 100vw, 560px",
    "weekend": "(max-width:1024px) 100vw, 310px",
    "partner": "(max-width:1024px) 100vw, 560px",
    "card": "(max-width:640px) 100vw, 370px",
    "tile": "(max-width:640px) 100vw, 240px",
    "logo2": "200px",
    "story": "110px",
}
