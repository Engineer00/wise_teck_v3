"""Admin panel, drafts, scheduled publishing and version history."""

from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import Client
from django.utils import timezone

from core import versioning
from core.models import BlogPost, FooterColumn, Page, Revision, Section, SiteSettings

from .base import SeededTestCase, section_post

MARKER = "Incubation &amp; <span"  # a plain-text part of the About intro title, as rendered


class AdminPanelTest(SeededTestCase):
    def test_login_required(self):
        self.assertEqual(Client().get("/admin/").status_code, 302)

    def test_login(self):
        r = Client().post("/admin/login/", {"username": "tester", "password": "pw-tester-123"})
        self.assertEqual(r.status_code, 302)

    def test_original_admin_address_redirects(self):
        r = Client().get("/adminpanel/login/?next=/admin/pages/")
        self.assertEqual(r["Location"], "/admin/login/?next=/admin/pages/")

    def test_every_screen_opens(self):
        a = self.admin_client()
        for res in [
            "pages",
            "sections",
            "menu",
            "programs",
            "footer",
            "redirects",
            "success-stories",
            "team",
            "blogs",
            "services",
            "courses",
            "messages",
        ]:
            with self.subTest(resource=res):
                self.assertEqual(a.get(f"/admin/{res}/").status_code, 200)
        self.assertEqual(a.get("/admin/").status_code, 200)
        self.assertEqual(a.get(f"/admin/site-settings/{SiteSettings.load().pk}/change/").status_code, 200)

    def test_section_form_saves(self):
        s = Section.objects.get(page__slug="home", layout="home_hero")
        r = self.admin_client().post(f"/admin/sections/{s.pk}/change/", section_post(s, title="Saved Through Admin"))
        self.assertEqual(r.status_code, 302)
        s.refresh_from_db()
        self.assertEqual(s.title, "Saved Through Admin")

    def test_reserved_page_address_refused(self):
        p = Page.objects.get(slug="placement")
        r = self.admin_client().post(
            f"/admin/pages/{p.pk}/change/",
            {"title": p.title, "meta_description": p.meta_description, "is_active": "on", "slug": "admin"},
        )
        self.assertContains(r, "used by the system")


class HistoryTest(SeededTestCase):
    def setUp(self):
        self.a = self.admin_client()
        self.about = Page.objects.get(slug="about")
        self.intro = self.about.sections.get(layout="split", eyebrow="Who We Are")

    def test_edit_keeps_previous_version_and_restore_brings_it_back(self):
        self.a.post(
            f"/admin/sections/{self.intro.pk}/change/", section_post(self.intro, title="History Test", highlight="")
        )
        self.assertContains(Client().get("/about/"), "History Test")
        rev = Revision.objects.get(content_type__model="page", object_id=self.about.pk)
        self.assertIn("Before editing section", rev.reason)
        self.assertContains(self.a.get(f"/preview/version/{rev.pk}/"), MARKER)  # preview the old version
        self.assertEqual(Page.objects.count(), 14)  # preview left nothing behind
        self.a.post(f"/admin/versions/{rev.pk}/restore/", {"back": "/admin/"})
        page = Client().get("/about/")
        self.assertContains(page, MARKER)
        self.assertNotContains(page, "History Test")
        self.assertTrue(
            Revision.objects.filter(object_id=self.about.pk, reason__startswith="Before restoring").exists()
        )

    def test_saving_without_changes_adds_no_version(self):
        self.a.post(f"/admin/sections/{self.intro.pk}/change/", section_post(self.intro))
        self.assertFalse(Revision.objects.exists())

    def test_page_settings_edit_keeps_the_old_values(self):
        """Regression: a validated form puts new values on the object before saving.

        The 'before' copy must be the old one."""
        col = FooterColumn.objects.first()
        n = col.links.count()
        data = {
            "title": "Renamed Column",
            "order": col.order,
            "links-TOTAL_FORMS": n,
            "links-INITIAL_FORMS": n,
            "links-MIN_NUM_FORMS": 0,
            "links-MAX_NUM_FORMS": 1000,
        }
        for i, link in enumerate(col.links.all()):
            data.update(
                {
                    f"links-{i}-id": link.pk,
                    f"links-{i}-label": link.label,
                    f"links-{i}-url": link.url,
                    f"links-{i}-order": link.order,
                }
            )
        data["links-0-DELETE"] = "on"
        self.a.post(f"/admin/footer/{col.pk}/change/", data)
        rev = Revision.objects.get(content_type__model="footercolumn", object_id=col.pk)
        self.a.post(f"/admin/versions/{rev.pk}/restore/", {"back": "/admin/"})
        col.refresh_from_db()
        self.assertNotEqual(col.title, "Renamed Column")
        self.assertEqual(col.links.count(), n)

    def test_deleted_section_can_be_restored(self):
        cta = self.about.sections.get(layout="cta")
        self.a.post(f"/admin/sections/{cta.pk}/delete/")
        self.assertNotContains(Client().get("/about/"), 'id="cta"')
        rev = Revision.objects.get(object_id=self.about.pk, reason__startswith="Before deleting")
        self.a.post(f"/admin/versions/{rev.pk}/restore/", {"back": "/admin/"})
        self.assertContains(Client().get("/about/"), 'id="cta"')


class DraftsTest(SeededTestCase):
    def setUp(self):
        self.a = self.admin_client()
        self.about = Page.objects.get(slug="about")

    def _draft_with_title(self, title):
        self.a.post(f"/admin/pages/{self.about.pk}/create-draft/")
        draft = Page.objects.drafts().get(draft_of=self.about)
        s = draft.sections.get(layout="split", eyebrow="Who We Are")
        self.a.post(f"/admin/sections/{s.pk}/change/", section_post(s, title=title, highlight=""))
        return draft

    def test_draft_is_private_until_published(self):
        draft = self._draft_with_title("Draft Only Title")
        self.assertEqual(draft.sections.count(), self.about.sections.count())
        self.assertNotContains(Client().get("/about/"), "Draft Only Title")
        self.assertContains(self.a.get(f"/preview/page/{draft.pk}/"), "Draft Only Title")
        self.assertEqual(Client().get(f"/preview/page/{draft.pk}/").status_code, 302)  # visitors can't preview
        self.assertEqual(Client().get(f"/{draft.slug}/").status_code, 404)
        self.a.post(f"/admin/pages/{draft.pk}/publish/")
        self.assertContains(Client().get("/about/"), "Draft Only Title")
        self.assertFalse(Page.objects.drafts().exists())
        self.assertEqual(Page.objects.get(pk=self.about.pk).slug, "about")
        self.assertTrue(Revision.objects.filter(object_id=self.about.pk, reason="Before publishing a draft").exists())

    def test_scheduled_draft_goes_live_by_itself(self):
        draft = self._draft_with_title("Scheduled Title")
        future = timezone.localtime() + timedelta(hours=2)
        self.a.post(
            f"/admin/pages/{draft.pk}/change/",
            {
                "title": draft.title,
                "meta_description": draft.meta_description,
                "publish_at": future.strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertNotContains(Client().get("/about/"), "Scheduled Title")
        Page.objects.filter(pk=draft.pk).update(publish_at=timezone.now() - timedelta(minutes=1))
        self.assertContains(Client().get("/about/"), "Scheduled Title")

    def test_publish_scheduled_command(self):
        draft = versioning.create_draft(self.about)
        Page.objects.filter(pk=draft.pk).update(publish_at=timezone.now() - timedelta(minutes=1))
        call_command("publish_scheduled", stdout=StringIO())
        self.assertFalse(Page.objects.drafts().exists())

    def test_scheduled_blog_post_hidden_until_its_time(self):
        post = BlogPost.objects.first()
        BlogPost.objects.filter(pk=post.pk).update(publish_at=timezone.now() + timedelta(days=1))
        self.assertNotContains(Client().get("/blog/"), post.title)
        self.assertEqual(Client().get(post.get_absolute_url()).status_code, 404)
        BlogPost.objects.filter(pk=post.pk).update(publish_at=timezone.now() - timedelta(minutes=1))
        self.assertContains(Client().get("/blog/"), post.title)
