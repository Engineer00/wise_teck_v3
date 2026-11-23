"""ACF-style custom content: Courses (fixed course fields, Content → Courses) and extra details (label + value
rows an editor adds to a section)."""

import json
from datetime import timedelta

from django.conf import settings
from django.test import Client
from django.utils import timezone
from django.utils.formats import date_format

from core import versioning
from core.layouts import GUIDE
from core.models import Course, Detail, Page, Revision, Section

from .base import SeededTestCase, section_post
from .test_seo import Head

COURSES = "/professional-paid-courses/"


def course_section(html):
    """The HTML of the Courses section on a page."""
    start = html.index('data-layout="courses"')
    return html[start : html.index("</section>", start)]


class CoursesTest(SeededTestCase):
    def test_section_stays_hidden_until_a_course_is_shown(self):
        self.assertNotContains(Client().get(COURSES), 'data-layout="courses"')
        Course.objects.create(name="Hidden Course", is_active=False)
        self.assertNotContains(Client().get(COURSES), 'data-layout="courses"')
        Course.objects.create(name="Graphic Design")
        r = Client().get(COURSES)
        self.assertContains(r, 'data-layout="courses"')
        self.assertContains(r, "<h3>Graphic Design</h3>")
        self.assertNotContains(r, "Hidden Course")

    def test_card_shows_only_the_filled_in_facts_and_hides_a_start_date_that_has_passed(self):
        today = timezone.localdate()
        soon, gone = today + timedelta(days=10), today - timedelta(days=1)
        Course.objects.create(
            name="Web Development",
            short_description="HTML, CSS and JavaScript.",
            duration="3 months",
            fee="Rs 15,000",
            schedule="Sat & Sun, 10 am – 1 pm",
            start_date=soon,
            display_order=1,
        )
        Course.objects.create(name="Last Batch", fee="Rs 9,000", start_date=gone, display_order=2)
        html = course_section(Client().get(COURSES).content.decode())
        first, second = html.split('id="course-')[1:]
        for label, value in [
            ("Duration", "3 months"),
            ("Fee", "Rs 15,000"),
            ("Schedule", "Sat &amp; Sun, 10 am – 1 pm"),
            ("Next start", date_format(soon, "j M Y")),
        ]:
            self.assertIn(f"{label}</dt><dd>{value}</dd>", first)
        self.assertEqual(second.count("<dt>"), 1)  # only the fee: no duration / schedule, the start date has passed
        self.assertIn("Fee</dt><dd>Rs 9,000</dd>", second)
        self.assertNotIn(date_format(gone, "j M Y"), html)

    def test_card_labels_come_from_the_section(self):
        Course.objects.create(name="Python", fee="Rs 10,000")
        Section.objects.filter(layout="courses").update(list_items="Length\nCost")
        self.assertIn("Cost</dt><dd>Rs 10,000</dd>", course_section(Client().get(COURSES).content.decode()))

    def test_card_links_to_the_enquiry_form_with_paid_courses_chosen(self):
        Course.objects.create(name="AI Tools")
        Course.objects.create(name="Own Page", link_url="/wise-college/")
        html = course_section(Client().get(COURSES).content.decode())
        self.assertIn('href="/contact/?interest=Professional+Paid+Courses"><span>Enquire Now', html)
        self.assertIn('href="/wise-college/"><span>Enquire Now', html)
        form = Client().get("/contact/?interest=Professional+Paid+Courses")
        self.assertContains(form, "<option selected>Professional Paid Courses</option>")

    def test_courses_are_listed_for_search_engines(self):
        c = Course.objects.create(name="Data Analysis", short_description="Excel and Power BI.")
        Course.objects.create(name="No Description")  # Google requires a description: left out
        h = Head()
        h.feed(Client().get(COURSES).content.decode())
        lists = [g for g in json.loads("".join(h.ld))["@graph"] if g["@type"] == "ItemList"]
        self.assertEqual(len(lists), 1)
        [entry] = lists[0]["itemListElement"]
        self.assertEqual(entry["item"]["@type"], "Course")
        self.assertEqual(entry["item"]["name"], "Data Analysis")
        self.assertTrue(entry["item"]["url"].endswith(f"{COURSES}#course-{c.pk}"))

    def test_admin_adds_a_course(self):
        a = self.admin_client()
        self.assertEqual(a.get("/admin/courses/add/").status_code, 200)
        start = timezone.localdate() + timedelta(days=30)
        r = a.post(
            "/admin/courses/add/",
            {
                "name": "Digital Marketing",
                "fee": "Rs 12,000",
                "start_date": start.isoformat(),
                "display_order": 1,
                "is_active": "on",
            },
        )
        self.assertEqual(r.status_code, 302)
        listing = a.get("/admin/courses/")
        self.assertContains(listing, f"{start:%b %d, %Y}")
        self.assertNotContains(listing, f"{start:%b %d, %Y} 00:00")  # a date, shown without a time
        self.assertContains(Client().get(COURSES), date_format(start, "j M Y"))


class ExtraDetailsTest(SeededTestCase):
    def setUp(self):
        self.about = Page.objects.get(slug="about")
        self.intro = self.about.sections.get(layout="split", eyebrow="Who We Are")

    def test_details_show_as_a_table_in_the_text_column(self):
        Detail.objects.create(section=self.intro, label="Founded", value="**2019**", order=1)
        Detail.objects.create(section=self.intro, label="Campus", value="Lahore", order=2)
        self.assertContains(
            Client().get("/about/"),
            '<dl class="details glass reveal"><div><dt>Founded</dt><dd><b>2019</b></dd></div>'
            "<div><dt>Campus</dt><dd>Lahore</dd></div></dl>",
        )

    def test_section_form_has_the_details_box(self):
        r = self.admin_client().get(f"/admin/sections/{self.intro.pk}/change/")
        self.assertContains(r, 'data-inline="details"')
        self.assertContains(r, 'name="details-TOTAL_FORMS"')

    def test_admin_saves_details_and_version_history_keeps_them(self):
        a = self.admin_client()
        added = {"details-0-label": "Fee", "details-0-value": "Rs 15,000", "details-0-order": "1"}
        r = a.post(f"/admin/sections/{self.intro.pk}/change/", section_post(self.intro, **added))
        self.assertEqual(r.status_code, 302)
        self.assertEqual([(d.label, d.value) for d in self.intro.details.all()], [("Fee", "Rs 15,000")])
        self.assertContains(Client().get("/about/"), "<dt>Fee</dt>")
        # restoring the version from before the change removes the detail; undoing that restore brings it back
        before = Revision.objects.get(content_type__model="page", object_id=self.about.pk)
        a.post(f"/admin/versions/{before.pk}/restore/", {"back": "/admin/"})
        self.assertNotContains(Client().get("/about/"), "<dt>Fee</dt>")
        undo = Revision.objects.get(object_id=self.about.pk, reason__startswith="Before restoring")
        a.post(f"/admin/versions/{undo.pk}/restore/", {"back": "/admin/"})
        self.assertContains(Client().get("/about/"), "<dt>Fee</dt>")

    def test_drafts_copy_the_details(self):
        Detail.objects.create(section=self.intro, label="Fee", value="Rs 15,000")
        draft = versioning.create_draft(self.about)
        self.assertEqual(Detail.objects.filter(section__page=draft).count(), 1)
        versioning.publish_draft(draft)
        self.assertEqual(list(Detail.objects.filter(section__page=self.about).values_list("label", flat=True)), ["Fee"])

    def test_details_box_matches_the_templates(self):
        """The admin offers the Extra details box exactly for the layouts whose template draws the table."""
        folder = settings.BASE_DIR / "templates" / "sections"
        for layout, _ in Section.LAYOUTS:
            with self.subTest(layout=layout):
                drawn = "sections/_details.html" in (folder / f"{layout}.html").read_text(encoding="utf-8")
                self.assertEqual(bool(GUIDE[layout]["details"]), drawn)
