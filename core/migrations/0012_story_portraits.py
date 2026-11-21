"""The two seed success stories get clean square portraits (their photos were two-photo collages, which looked
broken in the round avatar). Only stories still using the original seed photo are changed."""

from django.db import migrations

SWAPS = [
    ("seed/v3/7c886daaa1d8280e.jpg", "seed/stories/aima-asif.jpg"),
    ("seed/v3/8a77ff59e17fb1a5.jpg", "seed/stories/noshaba.jpg"),
]


def forwards(apps, schema_editor):
    SuccessStory = apps.get_model("core", "SuccessStory")
    for old, new in SWAPS:
        SuccessStory.objects.filter(image=old).update(image=new)


def backwards(apps, schema_editor):
    SuccessStory = apps.get_model("core", "SuccessStory")
    for old, new in SWAPS:
        SuccessStory.objects.filter(image=new).update(image=old)


class Migration(migrations.Migration):
    dependencies = [("core", "0011_visitor_statistics_and_rate_limits")]
    operations = [migrations.RunPython(forwards, backwards)]
