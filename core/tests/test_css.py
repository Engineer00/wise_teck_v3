"""Universal CSS: one stylesheet, every design value from a token, two breakpoints, no inline styles."""

import re
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]
CSS = ROOT / "static" / "css" / "wise-teck.css"


def _css():
    return re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)


def _outside_root(css):
    """The stylesheet with its :root token blocks blanked out."""
    out = css
    for m in re.finditer(r":root\s*\{[^}]*\}", css):
        out = out.replace(m.group(0), " " * len(m.group(0)), 1)
    return out


def _declarations(css):
    for m in re.finditer(r"([a-z-]+)\s*:\s*([^;{}]+)", css):
        if not m.group(1).startswith("--"):
            yield m.group(1), re.sub(r"url\([^)]*\)", "", m.group(2))


class UniversalCssTest(SimpleTestCase):
    def test_tokens_live_only_in_root(self):
        css = _css()
        roots = re.findall(r":root\s*\{", css)
        self.assertLessEqual(len(roots), 3)
        for m in re.finditer(r":root\s*\{", css):
            before = css[: m.start()]
            depth = before.count("{") - before.count("}")
            # allowed: top level, or directly inside an @media block (responsive token values) - never inside a layer
            opener = before[: before.rfind("{")].rsplit("}", 1)[-1].strip() if depth else ""
            self.assertTrue(
                depth == 0 or (depth == 1 and opener.startswith("@media")),
                "a :root token block is nested inside a layer",
            )

    def test_no_hard_coded_design_values(self):
        problems = []
        for prop, value in _declarations(_outside_root(_css())):
            v = re.sub(r"var\([^)]*\)", "", value)
            if re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(\s*\d|\bhsla?\(|(?<![\w-])(white|black)(?![\w-])", v):
                problems.append(f"colour  {prop}: {value[:60]}")
            if "radius" in prop and re.search(r"\d+(\.\d+)?px", v):
                problems.append(f"radius  {prop}: {value[:60]}")
            if prop == "font-size" and re.search(r"\d", v):
                problems.append(f"font    {prop}: {value[:60]}")
            if prop == "z-index" and re.search(r"\d", v):
                problems.append(f"z-index {prop}: {value[:60]}")
        self.assertEqual(problems, [], "use a token from the :root block instead")

    def test_only_the_standard_breakpoints(self):
        queries = {re.sub(r"\s+", "", q) for q in re.findall(r"@media\s*([^{]+)\{", _css())}
        allowed = {
            "(max-width:1023px)",
            "(min-width:1024px)",
            "(max-width:639px)",
            "(min-width:640px)",
            "(max-width:1199px)",  # menu breakpoint: the full menu needs ~1100px of header width
            "(prefers-reduced-motion:reduce)",
        }
        self.assertEqual(queries - allowed, set())

    def test_templates_have_no_inline_styles(self):
        found = []
        for f in (ROOT / "templates").rglob("*.html"):
            if "adminpanel" in f.parts:
                continue
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                for m in re.finditer(r'style="([^"]*)"', line):
                    value = re.sub(r"\{\{.*?\}\}", "1", m.group(1))
                    if not re.fullmatch(r"(\s*--[\w-]+:[^;]+;?)+\s*", value) and value != "position:absolute":
                        found.append(f'{f.relative_to(ROOT)}:{n} style="{m.group(1)}"')
        self.assertEqual(found, [], "styles belong in wise-teck.css (passing a --custom-property is fine)")

    def test_mobile_menu_breakpoint_matches_css(self):
        js = (ROOT / "static" / "js" / "wt.js").read_text(encoding="utf-8")
        self.assertIn("(max-width: 1199px)", js)
        self.assertIn("@media (max-width:1199px){.burger{display:grid}}", _css())
