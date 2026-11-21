"""Fixes from the site audit: security headers, pagination, social links, page weight, accessibility."""
from django.core.cache import cache
from django.utils import timezone

from core.models import BlogPost, Section, SiteSettings

from .base import SeededTestCase


class SecurityHeadersTests(SeededTestCase):
    def test_headers_on_site_and_admin(self):
        for url in ("/", "/about/", "/admin/login/"):
            r = self.client.get(url)
            csp = r.headers.get("Content-Security-Policy", "")
            self.assertIn("default-src 'self'", csp, url)
            self.assertIn("script-src 'self'", csp, url)
            self.assertNotIn("unsafe-inline", csp.split("script-src")[1].split(";")[0], url)
            self.assertIn("camera=()", r.headers.get("Permissions-Policy", ""), url)
            self.assertEqual(r.headers.get("X-Frame-Options"), "DENY", url)

    def test_no_inline_event_handlers_in_admin(self):
        page_section = Section.objects.filter(page__slug="about").first()
        for url in ("/admin/sections/", f"/admin/pages/{page_section.page_id}/change/", "/admin/site-settings/1/change/"):
            r = self.admin_client().get(url)
            self.assertEqual(r.status_code, 200, url)
            html = r.content.decode()
            for handler in (" onclick=", " onsubmit=", " onchange="):
                self.assertNotIn(handler, html, url)

    def test_django_builtin_admin_is_gone(self):
        self.assertEqual(self.client.get("/django-admin/").status_code, 404)
        self.assertNotIn("django-admin", self.client.get("/robots.txt").content.decode())


class PageWeightTests(SeededTestCase):
    def test_wave_drawing_is_not_inlined(self):
        html = self.client.get("/").content.decode()
        self.assertNotIn('id="wv-hero"', html)            # the 200 KB fallback drawing is gone
        self.assertIn('data-wave="wv-hero"', html)        # wt-waves.js draws into these
        self.assertLess(len(html), 120_000)

    def test_three_js_is_loaded_later(self):
        html = self.client.get("/").content.decode()
        self.assertNotIn('<script src="/static/js/vendor/three.min.js', html)
        self.assertIn('data-three="/static/js/vendor/three.min.js', html)

    def test_images_below_the_first_screen_are_lazy(self):
        html = self.client.get("/").content.decode()
        self.assertGreaterEqual(html.count('loading="lazy"'), 5)


class SocialLinkTests(SeededTestCase):
    def test_placeholder_links_are_hidden(self):
        s = SiteSettings.load()
        s.facebook, s.instagram, s.linkedin, s.youtube = "#", "", "#", "https://youtube.com/@wiseteck"
        s.save()
        html = self.client.get("/").content.decode()
        self.assertNotIn('aria-label="Facebook"', html)
        self.assertNotIn('href="#" aria-label', html)
        self.assertIn('href="https://youtube.com/@wiseteck" aria-label="YouTube" target="_blank" rel="noopener"', html)


class AccessibilityTests(SeededTestCase):
    def test_duplicate_photo_links_hidden_from_screen_readers(self):
        import re
        post = BlogPost.objects.live().first()
        for url in ("/blog/", post.get_absolute_url()):
            tags = re.findall(r'<a class="ph"[^>]*>', self.client.get(url).content.decode())
            self.assertTrue(tags, url)
            for tag in tags:
                self.assertIn('tabindex="-1" aria-hidden="true"', tag, url)


class PaginationTests(SeededTestCase):
    def setUp(self):
        cache.clear()
        now = timezone.now()
        for n in range(12):
            BlogPost.objects.create(title=f"Extra post {n}", short_description="x" * 50, is_active=True,
                                    published_at=now - timezone.timedelta(days=30 + n))
        self.total = BlogPost.objects.live().count()

    def test_blog_pages(self):
        r1 = self.client.get("/blog/")
        html1 = r1.content.decode()
        self.assertEqual(html1.count('class="blockc'), 9)
        self.assertIn('<nav class="pager"', html1)
        self.assertIn('<link rel="next" href="http://testserver/blog/?page=2"/>', html1)
        self.assertIn('<link rel="canonical" href="http://testserver/blog/"/>', html1)

        html2 = self.client.get("/blog/?page=2").content.decode()
        self.assertEqual(html2.count('class="blockc'), self.total - 9)
        self.assertIn('<link rel="canonical" href="http://testserver/blog/?page=2"/>', html2)
        self.assertIn('<link rel="prev" href="http://testserver/blog/"/>', html2)
        self.assertIn("Page 2", html2.split("<title>")[1].split("</title>")[0])

    def test_page_one_and_bad_pages(self):
        r = self.client.get("/blog/?page=1")
        self.assertEqual((r.status_code, r["Location"]), (301, "/blog/"))
        self.assertEqual(self.client.get("/blog/?page=99").status_code, 404)
        self.assertEqual(self.client.get("/blog/?page=abc").status_code, 404)

    def test_per_page_setting(self):
        Section.objects.filter(layout="blog_list").update(feed_limit=4)
        html = self.client.get("/blog/").content.decode()
        self.assertEqual(html.count('class="blockc'), 4)
        self.assertIn('aria-label="Page 4"', html)

    def test_short_lists_have_no_page_numbers(self):
        BlogPost.objects.filter(title__startswith="Extra post").delete()
        self.assertNotIn('<nav class="pager"', self.client.get("/blog/").content.decode())


class MetaDescriptionTests(SeededTestCase):
    def test_long_descriptions_are_clipped_for_search_results(self):
        post = BlogPost.objects.live().first()
        post.short_description = "word " * 60
        post.save()
        html = self.client.get(post.get_absolute_url()).content.decode()
        desc = html.split('<meta name="description" content="')[1].split('"')[0]
        self.assertLessEqual(len(desc), 160)
        self.assertTrue(desc.endswith("…"))


class ProductionSettingsTests(SeededTestCase):
    def test_hsts_in_production(self):
        from django.conf import settings
        text = (settings.BASE_DIR / "config" / "settings.py").read_text(encoding="utf8")
        self.assertIn("SECURE_HSTS_SECONDS = 31536000", text.split("if not DEBUG:")[1])
