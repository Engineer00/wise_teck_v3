"""Make the responsive WebP copies of every uploaded photo ahead of time (they are otherwise made on first view).

Run after a deploy or a bulk upload:  python manage.py make_image_variants
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core import images


class Command(BaseCommand):
    help = "Make the responsive WebP copies (srcset) of every photo in MEDIA_ROOT."

    def handle(self, *args, **options):
        root = Path(settings.MEDIA_ROOT)
        done = 0
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root).as_posix()
            if rel.startswith(images.VARIANT_DIR + "/") or path.suffix.lower() not in images.RESPONSIVE:
                continue
            if images.srcset(settings.MEDIA_URL + rel):
                done += 1
        self.stdout.write(self.style.SUCCESS(f"Responsive copies ready for {done} photos."))
