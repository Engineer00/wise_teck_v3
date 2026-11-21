"""Owner features: visitor statistics, SEO health, rate limits, announcement bar, 404 texts, Google Analytics,
responsive photos and the photo-size hints in the admin."""

import shutil
import tempfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from core import images, seo_audit
from core.models import Attempt, BlogPost, DailyVisit, DailyVisitor, Page, SiteSettings, safe_svg
from core.seo import detail_title

from .base import SeededTestCase

BROWSER = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"


class VisitorStatisticsTests(SeededTestCase):
    def test_a_real_visit_is_counted_once_per_day(self):
        self.client.get("/", HTTP_USER_AGENT=BROWSER, HTTP_REFERER="https://www.google.com/")
        self.client.get("/", HTTP_USER_AGENT=BROWSER)
        row = DailyVisit.objects.get(path="/", source="Google")
        self.assertEqual((row.device, row.views), ("phone", 1))
        self.assertEqual(DailyVisit.objects.filter(path="/").count(), 2)  # Google + direct
        self.assertEqual(DailyVisitor.objects.count(), 1)  # same person

    def test_bots_staff_previews_and_errors_are_not_counted(self):
        self.client.get("/", HTTP_USER_AGENT="Googlebot/2.1")
        self.client.get("/?static", HTTP_USER_AGENT=BROWSER)
        self.client.get("/no-such-page/", HTTP_USER_AGENT=BROWSER)
        self.admin_client().get("/", HTTP_USER_AGENT=BROWSER)
        self.assertFalse(DailyVisit.objects.exists())

    def test_dashboard_shows_visitors_seo_and_google_tools(self):
        self.client.get("/about/", HTTP_USER_AGENT=BROWSER)
        html = self.admin_client().get("/admin/").content.decode()
        for text in (
            "Visitors · last 30 days",
            "SEO health",
            "Google tools",
            "search.google.com/search-console",
            "trends.google.com",
            "Most viewed pages",
        ):
            self.assertIn(text, html)


class SeoHealthTests(SeededTestCase):
    def test_seed_content_passes_the_content_checks(self):
        report = seo_audit.audit()
        content = [i for i in report.issues if not i.text.startswith("Site Settings") and i.level != "tip"]
        self.assertEqual(content, [])
        self.assertGreaterEqual(report.score, 95)

    def test_duplicates_and_missing_descriptions_are_errors(self):
        about = Page.objects.get(slug="about")
        Page.objects.filter(slug="contact").update(title=about.title, meta_description="")
        texts = [i.text for i in seo_audit.audit().issues if i.level == "error"]
        self.assertTrue(any("same title" in t for t in texts))
        self.assertTrue(any("no description of its own" in t for t in texts))

    def test_brand_is_left_off_titles_that_would_be_too_long(self):
        site = SiteSettings.load()
        self.assertTrue(detail_title(site, "Short title").endswith(f"| {site.seo_name}"))
        long = "Cybersecurity Basics Every IT Professional Should Master"
        self.assertEqual(detail_title(site, long), long)


class RateLimitTests(SeededTestCase):
    def test_password_guessing_is_stopped(self):
        for _ in range(5):
            self.client.post("/admin/login/", {"username": "tester", "password": "wrong"})
        r = self.client.post("/admin/login/", {"username": "tester", "password": "pw-tester-123"})
        self.assertEqual(r.status_code, 429)  # even the right password waits
        self.assertContains(r, "Too many attempts", status_code=429)

    def test_successful_login_clears_the_count(self):
        self.client.post("/admin/login/", {"username": "tester", "password": "wrong"})
        r = self.client.post("/admin/login/", {"username": "tester", "password": "pw-tester-123"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Attempt.objects.filter(kind="login").exists())

    def test_contact_form_flooding_is_stopped(self):
        data = {"section": "1", "name": "Ali", "phone": "0300 1234567", "email": "", "interest": "", "message": "Hi"}
        for _ in range(5):
            self.client.post("/contact/", data)
        r = self.client.post("/contact/", data)
        self.assertContains(r, "Please wait a few minutes")


class EditableTextsTests(SeededTestCase):
    def test_announcement_bar_shows_only_when_filled_in(self):
        self.assertNotIn('class="announce"', self.client.get("/").content.decode())
        SiteSettings.objects.filter(pk=1).update(
            announcement="Admissions open", announcement_label="Apply now", announcement_url="/contact/"
        )
        html = self.client.get("/about/").content.decode()
        self.assertIn('class="announce"', html)
        self.assertIn("Admissions open", html)
        self.assertIn('href="/contact/">Apply now', html)

    def test_404_page_uses_the_admin_texts(self):
        SiteSettings.objects.filter(pk=1).update(
            notfound_title="Lost in Space", notfound_highlight="Space", notfound_text="Try the menu above."
        )
        r = self.client.get("/no-such-page/")
        self.assertContains(r, 'Lost in <span class="accent">Space</span>', status_code=404)
        self.assertContains(r, "Try the menu above.", status_code=404)

    def test_google_analytics_loads_only_with_an_id_and_the_csp_follows(self):
        r = self.client.get("/")
        self.assertNotIn("analytics.js", r.content.decode())
        self.assertNotIn("googletagmanager", r["Content-Security-Policy"])
        SiteSettings.objects.filter(pk=1).update(ga_id="G-AB12CD34EF")
        r = self.client.get("/")
        self.assertIn('data-ga="G-AB12CD34EF"', r.content.decode())
        self.assertIn("googletagmanager", r["Content-Security-Policy"])


class PhotoTests(SeededTestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)

    def test_uploaded_photos_get_webp_copies(self):
        Image.new("RGB", (1000, 600), "purple").save(Path(self.media) / "photo.jpg")
        with override_settings(MEDIA_ROOT=self.media):
            value = images.srcset("/media/photo.jpg")
            self.assertIn("/media/_v/photo-480.webp 480w", value)
            self.assertIn("/media/_v/photo-1000.webp 1000w", value)
            self.assertTrue((Path(self.media) / "_v" / "photo-800.webp").exists())
            self.assertEqual(images.srcset("https://example.com/photo.jpg"), "")
            self.assertEqual(images.srcset("/media/../manage.py.jpg"), "")  # never outside MEDIA_ROOT

    def test_svg_icons_with_scripts_are_refused(self):
        bad = SimpleUploadedFile("icon.svg", b'<svg onload="alert(1)"><circle r="4"/></svg>')
        with self.assertRaises(ValidationError):
            safe_svg(bad)
        safe_svg(SimpleUploadedFile("icon.svg", b'<svg viewBox="0 0 8 8"><circle r="4"/></svg>'))

    def test_admin_shows_best_photo_sizes(self):
        html = self.admin_client().get("/admin/site-settings/", follow=True).content.decode()
        self.assertIn('class="ap-size"', html)
        self.assertIn("512 × 512 px", html)
        self.assertIn("1200 × 630 px", html)
        html = self.admin_client().get(f"/admin/blogs/{BlogPost.objects.first().pk}/change/").content.decode()
        self.assertIn("1920 × 1080 px", html)
