"""Colour schemes: three brand colours drive every colour on the site; the admin refuses unreadable colours."""

from django.db.models.fields.files import FieldFile

from core import theme
from core.adminpanel.forms import SiteSettingsForm
from core.models import SiteSettings

from .base import SeededTestCase


class ThemeEngineTests(SeededTestCase):
    def test_presets_are_readable(self):
        for _key, name, primary, accent, dark in theme.PRESETS:
            self.assertEqual(theme.check_contrast(primary, accent, dark), [], name)

    def test_anchor_shades_become_the_chosen_colours(self):
        scheme = {"primary": "#047857", "accent": "#fb923c", "dark": "#102a2c"}
        self.assertEqual(theme.recolor(theme.DEFAULT["primary"], scheme), "#047857")
        self.assertEqual(theme.recolor(theme.DEFAULT["accent"], scheme), "#fb923c")
        self.assertEqual(theme.recolor(theme.DEFAULT["dark"], scheme), "#102a2c")

    def test_light_stays_light_and_status_colours_stay(self):
        scheme = {"primary": "#b91c1c", "accent": "#d4af37", "dark": "#2a1015"}
        L_before = theme.to_oklch("#f7f8fe")[0]
        L_after = theme.to_oklch(theme.recolor("#f7f8fe", scheme))[0]
        self.assertAlmostEqual(L_before, L_after, places=2)
        self.assertEqual(theme.recolor("#dc2626", scheme), "#dc2626")  # error red
        self.assertEqual(theme.recolor("#ffffff", scheme), "#ffffff")


class ThemeOnSiteTests(SeededTestCase):
    def set_scheme(self, key, **colours):
        s = SiteSettings.load()
        s.color_scheme = key
        for k, v in colours.items():
            setattr(s, f"color_{k}", v)
        s.save()

    def test_default_scheme_adds_nothing(self):
        html = self.client.get("/").content.decode()
        self.assertNotIn('id="colour-scheme"', html)
        self.assertNotIn("data-theme-map", html)

    def test_preset_recolours_css_scripts_and_drawings(self):
        self.set_scheme("ocean")
        html = self.client.get("/").content.decode()
        self.assertIn("--p-violet-700:#1d4ed8", html)
        self.assertIn("data-theme-map=", html)
        self.assertNotIn('stroke="#a9b3ee"', html)  # motif lavender recoloured
        self.assertIn("--p-err-600", theme.palette())  # status colours exist ...
        overrides = html.split('id="colour-scheme">')[1].split("</style>")[0]
        self.assertNotIn("--p-err-600:", overrides)  # ... but stay
        self.assertNotIn("--p-wordmark", overrides)  # the logo never changes colour

    def test_preview_is_for_staff_only(self):
        self.assertNotIn("Colour preview", self.client.get("/?scheme=emerald").content.decode())
        html = (
            self.admin_client()
            .get("/?scheme=custom&primary=%23047857&accent=%23d4af37&dark=%230f2a24")
            .content.decode()
        )
        self.assertIn("Colour preview", html)
        self.assertIn("--p-violet-700:#047857", html)
        self.assertNotIn(
            "--p-violet-700", self.client.get("/").content.decode().split("</head>")[0].split("wise-teck.css")[1]
        )


class ThemeAdminTests(SeededTestCase):
    def form(self, **changes):
        s = SiteSettings.load()
        data = {f.html_name: f.value() for f in SiteSettingsForm(instance=s) if f.value() not in (None, False)}
        data = {k: v for k, v in data.items() if not isinstance(v, FieldFile)}
        data.update(changes)
        return SiteSettingsForm(data=data, instance=s)

    def test_unreadable_custom_colours_are_refused(self):
        f = self.form(color_scheme="custom", color_primary="#facc15", color_accent="#d4af37", color_dark="#0d2158")
        self.assertFalse(f.is_valid())
        self.assertIn("darker primary", " ".join(f.errors["color_scheme"]))

    def test_readable_custom_colours_are_saved(self):
        f = self.form(color_scheme="custom", color_primary="#047857", color_accent="#d4af37", color_dark="#0f2a24")
        self.assertTrue(f.is_valid(), f.errors)

    def test_picker_on_the_settings_page(self):
        html = self.admin_client().get("/admin/site-settings/", follow=True).content.decode()
        self.assertIn("data-scheme-picker", html)
        self.assertIn("Ocean Blue", html)
        self.assertIn('type="color"', html)
