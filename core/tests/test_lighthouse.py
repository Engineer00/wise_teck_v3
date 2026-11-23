"""Daily Lighthouse results: the endpoint the GitHub workflow posts to, and the dashboard panel."""

import json

from django.test import Client, override_settings

from core import lighthouse
from core.models import LighthouseRun

from .base import SeededTestCase

TOKEN = "test-token-0123456789"


def result(url="/", mode="mobile", perf=91, seo=100, lcp=1800.0, issues=None):
    return {
        "url": url,
        "mode": mode,
        "scores": {"performance": perf, "accessibility": 100, "best_practices": 100, "seo": seo},
        "metrics": {"fcp": 900.0, "lcp": lcp, "tbt": 120.0, "si": 2000.0, "cls": 0.01},
        "issues": issues or [],
    }


def payload(*results, ran_at="2026-11-23T00:30:00Z"):
    return {
        "ran_at": ran_at,
        "version": "13.6.0",
        "report_url": "https://github.com/Engineer00/wise_teck_v3/actions/runs/1",
        "results": list(results) or [result()],
    }


def post(data, token=TOKEN):
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
    return Client().post("/api/lighthouse/", json.dumps(data), content_type="application/json", **headers)


@override_settings(LIGHTHOUSE_TOKEN=TOKEN)
class LighthouseEndpointTest(SeededTestCase):
    def test_saves_a_run(self):
        r = post(payload(result(), result(mode="desktop")))
        self.assertEqual(r.status_code, 201)
        run = LighthouseRun.objects.get()
        self.assertEqual((run.version, len(run.results)), ("13.6.0", 2))
        self.assertEqual(run.results[0]["scores"]["performance"], 91)

    def test_wrong_or_missing_token_is_refused(self):
        self.assertEqual(post(payload(), token="nope").status_code, 403)
        self.assertEqual(post(payload(), token="").status_code, 403)
        self.assertFalse(LighthouseRun.objects.exists())

    def test_only_post(self):
        self.assertEqual(Client().get("/api/lighthouse/").status_code, 405)

    def test_bad_bodies_are_refused(self):
        self.assertEqual(post({"results": []}).status_code, 400)
        r = Client().post(
            "/api/lighthouse/", "not json", content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {TOKEN}"
        )
        self.assertEqual(r.status_code, 400)

    def test_values_are_cleaned(self):
        dirty = result(perf=250, issues=[{"id": "x", "title": "t" * 500, "value": True}] * 30)
        dirty["mode"] = "mobile"
        bad_rows = [{"url": "https://evil.example/", "mode": "mobile"}, {"url": "/", "mode": "tablet"}, "junk"]
        data = payload(dirty, *bad_rows)
        data["report_url"] = "javascript:alert(1)"
        self.assertEqual(post(data).status_code, 201)
        run = LighthouseRun.objects.get()
        self.assertEqual(len(run.results), 1)  # the three bad rows are dropped
        row = run.results[0]
        self.assertEqual(row["scores"]["performance"], 100)  # clamped to 0-100
        self.assertEqual(len(row["issues"]), lighthouse.MAX_ISSUES)
        self.assertEqual(len(row["issues"][0]["title"]), 200)
        self.assertEqual(row["issues"][0]["value"], "")
        self.assertEqual(run.report_url, "")

    def test_keeps_only_the_newest_runs(self):
        for day in range(1, 6):
            lighthouse.save(payload(ran_at=f"2026-11-{day:02d}T00:30:00Z"))
        old_keep, lighthouse.KEEP = lighthouse.KEEP, 3
        try:
            lighthouse.save(payload(ran_at="2026-11-06T00:30:00Z"))
        finally:
            lighthouse.KEEP = old_keep
        self.assertEqual(LighthouseRun.objects.count(), 3)
        self.assertEqual(LighthouseRun.objects.first().ran_at.day, 6)


class LighthouseOffTest(SeededTestCase):
    def test_endpoint_does_not_exist_without_a_token(self):
        with self.settings(LIGHTHOUSE_TOKEN=""):
            self.assertEqual(post(payload()).status_code, 404)

    def test_robots_keeps_crawlers_out(self):
        self.assertIn("Disallow: /api/", Client().get("/robots.txt").content.decode())


@override_settings(LIGHTHOUSE_TOKEN=TOKEN)
class LighthouseDashboardTest(SeededTestCase):
    def test_panel_explains_setup_when_empty(self):
        with self.settings(LIGHTHOUSE_TOKEN=""):
            html = self.admin_client().get("/admin/").content.decode()
        self.assertIn("Speed &amp; quality · Google Lighthouse", html)
        self.assertIn("LIGHTHOUSE_TOKEN", html)

    def test_panel_shows_scores_changes_vitals_and_issues(self):
        lighthouse.save(payload(result(perf=80), result(mode="desktop", perf=95), ran_at="2026-11-22T00:30:00Z"))
        issue = {"id": "link-text", "title": "Links do not have descriptive text", "value": "4 links found"}
        lighthouse.save(
            payload(
                result(perf=92, lcp=3100.0, issues=[issue]),
                result(mode="desktop", perf=97),
                result(url="/about/", issues=[issue]),
            )
        )
        info = lighthouse.summary()
        phone = info["modes"][0]["cards"][0]
        self.assertEqual((phone["value"], phone["change"], phone["rating"]), (92, 12, "good"))  # (92 + 91) / 2
        self.assertEqual(info["vitals"][0]["text"], "3.1 s")
        self.assertEqual(info["vitals"][0]["rating"], "fair")
        self.assertEqual(info["issues"][0]["pages"], 2)
        html = self.admin_client().get("/admin/").content.decode()
        for text in ("Links do not have descriptive text", "3.1 s", "/about/", "Full reports for every page"):
            self.assertIn(text, html)


class SearchFindingsTest(SeededTestCase):
    """What Lighthouse flagged on 23 Nov 2026: vague "Read More" links, a skipped heading level, no /llms.txt."""

    def test_read_more_links_name_their_target(self):
        from django.core.cache import cache

        cache.clear()
        html = Client().get("/").content.decode()
        self.assertIn('Read More<span class="vh">: About Wise-Teck</span>', html)
        self.assertNotRegex(html, r">Read More <i")
        self.assertIn('<span class="vh">: ', Client().get("/blog/").content.decode())

    def test_vague_filter(self):
        from core.templatetags.wt import vague

        self.assertTrue(vague(" Read More "))
        self.assertFalse(vague("Explore Programs"))
        self.assertFalse(vague(None))

    def test_contact_form_title_is_an_h2(self):
        html = Client().get("/contact/").content.decode()
        self.assertRegex(html, r'<form class="glass form[^>]*>[\s\S]*?<h2>')
        self.assertNotIn("<h3>Send", html)

    def test_llms_txt_lists_live_pages(self):
        from django.core.cache import cache

        cache.clear()
        r = Client().get("/llms.txt")
        self.assertEqual(r["Content-Type"], "text/plain; charset=utf-8")
        text = r.content.decode()
        self.assertTrue(text.startswith("# "))
        self.assertIn("## Pages", text)
        self.assertIn("/about/)", text)
