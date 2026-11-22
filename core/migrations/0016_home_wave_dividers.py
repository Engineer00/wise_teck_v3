"""Wave dividers after the home page's weekend-courses and success-stories sections, so every gap between home
sections has one (before, the last three sections ran together and the weekend card read as part of the stories).
Only sections that still have no divider are changed; a choice made in the admin is kept."""

from django.db import migrations

# (layout on the home page, divider style)
DIVIDERS = [("home_weekend", "a"), ("home_stories", "b")]


def change(apps, add):
    Section = apps.get_model("core", "Section")
    for layout, style in DIVIDERS:
        before, after = ("", style) if add else (style, "")
        Section.objects.filter(page__slug="home", layout=layout, divider_after=before).update(divider_after=after)


class Migration(migrations.Migration):
    dependencies = [("core", "0015_shorter_button_labels")]
    operations = [migrations.RunPython(lambda apps, se: change(apps, True), lambda apps, se: change(apps, False))]
