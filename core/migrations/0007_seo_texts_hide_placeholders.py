"""Better search-engine descriptions and the blog title; hides the "[Placeholder]" sections.
Only text that still matches the original seed is changed, so edits made in the admin are kept."""
from django.db import migrations

NEW = {
    "corporate-services": [None, None, "IT, software development, digital marketing, and other technology services for companies and businesses.", "Wise-Teck provides IT support, software development, digital marketing and other technology services for companies and businesses of every size."],
    "business-incubation": [None, None, "Wise-Teck helps students turn their business ideas into real businesses through guidance and support.", "The Wise-Teck Business Incubation Centre helps students turn their business ideas into real businesses through mentorship, guidance and support."],
    "about": [
        None,
        None,
        "About Wise-Teck — vision, core objectives and the Wise eco system.",
        "About Wise-Teck, a project of WISE Education Society: our vision, core objectives and the Wise eco system linking education, industry and self-earning."
    ],
    "wise-support-hub": [
        None,
        None,
        "Fully funded intermediate (ICS) education and skills training for orphaned and underprivileged girls.",
        "Wise Support Hub: fully funded intermediate (ICS) education and free professional skills training for orphaned and underprivileged girls."
    ],
    "wise-college": [
        None,
        None,
        "ADP and BS degree programs affiliated with the University of the Punjab.",
        "Wise College offers ADP and BS degree programs affiliated with the University of the Punjab, combined with professional skills training."
    ],
    "professional-paid-courses": [
        None,
        None,
        "Weekend professional training programs for students, graduates and working professionals.",
        "Weekend professional training programs at Wise-Teck for students, graduates and working professionals: practical skills that lead to earning."
    ],
    "earning-centre": [
        None,
        None,
        "Wise-Teck Earning Centre — practical projects, guidance and earning opportunities.",
        "The Wise-Teck Earning Centre turns professional skills into income through practical projects, mentorship, guidance and earning opportunities."
    ],
    "earning-blocks": [
        None,
        None,
        "Six earning blocks at the Wise-Teck Earning Centre.",
        "Explore the six earning blocks at the Wise-Teck Earning Centre and choose the skills, projects and mentorship that lead you to self-earning."
    ],
    "student-loan-scheme": [
        None,
        None,
        "Helping eligible students get loans to start their own businesses.",
        "The Wise-Teck Student Loan Scheme helps eligible students get loans to start their own businesses, with guidance from the idea to launch."
    ],
    "placement": [
        None,
        None,
        "Helping students and graduates find jobs, internships, and earning opportunities.",
        "Wise-Teck job placement and career services help students and graduates find jobs, internships and earning opportunities with industry partners."
    ],
    "success-stories": [
        None,
        None,
        "Success stories from Wise-Teck learners.",
        "Read success stories from Wise-Teck learners who turned professional skills into jobs, earning and businesses of their own."
    ],
    "contact": [
        None,
        None,
        "Contact Wise-Teck — phone, email and address.",
        "Contact Wise-Teck for admissions, programs and partnerships: call +92 300 8410868, email info@wise-teck.org or visit 48-Main Gulberg, Lahore."
    ],
    "blog": [
        "Blog | Wise-Teck",
        "Blog: IT Skills, AI & Self-Earning | Wise-Teck",
        "News, stories and articles from Wise-Teck.",
        "Articles from Wise-Teck on IT skills, AI, cybersecurity and self-earning: practical guides for students, graduates and working professionals."
    ]
}


def forwards(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Section = apps.get_model("core", "Section")
    for slug, (old_t, new_t, old_d, new_d) in NEW.items():
        for page in Page.objects.filter(slug=slug):
            changed = []
            if page.meta_description == old_d:
                page.meta_description = new_d
                changed.append("meta_description")
            if old_t and page.title == old_t:
                page.title = new_t
                changed.append("title")
            if changed:
                page.save(update_fields=changed)
    Section.objects.filter(layout="placeholder", title__startswith="[Placeholder]", is_active=True).update(is_active=False)


def backwards(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Section = apps.get_model("core", "Section")
    for slug, (old_t, new_t, old_d, new_d) in NEW.items():
        Page.objects.filter(slug=slug, meta_description=new_d).update(meta_description=old_d)
        if old_t:
            Page.objects.filter(slug=slug, title=new_t).update(title=old_t)
    Section.objects.filter(layout="placeholder", title__startswith="[Placeholder]").update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [("core", "0006_wordmark_logo")]
    operations = [migrations.RunPython(forwards, backwards)]
