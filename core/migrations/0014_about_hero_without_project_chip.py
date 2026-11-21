"""The About hero no longer shows the "A project of Wise Education Society" chip. It is hidden, not deleted, so it
can be switched back on in the admin (Sections -> About hero -> its card)."""

from django.db import migrations

CHIP = {
    "section__page__slug": "about",
    "section__layout": "page_hero",
    "group": "facts",
    "title": "A project of Wise Education Society",
}


def forwards(apps, schema_editor):
    apps.get_model("core", "Item").objects.filter(**CHIP).update(is_active=False)


def backwards(apps, schema_editor):
    apps.get_model("core", "Item").objects.filter(**CHIP).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [("core", "0013_collaborators_without_tagline")]
    operations = [migrations.RunPython(forwards, backwards)]
