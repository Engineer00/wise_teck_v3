"""Search-friendly page titles (30–60 characters) and blog summaries (at most 160 characters).
Only text that still matches the original seed is changed, so edits made in the admin are kept."""

from django.db import migrations

TITLES = {
    "about": [
        "About Wise-Teck | Bridging Education, Industry & Self-Earning",
        "About Wise-Teck | Education, Industry & Self-Earning",
    ],
    "wise-support-hub": ["Wise Support Hub | Wise-Teck", "Wise Support Hub | Free Education for Girls | Wise-Teck"],
    "success-stories": ["Success Stories | Wise-Teck", "Success Stories | From Skills to Jobs & Earning | Wise-Teck"],
}
SUMMARIES = [
    (
        "From help desks to cloud operations, artificial intelligence is rewriting daily IT work. This full guide explains what is changing, where value appears, which skills matter, and how learners can prepare for an AI-assisted career.",
        "From help desks to cloud operations, AI is rewriting daily IT work: what is changing, which skills matter and how to prepare for an AI-assisted career.",
    ),
    (
        "A complete practical guide to cybersecurity for IT learners and professionals: threats, weekly habits, project checklists, cloud risks, incident readiness, and the security mindset every career needs.",
        "A practical cybersecurity guide for IT learners and professionals: common threats, weekly habits, cloud risks, incident readiness and the security mindset.",
    ),
]


def forwards(apps, schema_editor):
    Page, BlogPost = apps.get_model("core", "Page"), apps.get_model("core", "BlogPost")
    for slug, (old, new) in TITLES.items():
        Page.objects.filter(slug=slug, title=old).update(title=new)
    for old, new in SUMMARIES:
        BlogPost.objects.filter(short_description=old).update(short_description=new)


def backwards(apps, schema_editor):
    Page, BlogPost = apps.get_model("core", "Page"), apps.get_model("core", "BlogPost")
    for slug, (old, new) in TITLES.items():
        Page.objects.filter(slug=slug, title=new).update(title=old)
    for old, new in SUMMARIES:
        BlogPost.objects.filter(short_description=new).update(short_description=old)


class Migration(migrations.Migration):
    dependencies = [("core", "0009_site_announcement_404_analytics")]
    operations = [migrations.RunPython(forwards, backwards)]
