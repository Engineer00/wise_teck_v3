"""Collaborator cards show the logo and the name only: the "Industry Collaborator" line under the name is cleared
(only where it still has that seed text, so anything typed in the admin is kept)."""
from django.db import migrations


def forwards(apps, schema_editor):
    Item = apps.get_model("core", "Item")
    Item.objects.filter(section__layout="home_partners", subtitle="Industry Collaborator").update(subtitle="")


def backwards(apps, schema_editor):
    Item = apps.get_model("core", "Item")
    Item.objects.filter(section__layout="home_partners", link_url="", subtitle="").update(subtitle="Industry Collaborator")


class Migration(migrations.Migration):
    dependencies = [("core", "0012_story_portraits")]
    operations = [migrations.RunPython(forwards, backwards)]
