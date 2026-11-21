"""Shorter button labels, so every button on phones and tablets is the standard 244px wide. Only labels that still
have their original seed text are changed; wording typed in the admin is kept. Page titles and menu items are not
touched."""

from django.db import migrations

# (page slug, field, old label, new label)
LABELS = [
    ("home", "button_label", "Explore the Earning Centre", "Visit Earning Centre"),
    ("about", "button_label", "Explore the Earning Centre", "Visit Earning Centre"),
    ("earning-blocks", "button2_label", "About the Earning Centre", "Visit Earning Centre"),
    ("business-incubation", "button_label", "Share Your Business Idea", "Share Your Idea"),
    ("business-incubation", "button2_label", "Student Loan Scheme", "Student Loans"),
    ("student-loan-scheme", "button_label", "Business Incubation Centre", "Incubation Centre"),
    ("contact", "button_label", "Call +92 300 8410868", "Call Us Now"),
]


def change(apps, old_to_new):
    Section = apps.get_model("core", "Section")
    for slug, field, old, new in LABELS:
        before, after = (old, new) if old_to_new else (new, old)
        Section.objects.filter(page__slug=slug, **{field: before}).update(**{field: after})


class Migration(migrations.Migration):
    dependencies = [("core", "0014_about_hero_without_project_chip")]
    operations = [migrations.RunPython(lambda apps, se: change(apps, True), lambda apps, se: change(apps, False))]
