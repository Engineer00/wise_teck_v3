"""Publish page drafts whose 'Go live at' time has passed.

The site also does this on the first page view after that time, so this command only makes the timing
exact on a quiet site. On the server, run it every minute (see DEPLOY.md):

    * * * * *  cd /srv/wiseteck/app && set -a && . /srv/wiseteck/.env && ../venv/bin/python manage.py publish_scheduled

Blog posts and success stories need nothing: they simply become visible at their 'Go live at' time.
"""
from django.core.management.base import BaseCommand

from core.versioning import publish_due


class Command(BaseCommand):
    help = "Publish page drafts whose 'Go live at' time has passed."

    def handle(self, *args, **opts):
        pages = publish_due()
        for p in pages:
            self.stdout.write(f"  published: {p.get_absolute_url()} ({p.title})")
        if pages:
            self.stdout.write(self.style.SUCCESS(f"Published {len(pages)} scheduled draft(s)."))
