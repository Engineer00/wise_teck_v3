"""SEO: meta tags, structured data, sitemap, robots, redirects, slugs, image optimisation."""
import io
import json
import os
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from core.models import BlogPost, Page, Redirect, SiteSettings

from .base import SeededTestCase


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.ld, self.h1, self.title = {}, {}, [], 0, ""
        self._ld = self._t = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            self.meta[a.get("name") or a.get("property")] = a.get("content")
        elif tag == "link":
            self.links[a.get("rel")] = a.get("href")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._ld = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self._t = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self._ld = self._ld and tag != "script"
        self._t = self._t and tag != "title"

    def handle_data(self, d):
        if self._ld:
            self.ld.append(d)
        if self._t:
            self.title += d


def head(url, client=None):
    h = Head()
    h.feed((client or Client()).get(url).content.decode())
    return h


class MetaTagsTest(SeededTestCase):
    def test_every_live_page(self):
        titles, descriptions = set(), set()
        for p in Page.objects.live().filter(is_active=True):
            url = p.get_absolute_url()
            with self.subTest(page=url):
                h = head(url)
                self.assertTrue(h.title.strip())
                self.assertTrue(h.meta.get("description"))
                self.assertEqual(h.links.get("canonical"), "http://testserver" + url)
                self.assertNotIn("noindex", h.meta.get("robots", ""))
                for k in ("og:title", "og:description", "og:image", "og:url", "og:type", "twitter:card"):
                    self.assertTrue(h.meta.get(k), k)
                self.assertTrue(h.meta["og:image"].startswith("http"))
                self.assertEqual(h.h1, 1, "exactly one h1")
                types = [g["@type"] for g in json.loads("".join(h.ld))["@graph"]]
                if p.slug == "home":
                    self.assertTrue({"EducationalOrganization", "WebSite"} <= set(types))
                else:
                    self.assertIn("BreadcrumbList", types)
                titles.add(h.title)
                descriptions.add(h.meta["description"])
        n = Page.objects.live().filter(is_active=True).count()
        self.assertEqual(len(titles), n, "titles are unique")
        self.assertEqual(len(descriptions), n, "descriptions are unique")

    def test_blog_post_is_an_article(self):
        post = BlogPost.objects.live().first()
        h = head(post.get_absolute_url())
        types = [g["@type"] for g in json.loads("".join(h.ld))["@graph"]]
        self.assertIn("BlogPosting", types)
        self.assertEqual(h.meta.get("og:type"), "article")

    def test_noindex_switch_and_sharing_overrides(self):
        Page.objects.filter(slug="about").update(noindex=True, share_title="Share X", share_description="Desc Y")
        h = head("/about/")
        self.assertIn("noindex", h.meta["robots"])
        self.assertEqual(h.meta["og:title"], "Share X")
        self.assertEqual(h.meta["twitter:description"], "Desc Y")
        from django.core.cache import cache
        cache.clear()                     # the sitemap is cached for 15 minutes
        self.assertNotIn("/about/</loc>", Client().get("/sitemap.xml").content.decode())

    def test_main_address_setting_drives_canonical_and_robots(self):
        SiteSettings.objects.filter(pk=1).update(site_url="https://wise-teck.dev/")
        self.assertEqual(head("/about/").links["canonical"], "https://wise-teck.dev/about/")
        self.assertIn("Sitemap: https://wise-teck.dev/sitemap.xml", Client().get("/robots.txt").content.decode())


class CrawlFilesTest(SeededTestCase):
    def test_robots(self):
        body = Client().get("/robots.txt").content.decode()
        for line in ("Disallow: /admin/", "Disallow: /preview/", "Sitemap: http://testserver/sitemap.xml"):
            self.assertIn(line, body)

    def test_sitemap(self):
        r = Client().get("/sitemap.xml")
        self.assertTrue(r["Content-Type"].startswith("application/xml"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        locs = [u.find(ns + "loc").text for u in ET.fromstring(r.content)]
        expected = Page.objects.live().filter(is_active=True).count() + BlogPost.objects.live().count()
        self.assertEqual(len(locs), expected)
        self.assertFalse(any("draft" in u or "preview" in u for u in locs))


class RedirectsTest(SeededTestCase):
    def test_old_addresses(self):
        for old, new in (("/about.html", "/about/"), ("/index.html", "/"), ("/explore-ecosystem/", "/about/#ecosystem")):
            with self.subTest(old=old):
                r = Client().get(old)
                self.assertEqual((r.status_code, r["Location"]), (301, new))

    def test_changed_address_redirects_without_chains(self):
        p = Page.objects.get(slug="placement")
        p.slug = "careers"
        p.save()
        self.assertEqual(Client().get("/placement/")["Location"], "/careers/")
        p.slug = "jobs"
        p.save()
        self.assertEqual(Client().get("/placement/")["Location"], "/jobs/")
        self.assertEqual(Client().get("/careers/")["Location"], "/jobs/")
        p.slug = "placement"
        p.save()
        self.assertEqual(Client().get("/placement/").status_code, 200)
        self.assertFalse(Redirect.objects.filter(old_path="/placement/").exists())


class ImageOptimisationTest(SeededTestCase):
    def test_large_upload_is_resized_and_compressed(self):
        from PIL import Image
        big = io.BytesIO()
        Image.new("RGB", (4000, 3000), (120, 80, 200)).save(big, "JPEG", quality=98)
        s = SiteSettings.load()
        s.share_image = SimpleUploadedFile("huge.jpg", big.getvalue(), content_type="image/jpeg")
        s.save()
        try:
            with Image.open(s.share_image.path) as im:
                self.assertLessEqual(max(im.size), 2000)
            self.assertLess(os.path.getsize(s.share_image.path), len(big.getvalue()))
        finally:
            os.remove(s.share_image.path)
