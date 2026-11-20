"""Public site: every page renders, matches the v3 design, and its content is editable."""
import importlib.util
from pathlib import Path
from unittest import skipUnless

from django.test import Client, override_settings

from core.models import NavItem, Page, Program, Section, SiteSettings, SuccessStory

from .base import SeededTestCase

V3_DIR = Path(__file__).resolve().parents[3] / "wise-teck-v3"
COMPARE = Path(__file__).resolve().parents[2] / "tools" / "compare_with_v3.py"


class PagesTest(SeededTestCase):
    def test_every_page_renders(self):
        for page in Page.objects.live():
            with self.subTest(page=page.slug):
                self.assertEqual(Client().get(page.get_absolute_url()).status_code, 200)

    def test_unknown_and_unpublished_pages_are_404(self):
        self.assertEqual(Client().get("/no-such-page/").status_code, 404)
        Page.objects.filter(slug="placement").update(is_active=False)
        self.assertEqual(Client().get("/placement/").status_code, 404)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_404_page_uses_site_design_and_noindex(self):
        r = Client().get("/no-such-page/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "noindex", status_code=404)
        self.assertContains(r, 'Page <span class="accent">Not Found', status_code=404)

    def test_every_layout_renders_on_a_new_page(self):
        page = Page.objects.create(slug="layout-test", title="Layout test")
        Section.objects.create(page=page, order=1, layout="page_hero", title="Test", crumbs="Home | /\nTest")
        for n, (layout, _) in enumerate(Section.LAYOUTS, 2):
            Section.objects.create(page=page, order=n, layout=layout, title=f"T {layout}")
        self.assertEqual(Client().get("/layout-test/").status_code, 200)

    @skipUnless(V3_DIR.exists(), "needs ../wise-teck-v3 (the static v3 site)")
    def test_pages_match_the_v3_static_site(self):
        spec = importlib.util.spec_from_file_location("compare_with_v3", COMPARE)
        compare = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compare)
        for v3_file, url in compare.MAP.items():
            with self.subTest(page=url):
                expected = compare.tokens(compare.read_v3(v3_file))
                actual = compare.tokens(Client().get(url).content.decode())
                self.assertEqual(expected, actual)


class EditingTest(SeededTestCase):
    def test_section_title_edit_shows_on_page(self):
        s = Section.objects.get(page__slug="home", layout="home_hero")
        s.title, s.highlight = "Edited Hero Title", "Hero"
        s.save()
        self.assertContains(Client().get("/"), 'Edited <span class="accent">Hero</span> Title')

    def test_hidden_section_disappears(self):
        Section.objects.filter(page__slug="about", anchor="objectives").update(is_active=False)
        self.assertNotContains(Client().get("/about/"), 'id="objectives"')

    def test_program_edit_updates_every_strip(self):
        p = Program.objects.first()
        p.title = "Hub Renamed"
        p.save()
        for url in ("/about/", "/earning-centre/", "/wise-college/"):
            self.assertContains(Client().get(url), "Hub Renamed")

    def test_site_settings_drive_contact_details(self):
        s = SiteSettings.load()
        s.phone = "+92 111 2223333"
        s.save()
        r = Client().get("/placement/")
        self.assertContains(r, "+92 111 2223333")
        self.assertContains(r, "tel:+921112223333")

    def test_menu_edit(self):
        NavItem.objects.filter(label="Placement").update(label="Careers")
        self.assertContains(Client().get("/"), ">Careers</a>")

    def test_publishing_a_story_adds_a_slide(self):
        self.assertEqual(Client().get("/").content.count(b'class="st-slide"'), 2)
        story = SuccessStory.objects.filter(is_active=False).first()
        story.is_active = True
        story.save()
        home = Client().get("/").content
        self.assertEqual(home.count(b'class="st-slide"'), 3)
        self.assertEqual(Client().get(story.get_absolute_url()).status_code, 200)


class ContactFormTest(SeededTestCase):
    def test_required_fields(self):
        r = Client().post("/contact/", {"name": "", "phone": ""})
        self.assertContains(r, "has-error")

    def test_spam_trap(self):
        from core.models import ContactMessage
        Client().post("/contact/", {"name": "Bot", "phone": "1", "website": "spam"})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_message_saved_and_thanked(self):
        from core.models import ContactMessage
        r = Client().post("/contact/", {"name": "Ali Test", "phone": "+92 300 1234567", "email": "ali@example.com",
                                        "interest": "Wise College", "message": "Hello"}, follow=True)
        m = ContactMessage.objects.get()
        self.assertEqual((m.name, m.interest, m.page), ("Ali Test", "Wise College", "/contact/"))
        self.assertContains(r, "form-msg--success")
