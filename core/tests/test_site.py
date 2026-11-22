"""Public site: every page renders and its content is editable."""

from django.test import Client, override_settings

from core.models import NavItem, Page, Program, Section, SiteSettings, SuccessStory

from .base import SeededTestCase


class PagesTest(SeededTestCase):
    def test_every_page_renders(self):
        for page in Page.objects.live():
            with self.subTest(page=page.slug):
                self.assertEqual(Client().get(page.get_absolute_url()).status_code, 200)

    def test_home_has_a_wave_between_every_pair_of_sections(self):
        """Every gap between home sections has a wave divider (alternating crest up / down), none before the footer;
        without one, two neighbouring sections read as a single block."""
        body = [s for s in Page.objects.get(slug="home").sections.filter(is_active=True) if not s.is_hero]
        self.assertEqual([s.divider_after for s in body], ["a", "b"] * 3 + [""])
        self.assertContains(Client().get("/"), 'class="wave-div"', count=len(body) - 1)

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

        r = Client().post(
            "/contact/",
            {
                "name": "Ali Test",
                "phone": "+92 300 1234567",
                "email": "ali@example.com",
                "interest": "Wise College",
                "message": "Hello",
            },
            follow=True,
        )
        m = ContactMessage.objects.get()
        self.assertEqual((m.name, m.interest, m.page), ("Ali Test", "Wise College", "/contact/"))
        self.assertContains(r, "form-msg--success")
