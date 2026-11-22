"""Professional Paid Courses page: the hidden "[Placeholder] Course List, Fees & Timings" notice becomes the new
Courses section (cards from Content → Courses). It shows nothing until the first course is added, so the live page
looks the same until then. Changed only while the placeholder is still the seeded one."""

from django.db import migrations

PAGE = "professional-paid-courses"
PLACEHOLDER = {
    "layout": "placeholder",
    "title": "[Placeholder] Course List, Fees & Timings",
    "body": "Add each course with its duration, fee, weekend schedule and next start date — to be supplied by Wise-Teck.",
    "spacing": "tight",
    "is_active": False,
    "anchor": "",
    "eyebrow": "",
    "highlight": "",
    "subtitle": "",
    "list_items": "",
    "item_label": "",
    "button_url": "",
}
COURSES = {
    "layout": "courses",
    "title": "Course List, Fees & Timings",
    "body": "",
    "spacing": "",
    "is_active": True,
    "anchor": "courses",
    "eyebrow": "Weekend Courses",
    "highlight": "Fees & Timings",
    "subtitle": "Choose a course and send us an enquiry for the next weekend batch.",
    "list_items": "Duration\nFee\nSchedule\nNext start",
    "item_label": "Enquire Now",
    "button_url": "/contact/?interest=Professional+Paid+Courses",
}


def swap(apps, old, new):
    Section = apps.get_model("core", "Section")
    Section.objects.filter(page__slug=PAGE, layout=old["layout"], title=old["title"]).update(**new)


class Migration(migrations.Migration):
    dependencies = [("core", "0017_courses_and_section_details")]
    operations = [
        migrations.RunPython(
            lambda apps, se: swap(apps, PLACEHOLDER, COURSES), lambda apps, se: swap(apps, COURSES, PLACEHOLDER)
        )
    ]
