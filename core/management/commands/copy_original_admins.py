"""Copy the admin logins from the original Wise-Teck site's database, so the same username and password work.

    py manage.py copy_original_admins --db "D:/wise teck site/wise_teck ORIGINAL/db.sqlite3"

Passwords are copied as their stored (hashed) form; nobody needs to know them. Existing users with the
same username are updated. Only staff accounts are copied.
"""
import sqlite3
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

FIELDS = ["username", "password", "email", "first_name", "last_name", "is_staff", "is_superuser", "is_active"]


class Command(BaseCommand):
    help = "Copy staff logins (with their passwords) from the original site's SQLite database."

    def add_arguments(self, parser):
        parser.add_argument("--db", required=True, help="Path to the original site's db.sqlite3")

    def handle(self, *args, db, **opts):
        path = Path(db)
        if not path.exists():
            raise CommandError(f"Not found: {path}")
        con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        rows = con.execute(f"SELECT {', '.join(FIELDS)} FROM auth_user WHERE is_staff = 1").fetchall()
        User = get_user_model()
        for r in rows:
            data = {k: r[k] for k in FIELDS}
            for k in ("is_staff", "is_superuser", "is_active"):
                data[k] = bool(data[k])
            user, created = User.objects.update_or_create(username=data.pop("username"), defaults=data)
            self.stdout.write(f"  {'added' if created else 'updated'}: {user.username}"
                              f"{' (superuser)' if user.is_superuser else ''}")
        self.stdout.write(self.style.SUCCESS(f"Copied {len(rows)} admin login(s) from the original site."))
